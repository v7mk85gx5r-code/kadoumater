import re, sys
F='/home/user/kadoumater/work/TOKYO_TEARDOWN_iPhone17_Enhanced.html'
class P:
    def __init__(self):
        self.t=open(F,encoding='utf-8').read(); self.n=0
    def rep(self,old,new,count=1):
        c=self.t.count(old)
        if c!=count:
            print('PATTERN COUNT MISMATCH (%d != %d):\n%s'%(c,count,old[:300])); sys.exit(1)
        self.t=self.t.replace(old,new); self.n+=1
    def rex(self,pattern,new,count=1,flags=re.S):
        m=re.findall(pattern,self.t,flags)
        if len(m)!=count:
            print('REGEX COUNT MISMATCH (%d != %d): %s'%(len(m),count,pattern[:200])); sys.exit(1)
        self.t=re.sub(pattern,lambda _m:new,self.t,flags=flags); self.n+=1
    def save(self):
        open(F,'w',encoding='utf-8').write(self.t); print('applied',self.n,'patches; size',len(self.t))
