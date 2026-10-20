#!/bin/bash
# SF-1 charge ledger: every SF-1 job id from sacct, charged CPU node-h = ElapsedRaw/3600 * billing/256 * qos_factor
# (the s5p meter's formula, nd-unfolding/s5c_meter.py: CPU node billing 256, regular qos_factor 1.0).
# usage: ledger.sh <jobid,jobid,...>
JOBS=${1:?job ids}
sacct -X -P -n -j "$JOBS" --format=JobID,JobName%30,QOS,State,Submit,Start,End,Elapsed,ElapsedRaw,NNodes,AllocTRES%80 |
awk -F'|' 'BEGIN{OFS="|"; print "JobID|JobName|QOS|State|Submit|Start|End|Elapsed|ElapsedRaw|NNodes|billing|charged_node_h"}
{b=0; if (match($11, /billing=[0-9]+/)) b=substr($11, RSTART+8, RLENGTH-8); c=$9/3600*b/256; tot+=c;
 print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,b,sprintf("%.4f",c)} END{printf "TOTAL charged_node_h %.4f\n", tot}'
