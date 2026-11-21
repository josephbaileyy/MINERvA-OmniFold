#!/bin/bash
# Test of t3p_submit.sh's clean_check (rev 2): a clean deploy and ignored __pycache__/ pass; an ignored non-__pycache__
# file, a tracked change and an untracked file each refuse. Extracts the function from the script itself.
# Usage: bash test_clean_check.sh   (exit 0 only if all five cases read as declared)
HERE=$(cd "$(dirname "$0")" && pwd)
S=$(mktemp -d); trap 'rm -rf -- "$S"' EXIT
cd "$S" && git init -q r && cd r || exit 2
printf '__pycache__/\n*.log\n' > .gitignore; mkdir -p a/__pycache__; echo x > a/f.py
git add -A && git -c user.name=t -c user.email=t@t commit -qm i || exit 2
D=$S/r
eval "$(sed -n '/^clean_check() {/,/^}/p' "$HERE/t3p_submit.sh")"
fail=0
want() { local name=$1 exp=$2; clean_check > /dev/null; local rc=$?; local got=$([ $rc -eq 0 ] && echo pass || echo refuse)
  echo "$name: $got (want $exp)"; [ "$got" = "$exp" ] || fail=1; }
want clean pass
touch a/__pycache__/f.cpython-311.pyc; want ignored-pycache pass
touch x.log; want ignored-other refuse; rm x.log
echo y >> a/f.py; want tracked-change refuse; git checkout -q a/f.py
touch new.txt; want untracked refuse; rm new.txt
exit $fail
