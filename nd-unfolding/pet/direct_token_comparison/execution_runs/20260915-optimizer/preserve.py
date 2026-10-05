"""Preserve closed optimizer diagnostic files and verify independent readback."""
from pathlib import Path
import hashlib
import json
import resource
import shutil
import tarfile
import time

started = time.monotonic()
source = Path('/pscratch/sd/j/josephrb/pet-optimizer-output-20260915')
destination = Path('/global/cfs/cdirs/m3246/josephrb/pet-routing-comparison/20260915-optimizer-58320923')
def inventory(root):
    return {str(p.relative_to(root)): {'bytes':p.stat().st_size, 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file()}
before = inventory(source)
assert sum(x['bytes'] for x in before.values()) <= 1024**3
assert not destination.exists()
destination.mkdir(parents=True)
shutil.copytree(source, destination/'payload')
shutil.copyfile('/pscratch/sd/j/josephrb/pet-optimizer-20260915.slurm.log',destination/'slurm.log')
assert before == inventory(source) == inventory(destination/'payload')
archive = destination/'payload.tar.gz'
with tarfile.open(archive,'w:gz') as stream:
    for name in before: stream.add(destination/'payload'/name,arcname=name,recursive=False)
with tarfile.open(archive) as stream:
    readback={member.name:{'bytes':member.size,'sha256':hashlib.sha256(stream.extractfile(member).read()).hexdigest()} for member in stream if member.isfile()}
assert readback == before
usage=resource.getrusage(resource.RUSAGE_SELF)
receipt={'job_id':'58320923','source':str(source),'destination':str(destination/'payload'),'files':before,'file_count':len(before),'bytes':sum(x['bytes'] for x in before.values()),'readback_exact':True,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'slurm_log_sha256':hashlib.sha256((destination/'slurm.log').read_bytes()).hexdigest(),'wall_seconds':time.monotonic()-started,'preservation_cpu_seconds':usage.ru_utime+usage.ru_stime}
(destination/'preservation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'},indent=2))
