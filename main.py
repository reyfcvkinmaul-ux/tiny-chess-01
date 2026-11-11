import os,json,urllib.request,urllib.error
U=os.environ['MAKEFUN_ENV_URL'];V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0};D=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)];K=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)];N=[(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]
def post(p,x):
 req=urllib.request.Request(U+p,data=json.dumps(x).encode(),headers={'content-type':'application/json'})
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
def parse(f):
 a=[];q=f.split()[0]
 for y,row in enumerate(q.split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:a.append((y*8+x,c));x+=1
 return dict(a)
def fenboard(f):
 b=[' ']*128
 for y,row in enumerate(f.split()[0].split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:b[y*16+x]=c;x+=1
 return b
def sq(s):return (8-int(s[1]))*16+ord(s[0])-97
def name(x):return chr(x%16+97)+str(8-x//16)
def pseudo(b,white):
 z=[]; own='PNBRQK' if white else 'pnbrqk'; opp='pnbrqk' if white else 'PNBRQK'
 for x,p in enumerate(b):
  if p not in own:continue
  u=p.lower()
  if u=='p':
   d=-16 if white else 16; r=x//16
   if 0<=x+d<128 and b[x+d]==' ':
    z += [(x,x+d,c) for c in ('q','r','b','n') if (x+d)//16 in (0,7)] or [(x,x+d,'')]
    if (r==6 if white else r==1) and b[x+2*d]==' ':z.append((x,x+2*d,''))
   for e in (d-1,d+1):
    if 0<=x+e<128 and b[x+e] in opp:z += [(x,x+e,c) for c in ('q','r','b','n') if (x+e)//16 in (0,7)] or [(x,x+e,'')]
  elif u=='n':
   for dx,dy in N:
    y,x2=x//16+x//16*0+dy,x%16+dx; t=y*16+x2
    if 0<=t<128 and x2 in range(8) and b[t] not in own:z.append((x,t,''))
  elif u=='k':
   for dx,dy in K:
    y,x2=x//16+dy,x%16+dx;t=y*16+x2
    if 0<=t<128 and x2 in range(8) and b[t] not in own:z.append((x,t,''))
  else:
   ds=K if u=='q' else D if u=='r' else [(1,1),(1,-1),(-1,1),(-1,-1)]
   for dx,dy in ds:
    y,x2=x//16+dy,x%16+dx
    while 0<=y<8 and 0<=x2<8:
     t=y*16+x2
     if b[t]==' ':z.append((x,t,''))
     else:
      if b[t] in opp:z.append((x,t,''))
      break
     if u=='k':break
     y+=dy;x2+=dx
 return z
def attack(b,x,bywhite):
 return any(a==x for a,c,p in pseudo(b,bywhite))
def legal(b,w):
 out=[]
 for a,c,p in pseudo(b,w):
  old=b[c];b[c]=b[a];b[a]=' '
  k=next((i for i,v in enumerate(b) if v==('K' if w else 'k')),None)
  bad=attack(b,k,not w);b[a]=b[c];b[c]=old
  if not bad:out.append((a,c,p))
 return out
def mv(t):
 a,c,p=t;return name(a)+name(c)+(p or '')
def score(b):return sum((V.get(x.lower(),0)*(1 if x.isupper() else -1)) for x in b)
def go(b,w,d,al=-10**9,be=10**9):
 z=legal(b,w)
 if not z:return (-10**6 if attack(b,next((i for i,v in enumerate(b) if v==('K' if w else 'k')),0),not w) else 0),None
 if d<1:return (score(b)*(1 if w else -1)),None
 best=-10**9;bm=None
 for a,c,p in z:
  o=b[c];b[c]=b[a];b[a]=' '
  if p:b[c]=p.upper() if w else p
  v=-go(b,not w,d-1,-be,-al)[0]
  b[a]=b[c];b[c]=o
  if v>best:best,bm=v,(a,c,p)
  al=max(al,v)
  if al>=be:break
 return best,bm
def choose(g):
 b=fenboard(g['fen']);w=g['fen'].split()[1]=='w';z=legal(b,w)
 if not z:return g['legal_moves'][0]
 best=(-10**9,z[0])
 for t in z:
  a,c,p=t;o=b[c];b[c]=b[a];b[a]=' '
  if p:b[c]=p.upper() if w else p
  v=-go(b,not w,2)[0]
  b[a]=b[c];b[c]=o
  if v>best[0]:best=(v,t)
 m=mv(best[1]);return m if m in g['legal_moves'] else g['legal_moves'][0]
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g)})
