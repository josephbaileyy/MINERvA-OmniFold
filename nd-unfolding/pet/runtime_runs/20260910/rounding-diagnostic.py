import sys,json,math,hashlib
from pathlib import Path
import numpy as np
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'nd-unfolding/pet'))
import typed_descriptor_source_audit as audit
import typed_descriptor_source_smoke as source
import typed_descriptors as typed
raw=json.loads((root/'nd-unfolding/pet/runtime_fixtures/source_audit.json').read_text())['rows'][0]
batch=audit.map_row(raw,source.FIXED_SOURCES[0],0)
reference=typed.ReferenceTypedDescriptorEncoder.initialize(audit.identity_normalization(),projection_dim=16,seed=0)
encoder=reference.family_encoders['prongs'];family=batch.descriptors.families['prongs'];features=encoder.contract.prepare_features(family,encoder.normalization)
column=4
pre=[math.fsum(float(x)*float(w) for x,w in zip(row,encoder.weight[:,column]))+float(encoder.bias[column]) for row in features]
pooled=math.fsum(math.tanh(x) for x in pre)
u=2**-24;n=features.shape[1];gamma=n*u/(1-n*u)
dot_bounds=[gamma*math.fsum(abs(float(x)*float(w)) for x,w in zip(row,encoder.weight[:,column])) for row in features]
print(json.dumps({'kind':'SYNTHETIC_ROUNDING_DIAGNOSTIC_NOT_ACCEPTANCE','column':51,'family':'prongs','family_column':column,'float64_fsum_dot_then_tanh_and_fsum':pooled,'dot_inputs_float64':pre,'linear_float32_gamma_n_bounds':dot_bounds,'note':'Linear-operation bounds only; not an adopted end-to-end tolerance or proof about the runtime tanh implementation.','numpy_version':np.__version__,'feature_shape':features.shape,'features_sha256':hashlib.sha256(features.tobytes()).hexdigest(),'weight_sha256':hashlib.sha256(encoder.weight.tobytes()).hexdigest()},indent=2))
