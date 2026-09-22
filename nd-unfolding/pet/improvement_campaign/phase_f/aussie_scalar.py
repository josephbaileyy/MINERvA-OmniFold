import argparse
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import sys
# Insert phase_b/scalar into path to import its modules
HERE = Path(__file__).resolve().parent
PHASE_B_SCALAR = HERE.parent / "phase_b" / "scalar"
if str(PHASE_B_SCALAR) not in sys.path:
    sys.path.insert(0, str(PHASE_B_SCALAR))

import binned_unfolding as bu
import features
import run_ibu
import scalar_common as scm
import scalar_omnifold as so

LOGIT_CAP = 30.0

class MLP(nn.Module):
    def __init__(self, in_features, hidden=(64, 64)):
        super().__init__()
        layers = []
        in_dim = in_features
        for h in hidden:
            layers.append(nn.Linear(in_dim, h))
            layers.append(nn.ReLU())
            in_dim = h
        layers.append(nn.Linear(in_dim, 1))
        self.net = nn.Sequential(*layers)
        
    def forward(self, x):
        return self.net(x).squeeze(-1)

def _weighted_logloss_bce(logits, y, w):
    loss = F.binary_cross_entropy_with_logits(logits, y, reduction="none")
    return (loss * w).sum() / w.sum()

def train_classifier(X_sim, X_dat, w_sim, w_dat, epochs=50, batch_size=1024, lr=1e-3, seed=0):
    torch.manual_seed(seed)
    # We will standardize inputs
    mean = np.mean(X_sim, axis=0)
    std = np.std(X_sim, axis=0)
    std[std == 0] = 1.0
    
    # We use slog1p transform for heavy tails like B1 does
    def transform(x):
        return np.sign(x) * np.log1p(np.abs(x))
    
    X_sim_t = transform(X_sim)
    X_dat_t = transform(X_dat)
    
    mean = np.mean(X_sim_t, axis=0)
    std = np.std(X_sim_t, axis=0)
    std[std == 0] = 1.0
    
    X_sim_z = (X_sim_t - mean) / std
    X_dat_z = (X_dat_t - mean) / std
    
    model = MLP(X_sim.shape[1])
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    X = np.concatenate([X_sim_z, X_dat_z])
    y = np.concatenate([np.zeros(len(X_sim_z)), np.ones(len(X_dat_z))])
    w = np.concatenate([w_sim, w_dat])
    
    idx = np.random.RandomState(seed).permutation(len(X))
    n_tr = int(0.8 * len(X))
    tr, va = idx[:n_tr], idx[n_tr:]
    
    X_tr, y_tr, w_tr = torch.tensor(X[tr], dtype=torch.float32), torch.tensor(y[tr], dtype=torch.float32), torch.tensor(w[tr], dtype=torch.float32)
    X_va, y_va, w_va = torch.tensor(X[va], dtype=torch.float32), torch.tensor(y[va], dtype=torch.float32), torch.tensor(w[va], dtype=torch.float32)
    
    best_loss = float('inf')
    best_state = None
    patience = 4
    stale = 0
    
    for epoch in range(epochs):
        model.train()
        perm = torch.randperm(len(X_tr))
        for i in range(0, len(X_tr), batch_size):
            b = perm[i:i+batch_size]
            logits = model(X_tr[b])
            loss = _weighted_logloss_bce(logits, y_tr[b], w_tr[b])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        model.eval()
        with torch.no_grad():
            val_loss = _weighted_logloss_bce(model(X_va), y_va, w_va).item()
            
        if val_loss < best_loss - 1e-7:
            best_loss = val_loss
            stale = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            stale += 1
            if stale >= patience:
                break
                
    if best_state is not None:
        model.load_state_dict(best_state)
        
    return model, mean, std

def train_unfolder(classifier, cls_mean, cls_std, Z_sim_pass, X_sim_pass, w_sim_pass, Z_sim_miss, w_sim_miss, epochs=50, batch_size=2048, lr=1e-3, seed=0):
    torch.manual_seed(seed+1)
    
    def transform(x):
        return np.sign(x) * np.log1p(np.abs(x))
        
    Z_sim_pass_t = transform(Z_sim_pass)
    Z_sim_miss_t = transform(Z_sim_miss) if len(Z_sim_miss) > 0 else Z_sim_miss
    
    z_mean = np.mean(Z_sim_pass_t, axis=0)
    z_std = np.std(Z_sim_pass_t, axis=0)
    z_std[z_std == 0] = 1.0
    
    Z_sim_pass_z = (Z_sim_pass_t - z_mean) / z_std
    if len(Z_sim_miss) > 0:
        Z_sim_miss_z = (Z_sim_miss_t - z_mean) / z_std
        
    X_sim_pass_t = transform(X_sim_pass)
    X_sim_pass_z = (X_sim_pass_t - cls_mean) / cls_std
    
    unfolder = MLP(Z_sim_pass.shape[1])
    optimizer = optim.Adam(unfolder.parameters(), lr=lr)
    
    n_pass = len(Z_sim_pass)
    n_miss = len(Z_sim_miss)
    
    for p in classifier.parameters():
        p.requires_grad = True
        
    # Validation split for unfolder
    idx_pass = np.random.RandomState(seed).permutation(n_pass)
    n_tr_pass = int(0.8 * n_pass)
    tr_pass, va_pass = idx_pass[:n_tr_pass], idx_pass[n_tr_pass:]
    
    Z_tr_pass, X_tr_pass, w_tr_pass = Z_sim_pass_z[tr_pass], X_sim_pass_z[tr_pass], w_sim_pass[tr_pass]
    Z_va_pass, X_va_pass, w_va_pass = Z_sim_pass_z[va_pass], X_sim_pass_z[va_pass], w_sim_pass[va_pass]
    
    if n_miss > 0:
        idx_miss = np.random.RandomState(seed).permutation(n_miss)
        n_tr_miss = int(0.8 * n_miss)
        tr_miss, va_miss = idx_miss[:n_tr_miss], idx_miss[n_tr_miss:]
        Z_tr_miss, w_tr_miss = Z_sim_miss_z[tr_miss], w_sim_miss[tr_miss]
        Z_va_miss, w_va_miss = Z_sim_miss_z[va_miss], w_sim_miss[va_miss]
        
    best_loss = float('inf')
    best_state = None
    stale = 0
    patience = 5
    
    for epoch in range(epochs):
        unfolder.train()
        classifier.eval()
        
        perm = torch.randperm(len(Z_tr_pass))
        perm_miss = torch.randperm(len(Z_tr_miss)) if n_miss > 0 else None
        
        for i in range(0, len(Z_tr_pass), batch_size):
            b = perm[i:i+batch_size]
            Z_b = torch.tensor(Z_tr_pass[b], dtype=torch.float32, requires_grad=True)
            X_b = torch.tensor(X_tr_pass[b], dtype=torch.float32, requires_grad=True)
            w_b = torch.tensor(w_tr_pass[b], dtype=torch.float32)
            
            lw_z = unfolder(Z_b)
            
            with torch.enable_grad():
                lw_x = classifier(X_b)
                # mlc loss
                loss_reg = (-lw_z.exp() * lw_x - (1 - lw_x.exp())) / 2
                loss_reg = (loss_reg * w_b).mean()
                
                grads_x = torch.autograd.grad(
                    loss_reg,
                    classifier.parameters(),
                    create_graph=True,
                    allow_unused=True
                )
                
                loss_gradnorm = sum(g.abs().sum() for g in grads_x if g is not None)
                loss_gradnorm = loss_gradnorm * 1e3
                
            loss = loss_gradnorm
            
            if n_miss > 0:
                b_m = perm_miss[i % len(Z_tr_miss) : (i % len(Z_tr_miss))+batch_size]
                if len(b_m) == 0:
                     b_m = perm_miss[:batch_size]
                Z_m = torch.tensor(Z_tr_miss[b_m], dtype=torch.float32)
                w_m = torch.tensor(w_tr_miss[b_m], dtype=torch.float32)
                lw_z_m = unfolder(Z_m)
                # target is R(z) = 1, so log R(z) = 0
                loss_miss = ((lw_z_m ** 2) * w_m).mean()
                loss = loss + loss_miss
                
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        # Validation
        unfolder.eval()
        with torch.no_grad():
            Z_va_b = torch.tensor(Z_va_pass, dtype=torch.float32)
            X_va_b = torch.tensor(X_va_pass, dtype=torch.float32)
            w_va_b = torch.tensor(w_va_pass, dtype=torch.float32)
            lw_z_va = unfolder(Z_va_b)
            lw_x_va = classifier(X_va_b)
            
            # Since we can't easily autograd on validation without create_graph (which is expensive),
            # we just use the raw MLC regression loss as validation metric.
            # mlc loss:
            val_loss = ((-lw_z_va.exp() * lw_x_va - (1 - lw_x_va.exp())) / 2 * w_va_b).mean()
            
            if n_miss > 0:
                Z_va_m = torch.tensor(Z_va_miss, dtype=torch.float32)
                w_va_m = torch.tensor(w_va_miss, dtype=torch.float32)
                val_loss += ((unfolder(Z_va_m) ** 2) * w_va_m).mean()
                
            val_loss = val_loss.item()
            
        if val_loss < best_loss - 1e-7:
            best_loss = val_loss
            stale = 0
            best_state = {k: v.cpu().clone() for k, v in unfolder.state_dict().items()}
        else:
            stale += 1
            if stale >= patience:
                break
                
    if best_state is not None:
        unfolder.load_state_dict(best_state)
        
    return unfolder, z_mean, z_std

def _capped_ratio(logit: np.ndarray) -> np.ndarray:
    logit = np.asarray(logit, dtype=np.float64)
    return np.exp(np.clip(logit, -LOGIT_CAP, LOGIT_CAP))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--populations", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    
    pop = scm.load_populations(args.populations)
    endpoint = scm.endpoint_from_populations(pop)
    bins = run_ibu.build_bins(pop)
    pga = pop["a_pass_truth"].astype(bool)
    s1a = pga & pop["a_pass_reco"].astype(bool)
    pgb = pop["b_pass_truth"].astype(bool)
    s1b = pgb & pop["b_pass_reco"].astype(bool)
    w_data = (pop["a_w_reco"] * pop["a_tilt"])[s1a]
    
    inputs = "muon_eavail"
    
    X_reco_mc, fill_mc = features.reco_matrix(pop, "b", inputs, used=s1b)
    X_reco_mc_pass = X_reco_mc[s1b]
    X_reco_data, fill_data = features.reco_matrix(pop, "a", inputs, used=s1a)
    X_reco_data = X_reco_data[s1a]
    X_gen_mc, fill_gen = features.truth_matrix(pop, "b", "truth4", used=pgb)
    X_gen_mc_pass = X_gen_mc[s1b]
    X_gen_mc_miss = X_gen_mc[pgb & ~s1b]
    
    w_truth_mc = pop["b_w_truth"][pgb]
    w_reco_mc = pop["b_w_reco"]
    
    c = bu.ENGINE_NORMALIZATION / w_reco_mc[s1b].sum()
    w_truth_mc *= c
    w_reco_mc *= c
    w_data *= bu.ENGINE_NORMALIZATION / w_data.sum()
    
    w_reco_mc_pass = w_reco_mc[s1b]
    w_truth_mc_pass = w_truth_mc[s1b[pgb]]
    w_truth_mc_miss = w_truth_mc[~s1b[pgb]]

    records = []
    
    for seed in [1, 2, 3]:
        t0 = time.perf_counter()
        
        # Train Step 1
        classifier, c_mean, c_std = train_classifier(X_reco_mc_pass, X_reco_data, w_reco_mc_pass, w_data, epochs=50, lr=1e-3, seed=seed)
        
        # Train Step 2
        unfolder, z_mean, z_std = train_unfolder(classifier, c_mean, c_std, X_gen_mc_pass, X_reco_mc_pass, w_truth_mc_pass, X_gen_mc_miss, w_truth_mc_miss, epochs=50, lr=1e-3, seed=seed)
        
        # Evaluation
        unfolder.eval()
        with torch.no_grad():
            def transform(x):
                return np.sign(x) * np.log1p(np.abs(x))
            Z_all_t = transform(X_gen_mc)
            Z_all_z = (Z_all_t - z_mean) / z_std
            Z_tensor = torch.tensor(Z_all_z, dtype=torch.float32)
            lw_z = unfolder(Z_tensor).numpy()
            
        ratio2 = _capped_ratio(lw_z)
        push = np.ones_like(w_truth_mc)
        push = ratio2
        
        t1 = time.perf_counter()
        
        rec_score = scm.score_push(endpoint, push, run_ibu.SCOREABLE, run_ibu.INFORMATIONAL)
        
        records.append({
            "seed": seed,
            "seconds": t1 - t0,
            "push": rec_score
        })
        print(f"[aussie] seed={seed} R={rec_score['recovery']:.4f} t={t1-t0:.1f}s")
        
    payload = {
        "schema": "phase-f-aussie-scalar/1",
        "task": {
            "inputs": inputs,
            "truth_features": features.labels("truth4", reco=False),
        },
        "event_counts": {
            "prior_pass_reco_and_gen": int(s1b.sum()),
            "prior_pass_gen_only": int((pgb & ~s1b).sum())
        },
        "iterations": records,
    }
    out_file = out_dir / "aussie_scalar.json"
    scm.write_json(out_file, payload, compact=True)
    
if __name__ == "__main__":
    main()
