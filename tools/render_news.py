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
def datum_de(n):
    d = str(n.get("checked", ""))[:10]
    try: d = d[8:10] + "." + d[5:7] + "." + d[0:4]
    except Exception: pass
    z = str(n.get("zeit", "") or "")
    return d + (", " + z + " Uhr" if z else "")
WICON=[('gewitter','⛈️'),('schneeregen','🌨️'),('schnee','❄️'),('regen','🌧️'),('nebel','🌫️'),('wind','💨'),('bedeckt','☁️'),('bewölkt','⛅'),('wolkig','⛅'),('heiter','🌤️'),('sonn','☀️'),('klar','☀️'),('trocken','🌤️')]
def wetter_html(n):
 """Wetter-Vorhersage als übersichtliche Tageskarten statt Fließtext."""
 e=html.escape
 teile=[t.strip() for p in n['paragraphs'] for t in re.split(r'\s{2,}|\n',p) if t.strip()]
 tage=[];warn=[];rest=[]
 for t in teile:
  m=re.match(r'^(\w+), (\d{1,2}\.\d{1,2}\.): (.*)$',t)
  if m: tage.append(m.groups())
  elif re.search(r'WARNUNG|Warnung',t): warn.append(t)
  else: rest.append(t)
 if not tage: return None
 h='<div class="wt-tage">'
 for tag,dat,txt in tage:
  bits=[b.strip() for b in txt.split(',')]
  zust=bits[0] if bits else ''
  ico=next((i for k,i in WICON if k in zust.lower()),'🌦️')
  temp=next((b for b in bits if '°C' in b),'')
  regen=next((b for b in bits if 'Regenrisiko' in b),'')
  rm=re.search(r'(\d+)\s*%',regen); rl=re.search(r'ca\. ([\d,.]+) l/m²',regen)
  boe=next((b for b in bits if 'Böen' in b),'')
  h+=('<div class="wt-tag"><div class="wt-kopf"><b>'+e(tag)+'</b> '+e(dat)+'</div><div class="wt-ico" aria-hidden="true">'+ico+'</div>'
      '<div class="wt-zust">'+e(zust)+'</div><div class="wt-temp">'+e(temp.replace(' bis ',' – '))+'</div>'
      +('<div class="wt-regen">💧 '+e(rm.group(1))+' %'+(' · '+e(rl.group(1))+' l/m²' if rl else '')+'</div>' if rm else '')
      +('<div class="wt-boe">💨 '+e(boe)+'</div>' if boe else '')+'</div>')
 h+='</div>'
 from datetime import datetime,timedelta,date as _d
 try:
  from zoneinfo import ZoneInfo; jetzt=datetime.now(ZoneInfo('Europe/Berlin')).replace(tzinfo=None)
 except Exception: jetzt=datetime.now()
 WT={'Mo':0,'Di':1,'Mi':2,'Do':3,'Fr':4,'Sa':5,'So':6}
 def abgelaufen(w):
  # "(Di 20:00 bis Mi 10:00 Uhr)": Ende ab dem Einstell-Datum auf den Wochentag rechnen
  m=re.search(r'bis (Mo|Di|Mi|Do|Fr|Sa|So) (\d{1,2}):(\d{2})',w)
  if not m: return False
  try: start=_d.fromisoformat(n['checked'])
  except Exception: return False
  tage=(WT[m.group(1)]-start.weekday())%7
  ende=datetime(start.year,start.month,start.day,int(m.group(2)),int(m.group(3)))+timedelta(days=tage)
  return ende<jetzt
 warn=[w for w in warn if not abgelaufen(w)]
 for w in warn:
  w=re.sub(r'Amtliche WARNUNG vor ([A-ZÄÖÜ]+)',lambda m:'Amtliche Warnung vor '+m.group(1).capitalize(),w)
  h+='<p class="wt-warn">⚠️ '+e(w)+'</p>'
 h+=''.join('<p>'+e(r)+'</p>' for r in rest)
 return h
def rueck_html(n):
 e=html.escape; tag=[p for p in n['paragraphs'] if re.match(r'^(Mo|Di|Mi|Do|Fr|Sa|So), \d',p)]; rest=[p for p in n['paragraphs'] if p not in tag]
 if not tag: return None
 return ''.join('<p>'+e(p)+'</p>' for p in rest)+'<ul class="wt-liste">'+''.join('<li><b>'+e(p.split(': ',1)[0])+'</b><span>'+e(p.split(': ',1)[-1])+'</span></li>' for p in tag)+'</ul>'
def render(n):
 e=html.escape
 expiry=f' data-valid-until="{n["valid_until"]}"' if n.get('valid_until') else ''
 return f'<article class="news-entry" id="{n["id"]}"{expiry}><p class="news-meta">Eingestellt: {datum_de(n)}</p><h2>{e(re.sub(r"^WETTER · ","Wetter: ",n["title"]))}</h2><p class="expired-label" hidden>Archiv: Der angegebene Zeitraum ist abgelaufen.</p>'+((wetter_html(n) if n['id'].endswith('-wetter') else rueck_html(n) if n['id'].startswith('wetter-rueckblick') else None) or ''.join(f'<p>{e(p)}</p>' for p in n['paragraphs']))+f'<p class="source">Quelle: <a href="{e(n["url"],quote=True)}" target="_blank" rel="noopener">{e(n["source"])}</a>'+''.join(f' · <a href="{e(w["url"],quote=True)}" target="_blank" rel="noopener">{e(w["source"])}</a>' for w in n.get('weitere',[]) if str(w.get('url','')).startswith('https://'))+'</p><a class="nach-oben" href="#" aria-label="Nach oben">↑ nach oben</a></article>'
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
 return n['checked']  # tatsächliches Datum der Meldung (nicht das Datum der Übernahme)
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
