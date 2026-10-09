import csv,sys,collections
for s in sys.argv[2:]:
    rows=list(csv.DictReader(open(f'{sys.argv[1]}/pairings_{s}.tsv'),delimiter='\t'))
    c=collections.Counter(r['outcome'] for r in rows)
    print(s,len(rows),dict(c))
    for o in ('DISPROVED','UNRESOLVED'):
        print('  ',o,[r['id'] for r in rows if r['outcome']==o])
