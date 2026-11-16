# Bulk HPSS copy of LL5D's $U (package; DRAFT for the director and coverage-5b-audit)

$U is `/pscratch/sd/j/josephrb/ll5d-unfolds-r2`: 1759 files, 503,722,891 bytes. The director's rulings of 2026-11-16:
- (a) the pins of record are proposals 1-4 below;
- (b) the 97 atime sidecars are included;
- (c) it is one archive in four groups.
The kit is RSN's reviewed one (fd/referee-sensitivity-20261111/hpss/, kit rev 2; its run-20261112 printed `ARCHIVE
PASS`). Only its list and target change:
- `hpss_ll5d_u.template.sh` is `hpss_rsn.template.sh` (7aaa9a06) with five lines changed: OUT, H, W, GROUPS_IN_ORDER
  and N_ROWS (`template-vs-rsn-7aaa9a06.diff.txt`). Its header comments still describe RSN's run; the code is
  unchanged.
- `hpss_ll5d_u_launch.sh` is `hpss_rsn_launch.sh` (cd826dbd) with four lines changed: OUT, H, the list with its
  sha256, and the archive script with its sha256 (`launch-vs-rsn-cd826dbd.diff.txt`).
- `make_hpss_script.py` is byte-identical (d2f2a43a). `hpss_ll5d_u.sh` is the template with the list embedded; the
  list it extracts with its own sed equals `hpss_ll5d_u_list.tsv` byte for byte.

**The pins (`hpss_ll5d_u_list.tsv`, 1759 rows, sha256 980bb95e…).** `u_manifest.py` is a read-only manifest of $U,
run on login02 on 2026-11-16. It read every file by O_NOATIME and printed each file's sha256, size and atime before and
after (`u_manifest.raw.tsv.txt`): 1759 files, atime moved 0. `check_manifest.py` (`check_manifest.out.txt`, PASS)
then ties the manifest to the rulings before it becomes the list:
1. **null_roles (454):** each truth's products digest, made from the manifest exactly as ll5d_b.products_digest makes
   it, equals the null record's products_sha256: g18 c16e9ce0…, ar23 b716657b….
2. **extras (8):** the clipmean and data_control products. All 13 of the pilot's extras evidenced in
   bulk/evidence/extras-vs-pilot-r2.out.txt (these 8, plus 3 null-role and 2 toy products) equal the manifest.
3. **toys (1200)** and **4. sidecars (97):** the manifest is their pin of record. Each readout record watched 832 paths,
   its truth's 227 products and 600 toys among them, and none moved (receipts-ll5d/readout/README.md). The readout's
   1146-path atime-post covered the protected inputs, not $U's products (`products 1654 (in atime-pre: 0)`). Nothing
   has written $U since the bulk, and the manifest pass moved no atime.
The four groups partition all 1759 files. At run time the kit stages each file by O_NOATIME copy, and the bytes must
equal its pin, so for the toys and the sidecars two independent O_NOATIME reads must agree.

**What runs** (the director's go, on a login node via the launcher's survey, probe and archive modes): per group, the
O_NOATIME stage into /dev/shm (2 x the group's bytes + 256 MiB of headroom), then htar -Hcrc -Hverify=1, hsi
hashcreate and hashverify, then every member retrieved and re-hashed. The target is
`/home/j/josephrb/mnv-ll5d-unfolds-r2-20261116/` and must not exist beforehand. The output goes to
`/pscratch/sd/j/josephrb/hpss-ll5d-u-20261116/`. HPSS has about 51.7 GiB free (hpssquota, 2026-11-16) for about
0.5 GB. Nothing is deleted on pscratch or HPSS.

**CANNOT AUTHORIZE:** any removal of $U. That stays Joseph's, after this archive is verified.
