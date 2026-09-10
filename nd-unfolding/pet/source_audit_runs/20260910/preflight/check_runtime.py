import json
import traceback
from pathlib import Path
import launch_typed_descriptor_source_audit as launcher
budget = launcher.RuntimeBudget()
result = {'kind': 'dependency_preflight_zero_source_opens', 'stages': []}
try:
 budget.install()
 for name in ('ROOT', 'tensorflow', 'keras'):
  module = __import__(name)
  status = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines())
  result['stages'].append({'module': name, 'version': getattr(module, '__version__', None), 'threads': int(status['Threads']), 'rss': status['VmRSS'], 'vmsize': status['VmSize']})
  budget.check()
 result['result'] = 'PASS'
except BaseException as error:
 result['result'] = 'BLOCKED'
 result['exception'] = {'type':type(error).__name__, 'message':str(error), 'traceback':traceback.format_exc()}
print(json.dumps(result, indent=2))
