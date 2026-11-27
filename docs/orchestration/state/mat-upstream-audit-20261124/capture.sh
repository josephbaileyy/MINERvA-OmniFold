#!/bin/bash
set -u
echo "# Raw upstream comparison outputs, captured $(date -u +%Y-%m-%dT%H:%M:%SZ) with gh api against public MinervaExpt repos."
echo "# Regenerate: bash capture.sh (the commands are echoed before each block)."
for r in MAT:35097b65ab1680db8058f9ede18fecffdc3a1ea3 MAT-MINERvA:50d7631416d1c93edd4db6886a2ca29da64fee60; do repo=${r%%:*}; sha=${r#*:}
 echo; echo "## $repo: pin $sha vs main"
 echo "\$ gh api repos/MinervaExpt/$repo/commits/$sha"
 gh api repos/MinervaExpt/$repo/commits/$sha --jq '"pin "+.sha+" "+.commit.committer.date+" "+(.commit.message|split("\n")[0])'
 echo "\$ gh api repos/MinervaExpt/$repo/compare/$sha...main"
 gh api repos/MinervaExpt/$repo/compare/$sha...main --jq '("status="+.status+" ahead_by="+(.ahead_by|tostring)+" behind_by="+(.behind_by|tostring)), (.commits[]|.sha+" "+.commit.committer.date[0:10]+" "+(.commit.message|split("\n")[0]|.[0:140]))'
done
for r in MINERvA-101-Cross-Section UnfoldUtils GENIEXSecExtract; do
 echo; echo "## $r: no pin recorded in this repo; main commits since 2025-06-01"
 echo "\$ gh api 'repos/MinervaExpt/$r/commits?since=2025-06-01T00:00:00Z&per_page=50'"
 gh api "repos/MinervaExpt/$r/commits?since=2025-06-01T00:00:00Z&per_page=50" --jq '.[]|.sha+" "+.commit.committer.date[0:10]+" "+(.commit.message|split("\n")[0]|.[0:140])'
done
echo; echo "## UnfoldUtils: f9099cd3...a2bbe41c changed files"
echo "\$ gh api repos/MinervaExpt/UnfoldUtils/compare/f9099cd3...a2bbe41c"
gh api repos/MinervaExpt/UnfoldUtils/compare/f9099cd3...a2bbe41c --jq '.files[]|.filename+" +"+(.additions|tostring)+" -"+(.deletions|tostring)'
for x in MAT-MINERvA:3e411c0d MAT-MINERvA:5bf46c53 MAT-MINERvA:c20ad220 MINERvA-101-Cross-Section:48a52760 MINERvA-101-Cross-Section:85b3d5fe; do repo=${x%%:*}; c=${x#*:}
 echo; echo "## $repo $c"; echo "\$ gh api repos/MinervaExpt/$repo/commits/$c"
 if [ "$c" = 5bf46c53 ] || [ "$c" = c20ad220 ]; then
  gh api repos/MinervaExpt/$repo/commits/$c --jq '("sha "+.sha+" author "+.commit.author.name+" committed "+.commit.committer.date), (.files[]|"--- "+.filename+" +"+(.additions|tostring)+" -"+(.deletions|tostring))'
 else
  gh api repos/MinervaExpt/$repo/commits/$c --jq '("sha "+.sha+" author "+.commit.author.name+" authored "+.commit.author.date+" committed "+.commit.committer.date), (.files[]|"--- "+.filename+"\n"+(.patch//""))'
 fi
done
echo; echo "## MAT branches: newest commit per branch"
gh api repos/MinervaExpt/MAT/branches --jq '.[].name' | while read b; do gh api "repos/MinervaExpt/MAT/commits?sha=$b&per_page=1" --jq ".[0]|.commit.committer.date[0:10]+\" $b \"+.sha"; done | sort -r
