import sys, os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
B='/home/claude/bdkng'; FD=B+'/tools/fonts'
def F(n,s): return ImageFont.truetype(os.path.join(FD,n),s)
W,H,FPS=1080,1920,30
GR=(27,77,46); GOLD=(232,184,74); WH=(255,255,255); CR=(247,243,234)
hd=Image.open(B+'/assets/bdkng-header-jens.png').convert('RGB').crop((1150,40,2172,704))
r=H*1.12/hd.height; BG=hd.resize((int(hd.width*r),int(hd.height*r))).filter(ImageFilter.GaussianBlur(3))
logo=Image.open(B+'/assets/bdkng-logo-jens.png').convert('RGBA')
def ease(t): t=max(0,min(1,t)); return 1-(1-t)**3
def back(t,dur,dark):
    z=1+0.06*t/dur; w,h=int(W*1.0/z*1.0), int(H/z)
    x=int((BG.width-W)/2+40*math.sin(t*0.4)); y=int((BG.height-H)/2)
    im=BG.crop((x,y,x+W,y+H)).resize((W,H)) if False else BG.crop((x,y,x+W,y+H))
    ov=Image.new('RGB',(W,H),GR); return Image.blend(im,ov,dark)
def wrap(d,txt,font,maxw):
    out=[];l=''
    for w in txt.split():
        t=(l+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: l=t
        else: out.append(l); l=w
    out.append(l); return out
def frame(sc,t,T):
    dur=sc['d']; im=back(T,1,sc.get('dark',0.86)); d=ImageDraw.Draw(im)
    a=ease(t/sc.get('in',0.35))
    font=F('InterDisplay-Black.otf',sc['size']); lines=wrap(d,sc['txt'],font,W-140); lh=int(sc['size']*1.08)
    tot=lh*len(lines); y0=(H-tot)//2-60+int((1-a)*120)
    if sc.get('pop'): 
        s=0.7+0.3*a; font=F('InterDisplay-Black.otf',max(10,int(sc['size']*s))); lh=int(sc['size']*s*1.08); tot=lh*len(lines); y0=(H-tot)//2-60
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    for i,l in enumerate(lines):
        col=GOLD if i in sc.get('gold',[]) else WH
        ld.text((W//2,y0+i*lh),l,font=font,fill=col+(int(255*a),),anchor='ma')
    bw=int(ease((t-0.15)/0.5)*360); ld.rounded_rectangle([W//2-bw//2,y0+tot+40,W//2+bw//2,y0+tot+56],8,fill=GOLD+(255,))
    if sc.get('sub'):
        fs=F('Inter-Bold.otf',sc.get('subsize',54)); sa=ease((t-0.4)/0.4)
        for i,l in enumerate(wrap(ld,sc['sub'],fs,W-160)): ld.text((W//2,y0+tot+110+i*int(sc.get('subsize',54)*1.25)),l,font=fs,fill=CR+(int(255*sa),),anchor='ma')
    if sc.get('search'):
        q=sc['search']; n=int(len(q)*max(0,min(1,(t-0.3)/(dur*0.55))))
        bx=[90,y0-260,W-90,y0-120]; ld.rounded_rectangle(bx,70,fill=(255,255,255,240)); 
        ld.text((150,y0-190),q[:n]+('|' if int(t*3)%2==0 else ''),font=F('Inter-Bold.otf',50),fill=(28,33,30,255),anchor='lm')
    if sc.get('logo'):
        lg=logo.copy(); s=0.6+0.4*a; lg.thumbnail((int(620*s),int(400*s))); pad=Image.new('RGBA',(lg.width+60,lg.height+40),(255,255,255,int(245*a))); pad.paste(lg,(30,20),lg)
        lay.alpha_composite(pad,((W-pad.width)//2,y0-pad.height-90))
    if not sc.get('logo'):
        lg=logo.copy(); lg.thumbnail((200,120)); pad=Image.new('RGBA',(lg.width+30,lg.height+20),(255,255,255,235)); pad.paste(lg,(15,10),lg); lay.alpha_composite(pad,(W-pad.width-50,90))
    # Ausblenden
    fo=sc.get('out',0.2)
    if t>dur-fo: 
        k=(t-(dur-fo))/fo; lay.putalpha(lay.getchannel('A').point(lambda v:int(v*(1-k))))
    im=im.convert('RGBA'); im.alpha_composite(lay); return im.convert('RGB')
def render(scenes,out):
    tmp=out[:-4]+'.tmp.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',tmp],stdin=subprocess.PIPE)
    T=0
    for sc in scenes:
        for i in range(int(sc['d']*FPS)):
            p.stdin.write(frame(sc,i/FPS,T).tobytes()); T+=1/FPS
    p.stdin.close(); assert p.wait()==0; os.replace(tmp,out)
JUNG=[dict(d=1.6,txt='Was geht in Bad König?',size=150,gold=[1]),
 dict(d=0.8,txt='Müll?',size=230,pop=1,out=0.1,in_=0.2),dict(d=0.8,txt='Fußball?',size=210,pop=1,out=0.1),dict(d=0.8,txt='Party?',size=230,pop=1,out=0.1,gold=[0]),
 dict(d=1.4,txt='Frag einfach.',size=170,gold=[0]),
 dict(d=3.2,txt='Die BDKNG-KI antwortet.',size=120,search='Was geht am Wochenende?',sub='In Sekunden. Mit Quelle.',dark=0.9),
 dict(d=2.2,txt='News. Termine. Verkehr.',size=130,sub='Alles aus Bad König an einem Ort.'),
 dict(d=1.6,txt='Folg uns!',size=190,sub='WhatsApp · Instagram · TikTok',gold=[0]),
 dict(d=2.6,txt='bdkng.de',size=170,logo=1,sub='Dein Info-Kanal rund um Bad König',out=0.01)]
ALT=[dict(d=3,txt='Neues aus Bad König?',size=170,in_=0.6,out=0.4),
 dict(d=3,txt='Alles an einem Ort.',size=175,gold=[1],out=0.4),
 dict(d=3,txt='Müll, Termine, Wetter, Verkehr.',size=150,out=0.4),
 dict(d=3,txt='Einfach fragen. Sofort Antwort.',size=160,gold=[1],out=0.4),
 dict(d=3,txt='Notruf, Apotheke, Rathaus.',size=160,out=0.4),
 dict(d=3,txt='Kostenlos und ohne Werbung.',size=160,gold=[1],out=0.4),
 dict(d=3,txt='Im WhatsApp-Kanal folgen.',size=160,out=0.4),
 dict(d=3,txt='bdkng.de',size=190,logo=1,sub='Bad König kompakt',subsize=70,out=0.01)]
for s in ALT: s['in']=0.6
for s in JUNG: s.setdefault('in',0.3)
if __name__=='__main__':
    which=sys.argv[1]
    if which=='probe':
        for nm,sc,t in [('j6',JUNG[5],2.5),('a3',ALT[2],1.5),('a8',ALT[7],2),('j2',JUNG[1],0.6)]: frame(sc,t,1).save(f'/tmp/film/{nm}.jpg',quality=85)
    else: render(JUNG if which=='jung' else ALT,f'/tmp/film/bdkng-{which}.mp4')
