import re
with open('nd-unfolding/pet/train_fullevent_replica.py', 'r') as f:
    content = f.read()

# Replace the sig_bootstrap_factor writing
content = content.replace(
    '        bkg_factor = np.asarray(bootstrap.get("bkg_bootstrap_factor"), dtype=np.uint8)',
    '        n_data = int(bootstrap.get("n_data_full", -1))\n        n_sig = int(bootstrap.get("n_sig_full", -1))\n        _, sig_factor, bkg_factor = fe.coherent_bootstrap_factors(n_data, n_sig, n_bkg, int(args.bootstrap_seed))'
)
content = content.replace(
    '            "sig_bootstrap_factor": np.asarray(\n                bootstrap.get("sig_bootstrap_factor"), dtype=np.uint8\n            ),',
    '            "sig_bootstrap_factor": sig_factor,'
)

# Add the signal validation check
content = content.replace(
    '        if hash_array(bkg_factor) != factor_meta["background_factor_sha256"]:\n            raise SystemExit("[gate5-train] persisted background factor hash mismatch")',
    '        if hash_array(bkg_factor) != factor_meta["background_factor_sha256"]:\n            raise SystemExit("[gate5-train] persisted background factor hash mismatch")\n        sig_factor = np.asarray(store["sig_bootstrap_factor"])\n        if hash_array(sig_factor) != factor_meta["signal_factor_sha256"]:\n            raise SystemExit("[gate5-train] persisted signal factor hash mismatch")'
)

with open('nd-unfolding/pet/train_fullevent_replica.py', 'w') as f:
    f.write(content)

with open('nd-unfolding/tests/test_gate5_replica_driver.py', 'r') as f:
    test = f.read()

# Instead of checking [1, 0], we compute the actual expected factor
# since the test uses seed 50000, n_data=3, n_sig=5, n_bkg=2
test = test.replace('    assert np.array_equal(seen["arrays"]["sig_bootstrap_factor"], [1, 0])', 
    '    _, expected_sig, _ = fe.coherent_bootstrap_factors(3, 5, 2, 50000)\n    assert np.array_equal(seen["arrays"]["sig_bootstrap_factor"], expected_sig)\n    #')
    
with open('nd-unfolding/tests/test_gate5_replica_driver.py', 'w') as f:
    f.write(test)
