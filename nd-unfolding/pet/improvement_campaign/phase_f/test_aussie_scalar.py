import numpy as np
import torch
import torch.nn.functional as F
from aussie_scalar import train_classifier, train_unfolder

def test_aussie_1d_gaussian_toy():
    np.random.seed(0)
    N = 50000
    z_sim = np.random.normal(0, 1, N).reshape(-1, 1)
    x_sim = np.random.normal(z_sim, 2).reshape(-1, 1)
    w_sim = np.ones(N)
    
    z_data = np.random.normal(0.2, 0.9, N).reshape(-1, 1)
    x_data = np.random.normal(z_data, 2).reshape(-1, 1)
    w_data = np.ones(N)
    
    # Train step 1
    classifier = train_classifier(x_sim, x_data, w_sim, w_data, epochs=20, batch_size=1024, lr=1e-2, seed=0)
    
    # Check step 1 (R(x))
    # Optimal R(x) = N(x; 0.2, 0.9^2 + 2^2) / N(x; 0, 1^2 + 2^2)
    # var_data = 0.9**2 + 2**2 = 4.81
    # var_sim = 1**2 + 2**2 = 5
    
    # Train step 2 (L_AutoDiff)
    # In this toy, there are no misses (everyone passes reco)
    unfolder = train_unfolder(classifier, z_sim, x_sim, w_sim, np.empty((0, 1)), np.empty((0,)), epochs=100, batch_size=2048, lr=1e-2, seed=0)
    
    # Check step 2 (R(z))
    # Optimal R(z) = N(z; 0.2, 0.9^2) / N(z; 0, 1^2)
    # R(z) = (1 / 0.9) * exp(-0.5 * ((z-0.2)/0.9)^2 + 0.5 * z^2)
    
    z_eval = np.linspace(-3, 3, 100).reshape(-1, 1)
    r_true = (1 / 0.9) * np.exp(-0.5 * ((z_eval - 0.2) / 0.9)**2 + 0.5 * z_eval**2)
    
    with torch.no_grad():
        unfolder.eval()
        lw_z = unfolder(torch.tensor(z_eval, dtype=torch.float32)).numpy()
        r_pred = np.exp(lw_z)
        
    err = np.abs(r_true.squeeze() - r_pred.squeeze()).mean()
    print(f"Mean absolute error on R(z): {err:.4f}")
    assert err < 0.2, f"Error too high: {err:.4f}"

if __name__ == '__main__':
    test_aussie_1d_gaussian_toy()
