import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, '/Users/josephbailey/local-research/MINERvA-OmniFold-pet-prong-semantics/nd-unfolding/pet')
import typed_descriptor_source_smoke as smoke
import typed_descriptor_source_audit as audit
def _raw_entry(entry: int) -> dict[str, object]:
    cluster_count = 15
    raw: dict[str, object] = {'ev_run': 10068, 'ev_subrun': 4, 'ev_gate': 1000 + entry, 'MasterAnaDev_leptonE': [300.0, 400.0, 2500.0, 2600.0], 'MasterAnaDev_minos_trk_p': 1500.0, 'muon_thetaX': 0.1, 'muon_thetaY': -0.2, 'isMinosMatchTrack': 1, 'MasterAnaDev_minos_trk_is_ok': 1, 'MasterAnaDev_minos_trk_qp': -0.0004, 'vtx': [10.0, -20.0, 6000.0, 0.0], 'cluster_energy': [float(index + 1) for index in range(cluster_count)], 'cluster_pos': [float(10 * index) for index in range(cluster_count)], 'cluster_z': [float(5000 + index) for index in range(cluster_count)], 'cluster_view': [index % 3 + 1 for index in range(cluster_count)], 'cluster_time': [float(-20 + index) for index in range(cluster_count)], 'cluster_isMuontrack': [1 if index in (2, 7) else 0 for index in range(cluster_count)], 'n_prongs': 3, 'prong_part_pos': [[1.0, 2.0, 3.0, 4.0], [5.0, -999.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0]], 'prong_part_E': [[10.0, 20.0, 30.0, 40.0], [50.0, 60.0, -999.0, 80.0], [90.0, 100.0, 110.0, 120.0]], 'prong_part_score': [0.1, 0.2, 0.3], 'prong_part_mass': [100.0, 200.0, 300.0], 'prong_part_charge': [1, -999, -1], 'prong_part_pid': [0, 9, 13], 'prong_dEdXMean': [-999.0, 2.0, 3.0]}
    for name in smoke.GENERIC_VALUE_BRANCHES:
        raw[f'{name}_sz'] = cluster_count
    for photon_index, presence_energy in ((1, 100.0), (2, -999.0)):
        raw[f'gamma{photon_index}_E'] = presence_energy
        raw[f'gamma{photon_index}_direction'] = [0.1, -999.0, 0.9] if photon_index == 1 and entry == 0 else [0.1, 0.2, 0.9]
        raw[f'gamma{photon_index}_dEdx'] = -999.0 if entry == 0 else 3.0
        raw[f'gamma{photon_index}_time'] = 12.0
        for suffix, value in (('energy_trkr', 20.0), ('energy_ecal', 30.0), ('energy_hcal', 5.0), ('energy_scal_X', 2.0), ('energy_scal_UV', 3.0), ('evis_trkr', 18.0), ('evis_ecal', 27.0), ('evis_hcal', 4.0), ('evis_scal_X', 1.0), ('evis_scal_UV', 2.0)):
            raw[f'gamma{photon_index}_{suffix}'] = value
    blob_values = {'MasterAnaDev_BlobX': [1.0, 2.0], 'MasterAnaDev_BlobY': [3.0, 4.0], 'MasterAnaDev_BlobZ': [5001.0, 5002.0], 'MasterAnaDev_BlobT': [10.0, -999.0], 'MasterAnaDev_BlobTPos': [0.5, 0.7], 'MasterAnaDev_BlobTotalE': [50.0, 75.0], 'MasterAnaDev_BlobIs3D': [1, 0], 'MasterAnaDev_BlobNClusters': [3, 5]}
    for name, values in blob_values.items():
        raw[name] = values
        raw[f'{name}_sz'] = len(values)
    return raw
raw = _raw_entry(1)
batch = audit.map_row(raw, smoke.FIXED_SOURCES[0], 0)
audit.check_mapping(raw, batch)
print("MAPPING_PASS", flush=True)
try:
    audit.ForwardCheck()(batch)
except BaseException:
    import traceback
    traceback.print_exc()
    raise
print("PASS: synthetic mapping and forward under import guard")
