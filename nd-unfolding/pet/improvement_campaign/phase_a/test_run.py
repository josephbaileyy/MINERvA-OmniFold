import sys
from pathlib import Path
import json
import time

repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root / "nd-unfolding" / "pet" / "improvement_campaign"))
sys.path.insert(0, str(repo_root / "nd-unfolding" / "pet" / "configuration_comparison"))
sys.path.insert(0, str(repo_root / "omnifold_nn"))
sys.path.insert(0, str(repo_root))

from run_unfold import CampaignMultiFold
from recipe import RunRecipe, StepRecipe, OptimizerRecipe
from authorization_scope import check_authorization
import data_loaders
import tensorflow as tf
from omnifold.net import get_network

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--identity-sidecar", required=True)
    args = parser.parse_args()
    
    check_authorization(False, Path(args.out))

    loader_args = {
        "inputs_npz": args.inputs,
        "identity_sidecar": args.identity_sidecar,
        "split_seed": 20260920,
        "is_theirs": False,
        "use_val_split": False
    }

    print("Loading data...")
    mc_loader = data_loaders.DataLoader(**loader_args, split="tuning", is_mc=True)
    data_loader = data_loaders.DataLoader(**loader_args, split="tuning", is_mc=False)
    
    # Subsample for test
    mc_loader.nmax = 10000
    data_loader.nmax = 10000
    
    model1 = get_network(input_shape=(10,), n_features=22)
    model2 = get_network(input_shape=(10,), n_features=22)
    
    recipe = RunRecipe(
        step1=StepRecipe(
            optimizer=OptimizerRecipe("AdamW", 1e-4, weight_decay=0.01),
            batch_size=512,
            epochs=2,
            patience=2
        ),
        step2=StepRecipe(
            optimizer=OptimizerRecipe("Adam", 1e-4),
            batch_size=512,
            epochs=2,
            patience=2
        ),
        iterations=1,
        arm_id="ours",
        event_split_seed=20260920
    )
    
    print("Initializing CampaignMultiFold...")
    engine = CampaignMultiFold(
        run_recipe=recipe,
        name="test_run",
        model_reco=model1,
        model_gen=model2,
        data=data_loader,
        mc=mc_loader,
        weights_folder=args.out,
        verbose=True
    )
    
    t0 = time.time()
    engine.Unfold()
    t1 = time.time()
    
    print(f"DONE. Elapsed: {t1 - t0:.2f} s")
    
if __name__ == "__main__":
    main()
