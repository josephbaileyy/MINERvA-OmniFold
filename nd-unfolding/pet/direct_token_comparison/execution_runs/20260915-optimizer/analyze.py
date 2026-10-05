"""Read closed tensor archives and attribute update discrepancies by replay."""
from pathlib import Path
import hashlib
import io
import json
import sys
import tarfile

import numpy as np

archive = Path(sys.argv[1])
with tarfile.open(archive) as stream:
    files = {m.name: stream.extractfile(m).read() for m in stream if m.isfile()}

def arrays(name):
    with np.load(io.BytesIO(files['capture/' + name]), allow_pickle=False) as source:
        return dict(source)

def metric(left, right):
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    assert left.shape == right.shape and np.isfinite(left).all() and np.isfinite(right).all()
    error = np.abs(left - right)
    return {'max_abs': float(error.max(initial=0)), 'failed': int(np.count_nonzero(error > 1e-5 + 1e-4 * np.abs(right))), 'exact': bool(np.array_equal(left, right))}

rows = []
for case in ('nominal', 'variable', 'masked', 'empty'):
    for route in ('pooled', 'direct'):
        stem = f'{case}-{route}'
        row = json.loads(files[f'capture/{stem}/analysis.json'])
        metadata = json.loads(files[f'capture/{stem}/cpu/variables.json'])
        state_cpu = arrays(f'{stem}/cpu/state-2.npz')
        state_gpu = arrays(f'{stem}/candidate/state-2.npz')
        failed = []
        for i, variable in enumerate(metadata['weights']):
            key = f'weight_{i}'
            diff = metric(state_cpu[key], state_gpu[key])
            if not diff['failed']:
                continue
            gradient_index = metadata['trainable_paths'].index(variable['path'])
            cpu = state_cpu[key].astype(float)
            gpu = state_gpu[key].astype(float)
            index = int(np.argmax(np.abs(cpu - gpu)))
            sample = {'variable': variable['path'], 'weight_index': i, 'gradient_index': gradient_index, 'metric': diff, 'max_error_flat_index': index, 'cpu_weight': float(cpu.flat[index]), 'gpu_weight': float(gpu.flat[index]), 'gradients': {}}
            for step in ('eager', 'second'):
                a = arrays(f'{stem}/cpu/{step}.npz')[f'gradient_{gradient_index}']
                b = arrays(f'{stem}/candidate/{step}.npz')[f'gradient_{gradient_index}']
                sample['gradients'][step] = {'cpu': float(a.flat[index]), 'gpu': float(b.flat[index]), 'metric': metric(a, b)}
            high_cpu = arrays(f'{stem}/float64-cpu-2.npz')[f'weight_{gradient_index}']
            high_gpu = arrays(f'{stem}/float64-candidate-2.npz')[f'weight_{gradient_index}']
            sample['float64_propagated'] = {'cpu': float(high_cpu.flat[index]), 'gpu': float(high_gpu.flat[index]), 'difference': float(abs(high_cpu.flat[index] - high_gpu.flat[index]))}
            failed.append(sample)
        replay_parity = []
        common = []
        float64_checks = []
        for label, target in (('cpu','cpu'), ('candidate','candidate')):
            for step in (1,2):
                native = arrays(f'{stem}/{label}/state-{step}.npz')
                same = arrays(f'{stem}/replay-{label}-{target}/step-{step}.npz')
                common_cpu = arrays(f'{stem}/replay-{label}-cpu/step-{step}.npz')
                common_gpu = arrays(f'{stem}/replay-{label}-candidate/step-{step}.npz')
                reference = arrays(f'{stem}/float64-{label}-{step}.npz')
                for j,path in enumerate(metadata['trainable_paths']):
                    i = next(i for i,v in enumerate(metadata['weights']) if v['path']==path)
                    replay_parity.append(metric(native[f'weight_{i}'],same[f'weight_{j}']))
                    float64_checks.append(metric(same[f'weight_{j}'],reference[f'weight_{j}']))
                for key in common_cpu:
                    common.append(metric(common_cpu[key],common_gpu[key]))
        prediction = metric(arrays(f'{stem}/cpu/prediction.npz')['prediction'],arrays(f'{stem}/candidate/prediction.npz')['prediction'])
        rows.append({'case': case, 'routing':route, 'instrumentation_exact':all(r['exact'] for r in row['instrumentation']), 'repeatability_exact':all(m['exact'] for r in row['repeatability'] for m in r.values()), 'initial_gradient_failures':sum(v['failed'] for k,v in row['comparisons']['initial'].items() if k.startswith('gradient_')), 'second_gradient_failures':sum(v['failed'] for k,v in row['comparisons']['second'].items() if k.startswith('gradient_')), 'failed_weights':failed, 'prediction':prediction, 'same_device_replay_exact':all(r['exact'] for r in replay_parity), 'same_device_replay_max_abs':max(r['max_abs'] for r in replay_parity), 'common_operand_failures':sum(r['failed'] for r in common), 'common_operand_max_abs':max(r['max_abs'] for r in common), 'float64_failures':sum(r['failed'] for r in float64_checks), 'float64_max_abs':max(r['max_abs'] for r in float64_checks)})
result = {'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(), 'rows':rows}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
for row in rows:
    print(json.dumps(row))
