python3(){ echo "CMD $*"; }
uomni_check(){ :; }; p1_check(){ :; }; cv_check(){ :; }; sha256sum(){ :; }
CVOMNI=CVO; UOMNI=UO; FLUXU=FU; MCFILE=MC; OUT=O; ACT=/nonexistent
BASE=(B); UNIV=(--omnifile UO --flux-universe-file FU --verbose)
awk(){ echo 0000000000000000000000000000000000000000000000000000000000000000; }
while read -r NAME; do
  echo "== $NAME"
  source "$CASE"
done
