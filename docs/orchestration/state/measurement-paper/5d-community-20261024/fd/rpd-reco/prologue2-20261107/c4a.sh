set -euo pipefail
"$1" "$2/nd-unfolding/fd_rpd_inputs.py" check-mat-setup --r "$3"
set +u
source "$4"
set -u
echo "flags=$-"
set -o | grep -E "errexit|nounset|pipefail"
