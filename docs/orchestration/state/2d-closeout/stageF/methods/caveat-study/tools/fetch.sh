#!/usr/bin/env bash
# fetch.sh ID... -- arXiv abs page and PDF for each ID into abs/ and pdf/, 3 s apart (read-only)
cd "${CAVEAT_WORK:?set CAVEAT_WORK to the scratch directory that holds abs/ and pdf/}"
for id in "$@"; do
  [ -s abs/$id.html ] || curl -sS -m 60 -A 'Mozilla/5.0 (read-only research)' -o abs/$id.html https://arxiv.org/abs/$id; sleep 3
  [ -s pdf/$id.pdf ] || curl -sSL -m 180 -A 'Mozilla/5.0 (read-only research)' -o pdf/$id.pdf https://arxiv.org/pdf/$id; sleep 3
  echo "$id abs=$(wc -c < abs/$id.html) pdf=$(wc -c < pdf/$id.pdf) $(file -b pdf/$id.pdf | cut -c1-20)"
done
