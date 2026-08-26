#!/usr/bin/env python3
"""Train one guarded PET-v2 weighted/literal arm and reweight the full inventory.

Exactly one of W_A, W_B, or L is trained per fresh process.  The intervention
changes only multiplicity representation: policy, unique-event split, models,
seeds, epochs, iterations, batch size, and learning schedule remain frozen.
This diagnostic writes no covariance and has no submission path.
"""

import argparse
import datetime as dt
import gc
import json
import os
import pickle
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "2d-unfolding", REPO / "nd-unfolding",
             REPO / "nd-unfolding/pet", REPO / "omnifold_nn"):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import fullevent_fps_dataloader as fe  # noqa: E402
import extract_fullevent_fps as extractor  # noqa: E402
from atomic_write import atomic_savez_compressed, atomic_write, is_complete, mark_complete  # noqa: E402
from pet_v2_equivalence_common import (  # noqa: E402
    BATCH_SIZE, BOOTSTRAP_SEED, CONTRACT_ID, EARLY_STOPPING_PATIENCE,
    EPOCHS_RECO, EPOCHS_TRUTH, ESTIMATOR_SEED, EXPECTED_INPUT_SHA256,
    EXPECTED_INPUT_SIZE, EXPECTED_WEIGHTED_TARGET_SHA256, MAX_EVENTS, NITER,
    PROHIBITIONS, REQUIRED_CLASS_RATIO, SUBSAMPLE_SEED,
    assert_deterministic_environment, assert_regular_file, fixed_factors,
    git_head, hash_array, literal_source_index, scalar, sha256_file,
)

SCHEMA = "pet-v2-equivalence-arm-v1"
ARMS = ("W_A", "W_B", "L")


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def _write_json(path, payload, note):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(_jsonable(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    atomic_write(str(path), writer, suffix=".json", overwrite=False, fsync=True)
    mark_complete(str(path), note=note)


def _write_npy(path, value, note):
    def writer(tmp):
        with open(tmp, "wb") as stream:
            np.save(stream, value, allow_pickle=False)
    atomic_write(str(path), writer, suffix=".npy", overwrite=False, fsync=True)
    mark_complete(str(path), note=note)


def _read_target_contract(args):
    receipt_path = assert_regular_file(
        args.target_receipt, sha256=args.expected_target_receipt_sha256,
        label="paired target receipt"
    )
    if not is_complete(str(receipt_path)):
        raise SystemExit("[pet-v2-train] paired target receipt completion marker invalid")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema") != "pet-v2-equivalence-paired-target-v1" or \
            receipt.get("status") != "PASS_TARGETS_AND_SPLIT":
        raise SystemExit("[pet-v2-train] paired target receipt is not a passing v1 receipt")
    if receipt.get("contract_id") != CONTRACT_ID:
        raise SystemExit("[pet-v2-train] target contract ID mismatch")
    if receipt.get("prohibitions_applied") != {key: True for key in PROHIBITIONS}:
        raise SystemExit("[pet-v2-train] target Gate-6 prohibitions drift")
    if receipt.get("execution", {}).get("head") != args.expected_head:
        raise SystemExit("[pet-v2-train] target and training HEADs differ")
    paths = {
        "weighted": assert_regular_file(
            args.weighted_target, sha256=receipt["weighted"]["sha256"],
            label="weighted target"),
        "literal": assert_regular_file(
            args.literal_target, sha256=receipt["literal"]["sha256"],
            label="literal target"),
        "literal_aggregate": assert_regular_file(
            args.literal_aggregate_target,
            sha256=receipt["literal"]["aggregate_sha256"],
            label="literal aggregate target"),
        "split": assert_regular_file(
            args.split_manifest, sha256=receipt["split"]["sha256"],
            label="split manifest"),
    }
    if receipt["weighted"]["sha256"] != EXPECTED_WEIGHTED_TARGET_SHA256:
        raise SystemExit("[pet-v2-train] weighted target does not carry the historical digest")
    if float(receipt["class_ratio"]["R"]) != REQUIRED_CLASS_RATIO:
        raise SystemExit("[pet-v2-train] target receipt class ratio drift")
    for label, path in paths.items():
        if not is_complete(str(path)):
            raise SystemExit(f"[pet-v2-train] {label} completion marker invalid")
    return receipt_path, receipt, paths


def _gpu_identity(tf):
    devices = tf.config.list_physical_devices("GPU")
    if len(devices) != 1:
        raise SystemExit(f"[pet-v2-train] exactly one visible GPU required, observed {devices}")
    rows = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name,uuid,driver_version,memory.total",
         "--format=csv,noheader,nounits"], text=True
    ).strip().splitlines()
    if len(rows) != 1:
        raise SystemExit(f"[pet-v2-train] nvidia-smi did not report exactly one GPU: {rows}")
    name, uuid, driver, memory_mib = [item.strip() for item in rows[0].split(",")]
    if name != "NVIDIA A100-SXM4-80GB" or int(memory_mib) < 80_000:
        raise SystemExit(
            f"[pet-v2-train] hardware is {name} {memory_mib} MiB, not A100-SXM4-80GB"
        )
    details = tf.config.experimental.get_device_details(devices[0])
    return {"name": name, "uuid": uuid, "driver_version": driver,
            "memory_total_mib": int(memory_mib), "tensorflow_details": details,
            "tensorflow_version": tf.__version__,
            "tensorflow_build": tf.sysconfig.get_build_info()}


def _ess(weight):
    weight = np.asarray(weight, np.float64)
    denom = float(np.square(weight).sum(dtype=np.float64))
    return 0.0 if denom == 0.0 else float(weight.sum(dtype=np.float64) ** 2 / denom)


def _quantiles(value):
    value = np.asarray(value, np.float64)
    levels = (0.0, 0.01, 0.1, 0.5, 0.9, 0.99, 1.0)
    return {str(level): float(x) for level, x in zip(levels, np.quantile(value, levels))}


def _model_inputs(cloud, event, indices):
    return (cloud[indices], event[indices])


def _prediction_discrepancy(tf, model, best_path, validation_inputs, batch_size=4096):
    # A fixed prefix of the predeclared validation partition; it is diagnostic, not a gate.
    n = min(4096, len(validation_inputs[0]))
    sample = (validation_inputs[0][:n], validation_inputs[1][:n])
    final = np.asarray(model.predict(sample, batch_size=batch_size, verbose=False), np.float64)
    best = tf.keras.models.clone_model(model)
    # Build the clone before loading a HDF5 weight-only checkpoint.
    best.predict((sample[0][:1], sample[1][:1]), verbose=False)
    best.load_weights(str(best_path))
    best_value = np.asarray(best.predict(sample, batch_size=batch_size, verbose=False), np.float64)
    difference = np.abs(final - best_value)
    return {"rows": int(n), "mean_abs_logit": float(difference.mean()),
            "max_abs_logit": float(difference.max()),
            "final_sha256": hash_array(final), "best_sha256": hash_array(best_value)}


def make_equivalence_multifold(MultiFold, tf, arm, split, literal, signal_factor,
                               imc, histories, diagnostics, truth_scalars, loss_fn=None):
    """Subclass only the finite-batch construction; shared PET/reweight bytes remain in engine."""

    class EquivalenceMultiFold(MultiFold):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.arm = arm
            self._static = {}
            self._iteration_push = []

        def _representation(self, stepn):
            if stepn in self._static:
                return self._static[stepn]
            sig_mult = np.asarray(signal_factor[imc], np.uint8)
            if stepn == 1:
                if self.arm == "L":
                    mc_source = literal_source_index(sig_mult)
                    measured_source = np.asarray(literal["source_index"], np.int64)
                else:
                    mc_source = np.arange(self.mc.nmax, dtype=np.int64)
                    measured_source = np.arange(self.data.nmax, dtype=np.int64)
                cloud = np.concatenate(
                    [self.mc.reco[mc_source], self.data.reco[measured_source]], axis=0)
                event = np.concatenate(
                    [self.mc.reco_evt[mc_source], self.data.reco_evt[measured_source]], axis=0)
                labels = np.concatenate(
                    [np.zeros(mc_source.size, np.float32),
                     np.ones(measured_source.size, np.float32)])
                split_mask = np.concatenate(
                    [np.asarray(split["signal_train"], bool)[mc_source],
                     np.concatenate([np.asarray(split["data_train"], bool),
                                     np.asarray(split["background_train"], bool)])[measured_source]])
                sources = (mc_source, measured_source)
            elif stepn == 2:
                base = (literal_source_index(sig_mult) if self.arm == "L"
                        else np.arange(self.mc.nmax, dtype=np.int64))
                sources = (base, base)
                source = np.concatenate([base, base])
                cloud = np.concatenate([self.mc.gen[base], self.mc.gen[base]], axis=0)
                event = np.concatenate([self.mc.gen_evt[base], self.mc.gen_evt[base]], axis=0)
                labels = np.concatenate(
                    [np.zeros(base.size, np.float32), np.ones(base.size, np.float32)])
                split_mask = np.concatenate(
                    [np.asarray(split["signal_train"], bool)[base],
                     np.asarray(split["signal_train"], bool)[base]])
                del source
            else:
                raise ValueError("stepn must be 1 or 2")
            train_index = np.flatnonzero(split_mask)
            validation_index = np.flatnonzero(~split_mask)
            order = np.concatenate([train_index, validation_index])
            ordered_cloud = cloud[order]
            ordered_event = event[order]
            ordered_labels = labels[order]
            options = tf.data.Options()
            options.experimental_deterministic = True
            feature_ds = tf.data.Dataset.from_tensor_slices(
                (ordered_cloud, ordered_event)).with_options(options)
            result = {
                "feature_ds": feature_ds, "cloud": ordered_cloud, "event": ordered_event,
                "labels": ordered_labels, "order": order,
                "n_train": int(train_index.size), "n_validation": int(validation_index.size),
                "sources": sources,
                "split_hash": hash_array(split_mask),
                "representation_rows": int(split_mask.size),
            }
            self._static[stepn] = result
            del cloud, event, labels, split_mask, train_index, validation_index
            gc.collect()
            return result

        def _represented_weights(self, stepn):
            rep = self._representation(stepn)
            sig_mult = np.asarray(signal_factor[imc], np.float32)
            if stepn == 1:
                mc_source, measured_source = rep["sources"]
                if self.arm == "L":
                    mc_weight = np.asarray(self.mc_weight_reco[mc_source], np.float32) / \
                        sig_mult[mc_source]
                    measured_weight = np.asarray(literal["weight"], np.float32)
                    if not np.array_equal(measured_source,
                                          np.asarray(literal["source_index"], np.int64)):
                        raise SystemExit("[pet-v2-train] literal measured source map drift")
                else:
                    mc_weight = np.asarray(self.mc_weight_reco, np.float32)
                    measured_weight = np.asarray(self.data.weight, np.float32)
                weight = np.concatenate(
                    [self.weights_push[mc_source] * mc_weight * self.mc.pass_reco[mc_source],
                     measured_weight * self.data.pass_reco[measured_source]])
            else:
                base, _ = rep["sources"]
                if self.arm == "L":
                    truth_weight = np.asarray(self.mc.weight[base], np.float32) / sig_mult[base]
                else:
                    truth_weight = np.asarray(self.mc.weight, np.float32)
                weight = np.concatenate(
                    [truth_weight * self.mc.pass_gen[base],
                     truth_weight * self.weights_pull[base] * self.mc.pass_gen[base]])
            if weight.shape != rep["labels"].shape or not np.isfinite(weight).all():
                raise SystemExit("[pet-v2-train] represented training weights invalid")
            return weight

        def _fit(self, iteration, stepn, model):
            rep = self._representation(stepn)
            weights = self._represented_weights(stepn)
            order = rep["order"]
            label_weight = np.stack([rep["labels"], weights[order]], axis=1)
            data = tf.data.Dataset.zip(
                (rep["feature_ds"], tf.data.Dataset.from_tensor_slices(label_weight)))
            options = tf.data.Options()
            options.experimental_deterministic = True
            data = data.with_options(options)
            n_train, n_validation = rep["n_train"], rep["n_validation"]
            train_steps = n_train // BATCH_SIZE
            validation_steps = n_validation // BATCH_SIZE
            if train_steps < 1 or validation_steps < 1:
                raise SystemExit("[pet-v2-train] empty fit partition after batching")
            shuffle_seed = ESTIMATOR_SEED + 1000 * int(iteration) + 10 * int(stepn)
            train = data.take(n_train).shuffle(
                n_train, seed=shuffle_seed, reshuffle_each_iteration=True
            ).repeat().batch(BATCH_SIZE).prefetch(1)
            validation = data.skip(n_train).repeat().batch(BATCH_SIZE).prefetch(1)
            lr = 1e-4 if int(iteration) == 0 else 1e-5
            model.compile(tf.keras.optimizers.Adam(learning_rate=lr),
                          loss=self._pet_v2_loss, weighted_metrics=[])
            best_path = Path(self.weights_folder) / (
                f"OmniFold_{self.name}_iter{iteration}_step{stepn}_best.weights.h5")
            final_path = Path(self.weights_folder) / (
                f"OmniFold_{self.name}_iter{iteration}_step{stepn}_final.weights.h5")
            early = tf.keras.callbacks.EarlyStopping(
                patience=EARLY_STOPPING_PATIENCE, restore_best_weights=True,
                monitor="val_loss")
            checkpoint = tf.keras.callbacks.ModelCheckpoint(
                str(best_path), save_best_only=True, save_weights_only=True,
                monitor="val_loss")
            epochs = EPOCHS_RECO if stepn == 1 else EPOCHS_TRUTH
            history = model.fit(
                train, epochs=epochs, steps_per_epoch=train_steps,
                validation_data=validation, validation_steps=validation_steps,
                verbose=False, callbacks=[early, checkpoint])
            model.save_weights(str(final_path))
            ran = len(history.history.get("loss", []))
            if ran != epochs or int(early.stopped_epoch) != 0:
                raise SystemExit(
                    f"[pet-v2-train] early stopping changed frozen {epochs}-epoch fit: "
                    f"ran={ran}, stopped_epoch={early.stopped_epoch}"
                )
            validation_inputs = (
                rep["cloud"][n_train:n_train + min(n_validation, 4096)],
                rep["event"][n_train:n_train + min(n_validation, 4096)],
            )
            discrepancy = _prediction_discrepancy(
                tf, model, best_path, validation_inputs)
            val_loss = np.asarray(history.history["val_loss"], np.float64)
            record = {
                "iteration": int(iteration), "step": int(stepn),
                "arm": self.arm, "learning_rate": lr,
                "epochs_requested": int(epochs), "epochs_ran": int(ran),
                "early_stopping_patience": EARLY_STOPPING_PATIENCE,
                "early_stopping_stopped_epoch": int(early.stopped_epoch),
                "best_epoch_zero_based": int(np.argmin(val_loss)),
                "train_rows": n_train, "validation_rows": n_validation,
                "representation_rows": rep["representation_rows"],
                "split_hash": rep["split_hash"],
                "train_steps_per_epoch": int(train_steps),
                "validation_steps": int(validation_steps),
                "optimizer_updates": int(train_steps * ran),
                "history": {key: [float(x) for x in value]
                            for key, value in history.history.items()},
                "best_checkpoint": str(best_path.resolve()),
                "best_checkpoint_sha256": sha256_file(best_path),
                "final_checkpoint": str(final_path.resolve()),
                "final_checkpoint_sha256": sha256_file(final_path),
                "best_final_validation_prediction": discrepancy,
            }
            histories.append(record)
            with open(str(final_path).replace(".weights.h5", ".history.pkl"), "wb") as stream:
                pickle.dump(history.history, stream)
            del train, validation, data, label_weight, weights
            gc.collect()

        def Unfold(self):
            self.step1_models, self.step2_models = [], []
            self.mc_weight_reco = (self.mc.weight if getattr(self.mc, "weight_reco", None) is None
                                   else self.mc.weight_reco)
            self.weights_pull = np.ones(self.mc.weight.shape[0], dtype=np.float32)
            self.weights_push = np.ones(self.mc.weight.shape[0], dtype=np.float32)
            for iteration in range(NITER):
                if iteration == 0:
                    self.step1_models.append(tf.keras.models.clone_model(self.model1))
                    self.step2_models.append(tf.keras.models.clone_model(self.model2))
                model1 = self.step1_models[0]
                model2 = self.step2_models[0]
                self._fit(iteration, 1, model1)
                new_pull = np.ones_like(self.weights_pull)
                reco_reweight = self.reweight(self._pack_reco(self.mc.reco), self.model1,
                                              batch_size=1000)
                new_pull[self.mc.pass_reco] = reco_reweight[self.mc.pass_reco]
                self.weights_pull = self.weights_push * new_pull
                self._fit(iteration, 2, model2)
                new_push = np.ones_like(self.weights_push)
                truth_reweight = self.reweight(self._pack_gen(self.mc.gen), self.model2,
                                               batch_size=1000)
                new_push[self.mc.pass_gen] = truth_reweight[self.mc.pass_gen]
                self.weights_push = new_push.astype(np.float32)
                self._iteration_push.append(self.weights_push.copy())
                truth_weight = np.asarray(self.mc.weight, np.float64) * self.weights_push
                reco_weight = np.asarray(self.mc_weight_reco, np.float64) * self.weights_push
                ppar = truth_scalars[:, fe.SCALAR_COLS["pparallel"]]
                regions = {
                    "ppar_lt_6": ppar < 6.0,
                    "ppar_6_to_20": (ppar >= 6.0) & (ppar <= 20.0),
                    "ppar_gt_20": ppar > 20.0,
                }
                diagnostics.append({
                    "iteration": int(iteration),
                    "truth_ess": _ess(truth_weight[self.mc.pass_gen]),
                    "reco_ess": _ess(reco_weight[self.mc.pass_reco]),
                    "push_quantiles": _quantiles(self.weights_push),
                    "push_max": float(self.weights_push.max()),
                    "cap_occupancy": int(np.count_nonzero(
                        np.abs(np.log(np.maximum(self.weights_push, np.finfo(np.float32).tiny))) >= 30.0)),
                    "fold_forward_reco_ratio": float(
                        reco_weight[self.mc.pass_reco].sum(dtype=np.float64) /
                        np.asarray(self.mc_weight_reco, np.float64)[self.mc.pass_reco].sum(dtype=np.float64)),
                    "target_class_ratio": REQUIRED_CLASS_RATIO,
                    "truth_region_weight_sums": {
                        key: float(truth_weight[self.mc.pass_gen & mask].sum(dtype=np.float64))
                        for key, mask in regions.items()},
                })

    if loss_fn is None:
        loss_fn = (__import__("omnifold.net", fromlist=["weighted_binary_crossentropy"])
                   .weighted_binary_crossentropy)
    EquivalenceMultiFold._pet_v2_loss = staticmethod(loss_fn)
    return EquivalenceMultiFold


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", required=True, choices=ARMS)
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--target-receipt", required=True)
    parser.add_argument("--expected-target-receipt-sha256", required=True)
    parser.add_argument("--weighted-target", required=True)
    parser.add_argument("--literal-target", required=True)
    parser.add_argument("--literal-aggregate-target", required=True)
    parser.add_argument("--split-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--full-inference-chunk", type=int, default=250_000)
    parser.add_argument("--full-inference-batch-size", type=int, default=4096)
    args = parser.parse_args(argv)

    assert_deterministic_environment()
    if git_head(REPO) != args.expected_head:
        raise SystemExit("[pet-v2-train] runtime HEAD mismatch")
    inputs = assert_regular_file(args.inputs, sha256=EXPECTED_INPUT_SHA256,
                                 size=EXPECTED_INPUT_SIZE, label="G2 source")
    target_receipt_path, target_receipt, paths = _read_target_contract(args)
    outdir = Path(args.output_dir).resolve()
    if outdir.exists():
        if outdir.is_symlink() or any(outdir.iterdir()):
            raise SystemExit(f"[pet-v2-train] output namespace occupied: {outdir}")
    outdir.mkdir(parents=True, exist_ok=True)
    weights_dir = outdir / "checkpoints"
    weights_dir.mkdir()
    artifact_path = outdir / "PETV2_ARM_ARTIFACT.npz"
    full_push_path = outdir / "PETV2_FULL_PUSH.npy"
    receipt_path = outdir / "PETV2_ARM_RECEIPT.json"

    # TensorFlow remains lazy until every CPU/provenance guard above has passed.
    import tensorflow as tf
    from omnifold import PET, MultiFold
    tf.config.experimental.enable_op_determinism()
    tf.keras.utils.set_random_seed(ESTIMATOR_SEED)
    gpu = _gpu_identity(tf)
    started = time.monotonic()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()

    with np.load(paths["split"], allow_pickle=False) as store:
        split = {key: np.asarray(store[key]) for key in store.files}
    with np.load(paths["literal"], allow_pickle=False) as store:
        literal = {key: np.asarray(store[key]) for key in store.files}
    target = paths["literal_aggregate"] if args.arm == "L" else paths["weighted"]
    data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        str(inputs), max_events=MAX_EVENTS, seed=SUBSAMPLE_SEED,
        bootstrap_seed=BOOTSTRAP_SEED, bkg_mode="negweight-refined",
        precomputed_target=str(target), precomputed_target_replica_seed=BOOTSTRAP_SEED,
        verify_identities=True,
    )
    if not np.array_equal(np.asarray(imc), np.asarray(split["mc_indices"])):
        raise SystemExit("[pet-v2-train] loader signal IDs differ from split manifest")
    target_meta = dict(meta.get("target") or {})
    if float(target_meta.get("step1_class_ratio", float("nan"))) != REQUIRED_CLASS_RATIO:
        raise SystemExit("[pet-v2-train] realized class ratio drift")
    n_data = int(target_receipt["inventory"]["n_data"])
    n_signal = int(target_receipt["inventory"]["n_signal"])
    n_background = int(target_receipt["inventory"]["n_background"])
    data_factor, signal_factor, background_factor = fixed_factors(
        n_data, n_signal, n_background)
    bootstrap = dict(meta.get("bootstrap") or {})
    if not np.array_equal(np.asarray(bootstrap["sig_bootstrap_factor"]), signal_factor[imc]):
        raise SystemExit("[pet-v2-train] loader signal multiplicity drift")
    if not np.array_equal(np.asarray(bootstrap["bkg_bootstrap_factor"]), background_factor):
        raise SystemExit("[pet-v2-train] loader background multiplicity drift")
    if hash_array(data_factor) != target_receipt["draw"]["data_factor_sha256"]:
        raise SystemExit("[pet-v2-train] loader/target data draw drift")

    P = int(np.asarray(mc.reco).shape[1])
    ev_reco, ev_truth = int(meta["n_evt_reco"]), int(meta["n_evt_truth"])
    m1 = PET(np.asarray(mc.reco).shape[-1], num_evt=ev_reco, num_part=P,
             num_transformer=2, num_heads=2, projection_dim=32,
             local=True, K=3, coord_idx=coord_reco)
    m2 = PET(np.asarray(mc.gen).shape[-1], num_evt=ev_truth, num_part=P,
             num_transformer=2, num_heads=2, projection_dim=32,
             local=True, K=3, coord_idx=coord_gen)
    with np.load(inputs, allow_pickle=True) as source:
        truth_scalars = np.asarray(source["truth_scalars"])[imc]
    histories, diagnostics = [], []
    EquivalenceMultiFold = make_equivalence_multifold(
        MultiFold, tf, args.arm, split, literal, signal_factor, imc,
        histories, diagnostics, truth_scalars)
    of = EquivalenceMultiFold(
        f"petv2_{args.arm}", m1, m2, data, mc, niter=NITER,
        epochs=EPOCHS_RECO, batch_size=BATCH_SIZE, early_stop=EARLY_STOPPING_PATIENCE,
        train_frac=0.8, weights_folder=str(weights_dir), log_folder=str(outdir),
        verbose=False)
    of.Unfold()
    if len(histories) != 2 * NITER or len(diagnostics) != NITER:
        raise SystemExit("[pet-v2-train] fit/iteration evidence is incomplete")
    final_step2 = histories[-1]["final_checkpoint"]
    inference_contract = {
        "weights_folder": str(weights_dir.resolve()),
        "step2_checkpoint": final_step2,
        "checkpoint_semantics": "final in-memory epoch; best tier retained separately",
        "pet_arch": {"num_feat_gen": int(np.asarray(mc.gen).shape[-1]),
                     "num_evt": ev_truth, "num_part": P, "num_transformer": 2,
                     "num_heads": 2, "projection_dim": 32, "local": True,
                     "K": 3, "coord_idx": list(coord_gen)},
        "event_features_reco": list(meta["feature_names"]),
        "event_features_truth": list(meta["truth_feature_names"]),
        "truth_norm_mean": list(meta["truth_norm_mean"]),
        "truth_norm_std": list(meta["truth_norm_std"]),
        "reco_norm_mean": list(meta["reco_norm_mean"]),
        "reco_norm_std": list(meta["reco_norm_std"]),
    }
    push_subset = np.asarray(of.weights_push, np.float64)
    full_push, inference_telem = extractor.reweight_full_inventory(
        str(inputs), inference_contract, chunk=args.full_inference_chunk,
        batch_size=args.full_inference_batch_size, model2=of.step2_models[0], progress=True)
    agreement_contract = dict(inference_contract)
    agreement_contract.update({"_subsample_indices": np.asarray(imc, np.int64),
                               "_subsample_push": push_subset})
    agreement = extractor.check_subsample_agreement(full_push, agreement_contract, tol=1e-3)
    _write_npy(full_push_path, np.asarray(full_push, np.float64),
               f"PET-v2 {args.arm} full-inventory push")
    artifact = {
        "schema": np.asarray(SCHEMA), "status": np.asarray("PASS_ARM_COMPLETE"),
        "contract_id": np.asarray(CONTRACT_ID), "arm": np.asarray(args.arm),
        "weights_push": push_subset, "iteration_push": np.stack(of._iteration_push),
        "mc_indices": np.asarray(imc, np.int64),
        "inference_contract": np.asarray(inference_contract, dtype=object),
        "histories": np.asarray(histories, dtype=object),
        "diagnostics": np.asarray(diagnostics, dtype=object),
        "input_sha256": np.asarray(EXPECTED_INPUT_SHA256),
        "target_receipt_sha256": np.asarray(sha256_file(target_receipt_path)),
        "target_sha256": np.asarray(sha256_file(target)),
        "split_sha256": np.asarray(sha256_file(paths["split"])),
        "signal_factor_sha256": np.asarray(hash_array(signal_factor)),
        "data_factor_sha256": np.asarray(hash_array(data_factor)),
        "background_factor_sha256": np.asarray(hash_array(background_factor)),
        "class_ratio": np.asarray(REQUIRED_CLASS_RATIO),
        "full_push_path": np.asarray(str(full_push_path)),
        "full_push_sha256": np.asarray(sha256_file(full_push_path)),
        "subsample_agreement": np.asarray(agreement, dtype=object),
    }
    atomic_savez_compressed(
        str(artifact_path), artifact, overwrite=False, fsync=True, mark=True,
        note=f"PET-v2 fixed-draw equivalence arm {args.arm}")
    completed = dt.datetime.now(dt.timezone.utc).isoformat()
    receipt = {
        "schema": SCHEMA, "status": "PASS_ARM_COMPLETE", "contract_id": CONTRACT_ID,
        "scope": "PET_DIAGNOSTIC_AND_METHOD_DEVELOPMENT_ONLY", "arm": args.arm,
        "representation": ("literal delete/duplicate" if args.arm == "L"
                           else "weighted multiplicity with zero rows retained"),
        "execution": {"head": git_head(REPO), "host": socket.gethostname(),
                      "pid": os.getpid(), "slurm_job_id": os.environ.get("SLURM_JOB_ID", "none"),
                      "started_at_utc": started_utc, "completed_at_utc": completed,
                      "elapsed_seconds": time.monotonic() - started},
        "gpu": gpu,
        "determinism": {"environment": {key: os.environ[key] for key in
                                         ("PYTHONHASHSEED", "TF_DETERMINISTIC_OPS",
                                          "CUBLAS_WORKSPACE_CONFIG")},
                        "op_determinism_enabled": True, "set_random_seed": ESTIMATOR_SEED,
                        "tf_data_deterministic": True},
        "policy": {"bootstrap_seed": BOOTSTRAP_SEED, "estimator_seed": ESTIMATOR_SEED,
                   "subsample_seed": SUBSAMPLE_SEED, "unique_signal_rows": MAX_EVENTS,
                   "niter": NITER, "epochs_reco": EPOCHS_RECO,
                   "epochs_truth": EPOCHS_TRUTH, "batch_size": BATCH_SIZE,
                   "early_stopping_patience": EARLY_STOPPING_PATIENCE,
                   "learning_rate": {"iteration_0": 1e-4, "iterations_1_2": 1e-5},
                   "optimizer": "new Adam per fit; model weights warm-start iterations"},
        "source": {"path": str(inputs), "sha256": sha256_file(inputs),
                   "target_receipt_sha256": sha256_file(target_receipt_path),
                   "target_sha256": sha256_file(target),
                   "split_sha256": sha256_file(paths["split"])},
        "fit_records": histories, "iteration_diagnostics": diagnostics,
        "full_inference": {**inference_telem, "subsample_agreement": agreement},
        "artifacts": {"training": {"path": str(artifact_path),
                                    "sha256": sha256_file(artifact_path),
                                    "size_bytes": artifact_path.stat().st_size},
                      "full_push": {"path": str(full_push_path),
                                    "sha256": sha256_file(full_push_path),
                                    "size_bytes": full_push_path.stat().st_size}},
        "prohibitions_applied": {key: True for key in PROHIBITIONS},
        "cannot_authorize": ["C_stat", "C_ML", "central movement", "Leg 2",
                             "unchanged retry", "coverage", "publication adoption"],
    }
    _write_json(receipt_path, receipt, f"PET-v2 arm {args.arm} receipt; published last")
    print(json.dumps({"status": receipt["status"], "arm": args.arm,
                      "receipt": str(receipt_path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
