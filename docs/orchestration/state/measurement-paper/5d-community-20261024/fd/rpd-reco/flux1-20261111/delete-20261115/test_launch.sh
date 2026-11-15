#!/bin/bash
# Plumbing tests of flux1_cleanup_launch.sh on macOS. Shims (made in a temp dir): ssh drops its options and host and
# runs its last argument with bash, so the two hops run locally; sha256sum is shasum -a 256 if missing. The test copy
# of the launcher has /dev/shm replaced by a temp dir; the launcher and inventory script themselves are unchanged.
# The inventory refuses off a login node (rc 4), so case 1 checks the staging, the sha line, rc and the copy removal.
D=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d); mkdir -p "$T/shim" "$T/shm" "$T/run"
cat > "$T/shim/ssh" <<'S'
#!/bin/bash
while [ $# -gt 1 ]; do shift; done
exec bash -c "$1"
S
chmod +x "$T/shim/ssh"
command -v sha256sum >/dev/null || { printf '#!/bin/bash\nexec shasum -a 256 "$@"\n' > "$T/shim/sha256sum"; chmod +x "$T/shim/sha256sum"; }
cp "$D/flux1_inventory.py" "$T/run/"
sed "s#/dev/shm/#$T/shm/#" "$D/flux1_cleanup_launch.sh" > "$T/run/flux1_cleanup_launch.sh"
echo "## 1. plumbing: staged, sha checked on the node, script run, copy removed"
mkdir "$T/s1"; PATH="$T/shim:$PATH" bash "$T/run/flux1_cleanup_launch.sh" inventory "$T/s1" login05; echo "launcher rc=$?"
echo "   left in the /dev/shm stand-in: $(ls -A "$T/shm" | wc -l | tr -d ' ')"
echo "## 2. the local script altered: refused before any ssh"
cp "$D/flux1_inventory.py" "$T/run/flux1_inventory.py.orig"; echo "# x" >> "$T/run/flux1_inventory.py"
mkdir "$T/s2"; PATH="$T/shim:$PATH" bash "$T/run/flux1_cleanup_launch.sh" inventory "$T/s2" login05; echo "launcher rc=$?"
cp "$T/run/flux1_inventory.py.orig" "$T/run/flux1_inventory.py"
echo "## 3. a node name that is not a login node"
mkdir "$T/s3"; PATH="$T/shim:$PATH" bash "$T/run/flux1_cleanup_launch.sh" inventory "$T/s3" saul; echo "launcher rc=$?"
echo "## 4. a session dir that is not empty"
mkdir "$T/s4"; touch "$T/s4/x"; PATH="$T/shim:$PATH" bash "$T/run/flux1_cleanup_launch.sh" inventory "$T/s4" login05; echo "launcher rc=$?"
echo "## 5. a staged copy that differs on the node: the shim's cat appends a byte, so the node-side sha check must refuse"
printf '#!/bin/bash\n/bin/cat "$@"; printf x\n' > "$T/shim/cat"; chmod +x "$T/shim/cat"
mkdir "$T/s5"; PATH="$T/shim:$PATH" bash "$T/run/flux1_cleanup_launch.sh" inventory "$T/s5" login05; echo "launcher rc=$?"
echo "   left in the /dev/shm stand-in: $(ls -A "$T/shm" | wc -l | tr -d ' ')"
