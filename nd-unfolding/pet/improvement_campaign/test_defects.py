import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_unfold import CampaignMultiFold
from recipe import RunRecipe, StepRecipe, OptimizerRecipe
from unittest.mock import patch

import pytest
import tensorflow as tf
import numpy as np

class DummyData:
    def __init__(self, nmax):
        self.nmax = nmax
        self.reco = np.zeros((nmax, 10))
        self.gen = np.zeros((nmax, 10))
        self.pass_reco = np.ones(nmax, dtype=bool)
        self.pass_gen = np.ones(nmax, dtype=bool)
        self.weight = np.ones(nmax)

def test_per_step_batch_size():
    recipe = RunRecipe(
        step1=StepRecipe(
            optimizer=OptimizerRecipe("Adam", 1e-4),
            batch_size=512,
            epochs=2,
            patience=2
        ),
        step2=StepRecipe(
            optimizer=OptimizerRecipe("Adam", 1e-4),
            batch_size=2048,
            epochs=2,
            patience=2
        ),
        iterations=2,
        arm_id="ours",
        event_split_seed=42
    )

    data = DummyData(4096)
    mc = DummyData(4096)
    
    model1 = tf.keras.Sequential([tf.keras.layers.Dense(1)])
    model2 = tf.keras.Sequential([tf.keras.layers.Dense(1)])
    
    engine = CampaignMultiFold(
        run_recipe=recipe,
        name="test_engine",
        model_reco=model1,
        model_gen=model2,
        data=data,
        mc=mc,
        batch_size=128,  # Ignored by CampaignMultiFold
        epochs=10,       # Ignored by CampaignMultiFold
        verbose=False
    )
    
    batch_sizes_used = []
    
    original_multifold_run_model = CampaignMultiFold.__bases__[0].RunModel
    def mock_run_model(self, labels, weights, iteration, model, stepn, NTRAIN=1000, cached=False):
        batch_sizes_used.append((stepn, self.BATCH_SIZE))
        
    with patch('omnifold.omnifold.MultiFold.RunModel', new=mock_run_model):
        engine.Unfold()
    
    step1_batches = [b for s, b in batch_sizes_used if s == 1]
    step2_batches = [b for s, b in batch_sizes_used if s == 2]
    
    assert all(b == 512 for b in step1_batches)
    assert all(b == 2048 for b in step2_batches)

def test_optimizer_is_correctly_applied():
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
        iterations=2,
        arm_id="ours",
        event_split_seed=42
    )
    
    data = DummyData(4096)
    mc = DummyData(4096)
    model1 = tf.keras.Sequential([tf.keras.layers.Dense(1)])
    model2 = tf.keras.Sequential([tf.keras.layers.Dense(1)])
    
    engine = CampaignMultiFold(
        run_recipe=recipe,
        name="test_engine2",
        model_reco=model1,
        model_gen=model2,
        data=data,
        mc=mc,
        verbose=False
    )
    
    engine.CompileModels(fixed=False)
    
    assert isinstance(engine.model1.optimizer, tf.keras.optimizers.AdamW)
    assert isinstance(engine.model2.optimizer, tf.keras.optimizers.Adam)

