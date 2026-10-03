# claude.ai のアーティファクト用：文書の骨格（doctype/html/head/body）は公開側で付くので外し、配色だけ補う
import re
SRC='/home/user/kadoumater/work/TOKYO_TEARDOWN_PC.html'
OUT='/tmp/claude-0/-home-user-kadoumater/f5a7295b-5052-559c-a72f-ff94e409391f/scratchpad/tokyo_teardown_pc.html'
t=open(SRC,encoding='utf-8').read()
head=t[t.index('<head>')+6:t.index('</head>')]
body=t[t.index('<body>')+6:t.index('</body>')]
head=re.sub(r'<meta[^>]*>\s*','',head)
head=head.replace('<title>TOKYO TEARDOWN PC — 東京解体</title>','<title>TOKYO TEARDOWN PC</title>')
head=head.replace(':root{\n  --ink:',':root{\n  color-scheme:dark;\n  --ink:',1)
head=head.replace('html,body{margin:0;height:100%;overflow:hidden;background:#05070c;}','html,body{margin:0;padding:0;height:100%;overflow:hidden;background:#05070c;}')
out=head.strip()+'\n'+body.strip()+'\n'
open(OUT,'w',encoding='utf-8').write(out)
print('artifact variant',len(out))
