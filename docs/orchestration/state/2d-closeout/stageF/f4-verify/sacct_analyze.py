import collections, re, sys, json
rows=[l.rstrip('\n').split('|') for l in open('sacct_X.txt') if l.strip()]
P=[r for r in rows if r[1].startswith('2dc_P_')]
print('alloc rows 2dc_P_:', len(P), 'other names:', sorted(set(r[1][:12] for r in rows if not r[1].startswith('2dc_P_')))[:10])
def bill(t):
    m=re.search(r'billing=(\d+)',t); return int(m.group(1)) if m else None
ran=[r for r in P if r[5] not in ('None','Unknown','')]
nr=[r for r in P if r[5] in ('None','Unknown','')]
print('ran',len(ran),'never started',len(nr))
print('ran states',collections.Counter((r[3],r[10]) for r in ran))
print('never-started states',collections.Counter((r[3].split()[0],r[7]) for r in nr))
print('ran QOS',collections.Counter(r[2] for r in ran)); print('nr QOS',collections.Counter(r[2] for r in nr))
ch=0; byq=collections.defaultdict(float); badbill=[]
for r in P:
    b=bill(r[9]); e=int(r[7])
    if e and b is None: badbill.append(r[0])
    c=e*(b or 0)/256/3600; ch+=c; byq[(r[2], r[5] not in ('None','Unknown',''))]+=c
print('charge total %.4f'%ch, {k:round(v,4) for k,v in byq.items()}, 'badbill',badbill)
packs=[r for r in ran if r[1].startswith('2dc_P_K')]
print('K packs ran',len(packs), collections.Counter(r[2] for r in packs))
shared=[r for r in ran if r[2]=='shared']; print('shared ran', len(shared))
print('max End', max(r[6] for r in ran))
print('nr id range', min(int(r[0]) for r in nr), max(int(r[0]) for r in nr))
# steps
S=[l.rstrip('\n').split('|') for l in open('sacct_steps.txt') if l.strip()]
ids=set(r[0] for r in P)
st=[r for r in S if r[0].split('.')[0] in ids]
print('rows incl steps for 2dc_P_', len(st))
mem=[r for r in st if re.match(r'^\d+\.\d+$', r[0])]
print('numbered steps', len(mem), collections.Counter((r[3],r[7]) for r in mem))
allsteps=[r for r in st if '.' in r[0]]
print('all steps', len(allsteps), collections.Counter((r[3],r[7]) for r in allsteps))
# members in pack jobs only
pk=set(r[0] for r in packs)
pm=[r for r in mem if r[0].split('.')[0] in pk]
print('pack member steps', len(pm), 'elapsed', min(int(r[6]) for r in pm), max(int(r[6]) for r in pm))
# per class charges
cls=collections.defaultdict(lambda:[0,0.0,[]])
for r in packs:
    n=r[1]
    k='S4U' if 'S4U' in n else 'S4CV' if 'S4CV' in n else 'S1' if '_S1_' in n else 'S2' if '_S2_' in n else 'S4B' if 'S4B' in n else n
    if r[0]=='59860260': k='smoke'
    c=int(r[7])*bill(r[9])/256/3600; cls[k][0]+=1; cls[k][1]+=c; cls[k][2].append(int(r[7]))
for k,v in cls.items(): print(k, v[0], round(v[1],4), min(v[2]), max(v[2]))
cv=[r for r in packs if any(t in r[1] for t in ('_S1_','_S2_','S4B')) and r[0]!='59860260']
print('CV packs', len(cv), 'sum elapsed', sum(int(r[7]) for r in cv), round(sum(int(r[7]) for r in cv)/3600,4))
json.dump({'n_alloc':len(P),'ran':len(ran),'never':len(nr),'charge':ch},open('sacct_summary.json','w'))
