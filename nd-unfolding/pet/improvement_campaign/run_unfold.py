import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

# Setup paths to import omnifold_nn and pet
repo_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "omnifold_nn"))
sys.path.insert(0, str(repo_root / "nd-unfolding" / "pet"))

sys.path.insert(0, str(repo_root / "nd-unfolding" / "pet" / "configuration_comparison"))
sys.path.insert(0, str(repo_root / "nd-unfolding" / "pet" / "improvement_campaign"))

import tensorflow as tf
import numpy as np

from omnifold.omnifold import MultiFold
from omnifold.net import weighted_binary_crossentropy
from recipe import RunRecipe, StepRecipe, OptimizerRecipe
from authorization_scope import check_authorization

class CampaignMultiFold(MultiFold):
    def __init__(self, run_recipe: RunRecipe, *args, **kwargs):
        self.run_recipe = run_recipe
        super().__init__(*args, **kwargs)
        
    def CompileModel(self, model, num_steps, fixed=False):
        stepn = 1 if model is self.model1 or (hasattr(self, "step1_models") and model in self.step1_models) else 2
        recipe = self.run_recipe.step1 if stepn == 1 else self.run_recipe.step2
        
        opt_recipe = recipe.optimizer
        
        lr_schedule = opt_recipe.learning_rate
        if opt_recipe.cosine_decay_steps > 0:
            lr_schedule = tf.keras.optimizers.schedules.CosineDecay(
                initial_learning_rate=opt_recipe.learning_rate,
                decay_steps=opt_recipe.cosine_decay_steps,
                alpha=0.0
            )
        
        if opt_recipe.family == "Adam":
            opt = tf.keras.optimizers.Adam(
                learning_rate=lr_schedule,
                beta_1=opt_recipe.beta_1,
                beta_2=opt_recipe.beta_2,
                epsilon=opt_recipe.epsilon,
                global_clipnorm=opt_recipe.global_clipnorm
            )
        elif opt_recipe.family == "AdamW":
            opt = tf.keras.optimizers.AdamW(
                learning_rate=lr_schedule,
                weight_decay=opt_recipe.weight_decay,
                beta_1=opt_recipe.beta_1,
                beta_2=opt_recipe.beta_2,
                epsilon=opt_recipe.epsilon,
                global_clipnorm=opt_recipe.global_clipnorm
            )
        else:
            raise ValueError(f"Unknown optimizer family: {opt_recipe.family}")

        model.compile(optimizer=opt, loss=weighted_binary_crossentropy, weighted_metrics=[])

    def RunModel(self, labels, weights, iteration, model, stepn, NTRAIN=1000, cached=False):
        recipe = self.run_recipe.step1 if stepn == 1 else self.run_recipe.step2
        self.BATCH_SIZE = recipe.batch_size
        self.EPOCHS = recipe.epochs
        self.patience = recipe.patience
        
        # We also need a per-epoch recorder that writes train/val loss, lr, update counts, grad norms and weight-tail/ESS stats.
        # This will be implemented by overriding fit or passing a custom callback.
        # But for now, just calling super
        
        # Override fit to inject our custom callback
        original_fit = model.fit
        
        class CampaignRecorder(tf.keras.callbacks.Callback):
            def __init__(self):
                super().__init__()
                self.history_records = []
            
            def on_epoch_end(self, epoch, logs=None):
                logs = logs or {}
                lr = tf.keras.backend.get_value(self.model.optimizer.learning_rate)
                if hasattr(lr, '__call__'):
                    # if it's a schedule
                    lr = lr(self.model.optimizer.iterations)
                
                iterations = tf.keras.backend.get_value(self.model.optimizer.iterations)
                
                # ESS stats can be computed on validation set ideally, but for now we just record basics
                record = {
                    "epoch": epoch,
                    "loss": logs.get("loss"),
                    "val_loss": logs.get("val_loss"),
                    "learning_rate": float(lr),
                    "optimizer_iterations": int(iterations)
                }
                self.history_records.append(record)
                
            def on_train_end(self, logs=None):
                with open(f"history_iter{iteration}_step{stepn}.json", "w") as f:
                    json.dump(self.history_records, f, indent=2)

        def custom_fit(*args, **kwargs):
            callbacks = kwargs.get("callbacks", [])
            callbacks.append(CampaignRecorder())
            kwargs["callbacks"] = callbacks
            return original_fit(*args, **kwargs)
            
        model.fit = custom_fit
        
        try:
            return super().RunModel(labels, weights, iteration, model, stepn, NTRAIN, cached)
        finally:
            model.fit = original_fit


def main():
    pass

if __name__ == "__main__":
    main()

