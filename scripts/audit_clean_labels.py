"""Executable checks behind docs/CLEAN-LABEL-AUDIT.md. Run from the repository root: PYTHONPATH=. python3 scripts/audit_clean_labels.py"""
import sys, os, tempfile
sys.dont_write_bytecode=True
from collections import OrderedDict
from repohandoff.tasks import TASK_BY_ID
def ns(tid):
    t=TASK_BY_ID[tid]; d={}
    exec(t.patch_clean[f'src/{t.module_name}.py'], d); return d
def run(label, f):
    try: print(f'  {label} -> {f()!r}')
    except Exception as e: print(f'  {label} -> RAISES {type(e).__name__}({e})')
n=ns('T25'); f=n['split_cents_exact']; print('T25')
run('split_cents_exact(1,[2**54,2**54+1])  # remainder ranking; exact answer [0, 1]', lambda:f(1,[2**54,2**54+1]))
for a in [(9007199254740995,[1]),(18014398509481986,[1]),(-100,[1,1,1]),(-1,[1,1]),(100,[0,0]),(10**18,[1,1,1]),(100,[1,1,1]),(10,[3,3,1])]:
    run(f'split_cents_exact{a} sum', lambda a=a:(f(*a), sum(f(*a)), a[0]))
n=ns('T05'); print('T05')
for u in ['https://example.org/\npath','https://ex\tample.org','https://example.org/\x00','https://exa mple.org','data:text/html,x','javascript:alert(1)','ftp://x.org']:
    run(f'is_safe_url({u!r})', lambda u=u:n['is_safe_url'](u))
run('sanitize_markdown_link("x","https://example.org/\\n")', lambda:n['sanitize_markdown_link']('x','https://example.org/\n'))
n=ns('T07'); f=n['expand_cron_field']; print('T07')
for a in [('5/2',0,10),('5/10',0,59),('-1',0,59),('-1-5',0,59),('60',0,59),('0-70',0,59),('1-5/2',0,59),('-5',-10,10)]:
    run(f'expand_cron_field{a}', lambda a=a:f(*a))
n=ns('T00'); f=n['allow_request']; print('T00')
run('allow_request([6.0],now=5.0,window=10.0,limit=1)', lambda:f([6.0],now=5.0,window=10.0,limit=1))
run('allow_request([-5.0],now=5.0,window=10.0,limit=1) (ts==cutoff)', lambda:f([-5.0],now=5.0,window=10.0,limit=1))
n=ns('T22'); print('T22')
def t22():
    c=OrderedDict([('cfg',1)]); r=n['lru_set'](c,'new',2,capacity=1,pinned={'cfg'}); return r, list(c), len(c)
run('all-pinned cap=1 insert', t22)
def t22b():
    c=OrderedDict(); r=n['lru_set'](c,'a',1,capacity=0); return r,list(c)
run('capacity=0 insert', t22b)
n=ns('T18'); print('T18'); run("check_tenant_access('','')", lambda:n['check_tenant_access']('',''))
run("check_tenant_access('t1','t2',{'tenant':'t2'},now=0) missing expires_at", lambda:n['check_tenant_access']('t1','t2',{'tenant':'t2'},now=0))
n=ns('T30'); print('T30'); run("mask_secret('abcd',0)", lambda:n['mask_secret']('abcd',0)); run("mask_secret('abcd',-1)", lambda:n['mask_secret']('abcd',-1))
n=ns('T13'); print('T13'); run('credit_with_tax_cents(-100,825) vs formula', lambda:(n['credit_with_tax_cents'](-100,825), -100+(-100*825)//10_000))
run('apply_credit_memo(1000,-500)', lambda:n['apply_credit_memo'](1000,-500))
n=ns('T11'); print('T11')
run("decode_cursor('40:é','s')", lambda:n['decode_cursor']('40:é','s'))
run("decode_cursor('²:abc','s')", lambda:n['decode_cursor']('²:abc','s'))
def t11():
    c=n['encode_cursor'](20,'s'); return n['decode_cursor']('21:'+c.split(':')[1],'s')
run('tampered offset', t11)
run("decode_cursor('-5:abc','s')", lambda:n['decode_cursor']('-5:abc','s'))
n=ns('T04'); print('T04')
for a in [1023,1024,2000,-3]: run(f'next_backoff({a})', lambda a=a:n['next_backoff'](a))
n=ns('T23'); f=n['keyset_page']; print('T23')
run('ids 2,10 equal score', lambda:[r['id'] for r in f([{'score':5,'id':2},{'score':5,'id':10}],5)])
run('after id 2 equal score', lambda:[r['id'] for r in f([{'score':5,'id':2},{'score':5,'id':10}],5,after_score=5,after_id=2)])
run('scores 10.1/a 10.9/b', lambda:[r['id'] for r in f([{'score':10.1,'id':'a'},{'score':10.9,'id':'b'}],5)])
n=ns('T15'); print('T15')
def t15():
    cnt=[0]
    def k(r): cnt[0]+=1; return cnt[0]%2
    rows=[{'v':i} for i in range(4)]
    return [r['v'] for r in n['deduplicate_rows'](rows,k,keep='last')], cnt[0]
run('stateful key_fn keep=last (rows, calls)', t15)
rows=[{"id":1,"v":"a"},{"id":2,"v":"b"},{"id":1,"v":"c"},{"id":2,"v":"d"}]
run('pure keep=last', lambda:[r['v'] for r in n['deduplicate_rows'](rows,lambda r:r['id'],keep='last')])
run('pure keep=first', lambda:[r['v'] for r in n['deduplicate_rows'](rows,lambda r:r['id'])])
n=ns('T20'); print('T20')
run("pick_highest_matching(['1.2.3','1.3.0-rc.1'])", lambda:n['pick_highest_matching'](['1.2.3','1.3.0-rc.1'],lambda v:True))
run("pick_highest_matching(['1.2.3+build.1'])", lambda:n['pick_highest_matching'](['1.2.3+build.1'],lambda v:True))
run("pick_highest_matching([])", lambda:n['pick_highest_matching']([],lambda v:True))
n=ns('T27'); print('T27')
run("parse_enum('',('Low','High'))", lambda:n['parse_enum']('',('Low','High')))
run("parse_enum_list('low,,high,',...)", lambda:n['parse_enum_list']('low,,high,',('Low','High')))
n=ns('T24'); print('T24'); run('retry_after_seconds(2.1,2.0)', lambda:n['retry_after_seconds'](2.1,2.0))
print('  "import math" in clean src:', 'import math' in TASK_BY_ID['T24'].patch_clean['src/retry_after.py'])
n=ns('T26'); print('T26')
run('ttl=0', lambda:n['check_and_record_nonce']({},'n',now=10.0,ttl=0.0))
run('ttl=-1', lambda:n['check_and_record_nonce']({},'n',now=10.0,ttl=-1.0))
n=ns('T09'); print('T09')
def t09():
    d=tempfile.mkdtemp(); root=os.path.join(d,'root'); out=os.path.join(d,'outside'); os.mkdir(root); os.mkdir(out)
    os.symlink(out, os.path.join(root,'link'))
    return str(n['safe_join'](root,'link/p')).replace(d,'<tmp>')
run('symlink root/link -> ../outside; safe_join(root,"link/p")', t09)
for p in ['a/.env','./a/../b','a\\.git\\x','/.hidden']: run(f'is_hidden_segment({p!r})', lambda p=p:n['is_hidden_segment'](p))
n=ns('T29'); print('T29')
run(r'truncate_log_lines("a\n",2)', lambda:n['truncate_log_lines']("a\n",2))
run(r'truncate_log_lines("a\r\nb",5)', lambda:n['truncate_log_lines']("a\r\nb",5))
n=ns('T17'); print('T17')
run("filter_attrs({'title':' hello '},{'title'})", lambda:n['filter_attrs']({'title':' hello '},{'title'}))
run("escape_html_text('&<>\"\\'')", lambda:n['escape_html_text']('&<>"\''))
