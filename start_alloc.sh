#!/bin/bash
# No args  -> interactive shell on a CPU node (original behaviour; `source start_alloc.sh`).
# With args -> run that command/options inside a fresh allocation (used by alloc_run.sh
#              to hold a detached, non-interactive allocation, e.g. `start_alloc.sh sleep 10800`).
salloc --nodes 1 --constraint cpu --time 180 --account m3246 --qos interactive "$@"
