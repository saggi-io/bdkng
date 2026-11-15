"""Render verified data/news.json into the existing rubric pages (no network access)."""
from pathlib import Path
import json,html,re,sys
root=Path(__file__).resolve().parents[1]
categories=('aktuell','verkehr','termine','sport','genuss','wichtig','wetter','muell')
news=json.loads((root/'data/news.json').read_text(encoding='utf-8'))
seen=set()
for n in news:
 n['checked']=str(n['checked'])[:10]
 if n.get('valid_until'):n['valid_until']=str(n['valid_until'])[:10]
 if not re.fullmatch(r'[a-z0-9-]+',n['id']) or n['id'] in seen: raise ValueError('Duplicate/invalid news ID')
 seen.add(n['id'])
 if not n['url'].startswith('https://') or not set(n['categories'])<=set(categories):raise ValueError('Invalid source/category')
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',n['checked']):raise ValueError('Invalid date')
 if n.get('valid_until') and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',n['valid_until']):raise ValueError('Invalid expiry')
def render(n):
 e=html.escape
 expiry=f' data-valid-until="{n["valid_until"]}"' if n.get('valid_until') else ''
 return f'<article class="news-entry" id="{n["id"]}"{expiry}><p class="news-meta">Quellenstand: {n["checked"]}</p><h2>{e(n["title"])}</h2><p class="expired-label" hidden>Archiv: Der angegebene Zeitraum ist abgelaufen.</p>'+''.join(f'<p>{e(p)}</p>' for p in n['paragraphs'])+f'<p class="source">Quelle: <a href="{e(n["url"],quote=True)}" target="_blank" rel="noopener">{e(n["source"])}</a>'+''.join(f' · <a href="{e(w["url"],quote=True)}" target="_blank" rel="noopener">{e(w["source"])}</a>' for w in n.get('weitere',[]) if str(w.get('url','')).startswith('https://'))+'</p></article>'
outputs={}
for slug in categories:
 path=root/(slug+'.html');text=path.read_text(encoding='utf-8')
 if slug=='wichtig':
  # Wichtiges: eigene Einträge plus aktuelle Polizei-, Feuerwehr-, Warn- und Sperrungsmeldungen (letzte 7 Tage)
  from datetime import date,timedelta
  grenze=(date.today()-timedelta(days=7)).isoformat()
  WICHTIG=re.compile(r'(Polizei|Feuerwehr|Brand|Unfall|Vollsperrung|gesperrt|Warnung|Unwetter|Hochwasser|Störung|Stromausfall|Wasserrohrbruch|Evakuierung|Zeugen)',re.I)
  items=[n for n in news if 'wichtig' in n['categories'] or (n.get('valid_until') and n['checked']>=grenze and (WICHTIG.search(n['source']+' '+n['title'])))]  # statische Infoseiten (ohne valid_until) nicht als Meldung
 else:
  items=[n for n in news if slug in n['categories']]
 # Neueste zuerst; Quellen mischen, freie Quellen vor Bezahlangeboten (Echo+)
 rang={};pos={}
 for n in sorted(items,key=lambda n:n['checked'],reverse=True):
  k=(n['checked'],n['source'].split(' ·')[0]);rang[k]=rang.get(k,0)+1;pos[n['id']]=rang[k]
 from datetime import date as _d
 # Jede weitere Meldung derselben Quelle am selben Tag rutscht ca. ein Drittel Tag nach hinten -> gemischte Liste
 items=sorted(items,key=lambda n:_d.fromisoformat(n['checked']).toordinal()-0.6*(pos[n["id"]]-1)-(0.1 if '🔒' in n['source'] else 0),reverse=True)
 replacement='<div class="news-list">'+''.join(render(n) for n in items)+'</div><p class="editorial-note">'
 updated,count=re.subn(r'<div class="news-list">.*?</div><p class="editorial-note">',lambda m:replacement,text,flags=re.S)
 if count!=1:raise ValueError('Rubric template not found: '+slug)
 outputs[path]=updated
# Neueste Meldungen kompakt: alles vom neuesten Tag aus allen Rubriken (mind. 3 Meldungen, sonst Vortag dazu)
RUBRIK={'aktuell':'📰 Aktuelles','verkehr':'🚧 Verkehr','termine':'📅 Termine','sport':'⚽ Sport','genuss':'🍽️ Genuss','wichtig':'⚠️ Wichtig','wetter':'🌤️ Wetter','muell':'🗑️ Müll'}
def neu_am(n):
 m=re.search(r'(\d{4}-\d{2}-\d{2})',n['id']);return max(m.group(1) if m else n['checked'],n['checked'])
mitdatum=[n for n in news if n.get('valid_until')]
tage=sorted({neu_am(n) for n in mitdatum},reverse=True)
kompakt=[];gezeigt=[]
for tag in tage:
 kompakt+=[n for n in mitdatum if neu_am(n)==tag];gezeigt.append(tag)
 if len(kompakt)>=3 or len(gezeigt)>=2:break
def tagtext(t):
 from datetime import date as _dd
 d=_dd.fromisoformat(t);return ['Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag','Sonntag'][d.weekday()]+', '+d.strftime('%d.%m.%Y')
def render_k(n):
 return render(n).replace('<p class="news-meta">','<p class="news-meta"><span class="k-rubrik">'+RUBRIK.get(n['categories'][0],'📰')+'</span> · ',1)
kp=root/'kompakt.html'
if kp.exists():
 kt=kp.read_text(encoding='utf-8')
 block='<div class="news-list"><p class="k-tag">Stand: '+' und '.join(tagtext(t) for t in gezeigt)+' · '+str(len(kompakt))+' Meldungen</p>'+''.join(render_k(n) for n in kompakt)+'</div><p class="editorial-note">'
 kt,c=re.subn(r'<div class="news-list">.*?</div><p class="editorial-note">',lambda m:block,kt,flags=re.S)
 if c!=1:raise ValueError('kompakt template not found')
 outputs[kp]=kt
for path,text in outputs.items():path.write_text(text,encoding='utf-8',newline='\n')
print(f'Rendered {len(news)} verified entries in {len(outputs)} rubrics.')
