import subprocess,sys
W=sys.argv[1]; AT=sys.argv[2]
def g(*a): return subprocess.run(['git','-C',W,*a],capture_output=True,text=True,check=True).stdout
def blob(c,p):
    r=subprocess.run(['git','-C',W,'rev-parse','--verify','-q',f'{c}:{p}'],capture_output=True,text=True)
    return r.stdout.strip() or None
tips={'A':'cc9eed27','B':'c783d9c3','C':'57f6dd30','D':'ecb52dde'}
base='f8e2bf85'
for L,t in tips.items():
    cs=g('rev-list','--no-merges',f'{base}..{t}').split()
    files=set()
    for c in cs:
        files|=set(x for x in g('diff-tree','--no-commit-id','--name-only','-r',c).split('\n') if x)
    diff=[f for f in sorted(files) if blob(AT,f)!=blob(t,f)]
    print(L,t,'commits',len(cs),'files',len(files),'differ@',AT,len(diff),diff)
up=set(x for x in g('diff','--name-only','ad2716d8','460631d1').split('\n') if x)
up2=set()
for c in g('rev-list','--no-merges','ad2716d8..460631d1').split():
    up2|=set(x for x in g('diff-tree','--no-commit-id','--name-only','-r',c).split('\n') if x)
print('upstream net-diff files',len(up),'per-commit union',len(up2))
for name,U in (('net',up),('union',up2)):
    d=[f for f in sorted(U) if blob(AT,f)!=blob('460631d1',f)]
    print(name,'differ from 460631d1 at',AT,len(d),d[:30])
print('is ad2716d8 ancestor of 460631d1:',subprocess.run(['git','-C',W,'merge-base','--is-ancestor','ad2716d8','460631d1']).returncode==0)
