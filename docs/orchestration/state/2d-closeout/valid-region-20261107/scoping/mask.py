import re,sys
# mask numbers not glued to an identifier (keeps H2, J88, R10, EW29, s5e, C_total); masks 0.36, +6.1, 153, 45
pat=re.compile(r'(?<![A-Za-z_0-9])[+\-−]?\d+(?:\.\d+)?')
W=int(sys.argv[1]) if len(sys.argv)>1 else 240
for line in sys.stdin:
    f,_,rest=line.partition(':'); l,_,t=rest.partition(':')
    print(f+':'+l+': '+pat.sub('#',t.rstrip('\n'))[:W])
