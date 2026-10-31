import re,sys
NUM=re.compile(r'^\d+\.\d+( [A-Z]{1,3})?$')
INTER=re.compile(r'^(Interlude|INTERLUDE)\b.{0,90}$')
OTHER=re.compile(r'^(S\d\d\s*[-–—]|Mini Stories|Story #\d|Wistram Days|Mating Rituals|Bonus|Side Story|Author.s Note|Note to Readers|Acknowledg|About the Author|More from the Innverse|Further Readin|Copyright Notice|Table of Contents|Contents$|Volume \d|The Wandering Inn, Book|BOOK \d)')
def heads(n):
    L=[l.rstrip('\r') for l in open(f'/home/claude/twi/books/b{n}.txt',encoding='utf-8').read().split('\n')]
    out=[]
    for i,l in enumerate(L):
        s=l.strip()
        if not s or len(s)>100: continue
        if NUM.match(s) or INTER.match(s) or OTHER.match(s): out.append((i,s))
    return L,out
for n in map(int,sys.argv[1:]):
    L,h=heads(n)
    print(f'=== b{n} ({len(L)} lines, {len(h)} heads)')
    for k,(i,s) in enumerate(h):
        j=h[k+1][0] if k+1<len(h) else len(L)
        w=sum(len(x.split()) for x in L[i+1:j] if x.strip() and x.strip()!='OceanofPDF.com')
        print(f'  L{i+1:>6} {w:>7}w  {s}')
