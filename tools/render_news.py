"""Render verified data/news.json into the existing rubric pages (no network access)."""
from pathlib import Path
import json,html,re,sys
root=Path(__file__).resolve().parents[1]
categories=('aktuell','verkehr','termine','sport','genuss','wichtig','wetter','muell')
news=json.loads((root/'data/news.json').read_text(encoding='utf-8'))
seen=set()
for n in news:
 if not re.fullmatch(r'[a-z0-9-]+',n['id']) or n['id'] in seen: raise ValueError('Duplicate/invalid news ID')
 seen.add(n['id'])
 if not n['url'].startswith('https://') or not set(n['categories'])<=set(categories):raise ValueError('Invalid source/category')
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',n['checked']):raise ValueError('Invalid date')
 if n.get('valid_until') and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',n['valid_until']):raise ValueError('Invalid expiry')
def render(n):
 e=html.escape
 expiry=f' data-valid-until="{n["valid_until"]}"' if n.get('valid_until') else ''
 return f'<article class="news-entry" id="{n["id"]}"{expiry}><p class="news-meta">Quellenstand: {n["checked"]}</p><h2>{e(n["title"])}</h2><p class="expired-label" hidden>Archiv: Der angegebene Zeitraum ist abgelaufen.</p>'+''.join(f'<p>{e(p)}</p>' for p in n['paragraphs'])+f'<p class="source">Quelle: <a href="{e(n["url"],quote=True)}" target="_blank" rel="noopener">{e(n["source"])}</a></p></article>'
outputs={}
for slug in categories:
 path=root/(slug+'.html');text=path.read_text(encoding='utf-8')
 items=sorted((n for n in news if slug in n['categories']),key=lambda n:n['checked'],reverse=True)
 replacement='<div class="news-list">'+''.join(render(n) for n in items)+'</div><p class="editorial-note">'
 updated,count=re.subn(r'<div class="news-list">.*?</div><p class="editorial-note">',lambda m:replacement,text,flags=re.S)
 if count!=1:raise ValueError('Rubric template not found: '+slug)
 outputs[path]=updated
for path,text in outputs.items():path.write_text(text,encoding='utf-8',newline='\n')
print(f'Rendered {len(news)} verified entries in {len(outputs)} rubrics.')
