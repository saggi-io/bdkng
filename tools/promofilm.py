import sys, os, subprocess, math, random
from PIL import Image, ImageDraw, ImageFont
B='/home/claude/bdkng'; FD=B+'/tools/fonts'
def F(n,s): return ImageFont.truetype(os.path.join(FD,n),max(8,int(s)))
BLACK='InterDisplay-Black.otf'
W,H,FPS=1080,1920,30
GR=(27,77,46); GOLD=(232,184,74); WH=(255,255,255); DK=(16,32,22); CR=(247,243,234)
HEAD0=Image.open(B+'/assets/bdkng-header-jens.png').convert('RGB')
HEAD=HEAD0.crop((90,0,1790,724))
HH=480
def headimg():
    w=int(HEAD.width*HH/HEAD.height); im=HEAD.resize((w,HH)); x=(w-W)//2; return im.crop((x,0,x+W,HH))
def ease(t): t=max(0,min(1,t)); return 1-(1-t)**3
def back_out(t):
    t=max(0,min(1,t)); c1=1.70158; c3=c1+1; return 1+c3*(t-1)**3+c1*(t-1)**2
def wrap(d,txt,font,maxw):
    out=[];l=''
    for w in txt.split():
        t=(l+' '+w).strip()
        if d.textlength(t,font=font)<=maxw or not l: l=t
        else: out.append(l); l=w
    out.append(l); return out
def fit(d,txt,size,maxw,maxlines=4):
    while size>40:
        f=F(BLACK,size); L=wrap(d,txt,f,maxw)
        if len(L)<=maxlines and all(d.textlength(x,font=f)<=maxw for x in L): return f,L,size
        size-=6
    f=F(BLACK,size); return f,wrap(d,txt,f,maxw),size
def fit2(d,txt,size,maxw):
    parts=txt.split('\n')
    while size>40:
        f=F(BLACK,size); L=parts
        if all(d.textlength(x,font=f)<=maxw for x in L): return f,L,size
        size-=6
    return f,L,size
def pills(ld,y,a,size=58):
    f=F('Inter-Bold.otf',size); cols=[((37,211,102),'WhatsApp'),((225,48,108),'Instagram'),((24,119,242),'Facebook'),((20,20,20),'TikTok')]
    for i,(c,n) in enumerate(cols):
        k=ease((a-i*0.12)/0.4)
        if k<=0: continue
        w=ld.textlength(n,font=f)+90; x=W//2-w//2; yy=y+i*int(size*2.1)+int((1-k)*60)
        ld.rounded_rectangle([x,yy,x+w,yy+int(size*1.6)],int(size*0.8),fill=c+(int(255*k),),outline=(255,255,255,int(255*k)),width=3)
        ld.text((W//2,yy+int(size*0.8)),n,font=f,fill=(255,255,255,int(255*k)),anchor='mm')
# ---------- ALT: obere Drittel Header, darunter eine Farbe ----------
def alt_frame(txt,t,dur,last=False):
    im=Image.new('RGB',(W,H),GR); d=ImageDraw.Draw(im)
    im.paste(headimg(),(0,70)); d.rectangle([0,70+HH,W,70+HH+12],fill=GOLD)
    a=ease(t/0.6); fo=1 if last else min(1,max(0,(dur-t)/0.4))
    al=a*fo
    f,L,s=fit2(d,txt,190 if not last else 220,W-120)
    lh=int(s*1.1); tot=lh*len(L); top=70+HH+12; y0=top+(H-top-tot)//2-40+int((1-a)*60)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    for i,l in enumerate(L): ld.text((W//2,y0+i*lh),l,font=f,fill=(GOLD if last else WH)+(int(255*al),),anchor='ma')
    if last:
        fs=F('Inter-Bold.otf',64); ld.text((W//2,y0+tot+50),'Bad König kompakt',font=fs,fill=CR+(int(255*al),),anchor='ma')
    im=im.convert('RGBA'); im.alpha_composite(lay); return im.convert('RGB')
ALT=['Neues aus\nBad König?','Alles an\neinem Ort.','Müll\nTermine\nWetter\nVerkehr','CHAT','Sport\nVereine\nNeuigkeiten','SOCIAL','bdkng.de']
def alt_social(t,dur=3):
    im=Image.new('RGB',(W,H),GR); d=ImageDraw.Draw(im); im.paste(headimg(),(0,70)); d.rectangle([0,70+HH,W,70+HH+12],fill=GOLD)
    im=im.convert('RGBA'); lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    a=ease(t/0.6); ld.text((W//2,70+HH+110),'Folge uns',font=F(BLACK,170),fill=WH+(int(255*a),),anchor='ma'); pills(ld,70+HH+380,t-0.4,70)
    im.alpha_composite(lay); return im.convert('RGB')
def alt_chat(t,dur=5):
    im=Image.new('RGB',(W,H),GR); d=ImageDraw.Draw(im)
    hh=HH+40; im.paste(headimg(),(0,40))
    d.text((W//2,hh+90),'Frag die BDKNG-KI',font=F(BLACK,104),fill=GOLD,anchor='ma')
    f=F('Inter-Bold.otf',58); y=hh+230
    q='Was geht am Wochenende?'; n=int(len(q)*min(1,t/1.0))
    y=bubble(d,(0,y),q[:n] or ' ',f,GOLD,DK,True)
    if 1.1<t<1.6:
        for i in range(3): d.ellipse([90+i*56,y+20,126+i*56,y+56],fill=CR)
    if t>=1.6:
        for i,a in enumerate(['Sa 19 Uhr: Vortrag in der Rentmeisterei','Sa 15 Uhr: Fußball SG Bad König/Zell','So 14 Uhr: Handball HSG Odenwald']):
            if t>=1.6+i*0.5: y=bubble(d,(0,y),a,f,WH,DK,False)
    if t>3.2: d.text((W//2,H-180),'Sofort Antwort. Mit Quelle.',font=F(BLACK,72),fill=WH,anchor='ma')
    return im
# ---------- JUNG: Kinetic Type, harte Farbwechsel, Chat ----------
PAL=[(GOLD,DK),(DK,GOLD),(WH,GR),(GR,WH),((255,90,60),WH),((40,40,40),GOLD)]
def slam(words,t,bg,fg,size=240,stagger=0.18,rot=0):
    im=Image.new('RGB',(W,H),bg); lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    n=len(words); lh=int(size*1.02); y0=(H-lh*n)//2
    for i,w in enumerate(words):
        k=back_out((t-i*stagger)/0.28)
        if t<i*stagger: continue
        f,L,s=fit(ld,w,size,W-100,1); x=W//2+int((1-k)*(-W if i%2 else W))
        ld.text((x,y0+i*lh),w,font=f,fill=fg+(255,),anchor='ma')
    if rot: lay=lay.rotate(rot*math.sin(t*9)*max(0,1-t*2),resample=Image.BICUBIC)
    im=im.convert('RGBA'); im.alpha_composite(lay); return im.convert('RGB')
def pop(word,t,bg,fg,size=300):
    im=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(im)
    s=size*(0.4+0.6*back_out(t/0.22)); f=F(BLACK,s)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay); ld.text((W//2,H//2),word,font=f,fill=fg+(255,),anchor='mm')
    lay=lay.rotate(-6+4*math.sin(t*5),resample=Image.BICUBIC,center=(W//2,H//2))
    im=im.convert('RGBA'); im.alpha_composite(lay); return im.convert('RGB')
def bubble(d,xy,txt,f,bg,fg,right):
    x,y=xy; L=wrap(d,txt,f,700); lh=int(f.size*1.3); w=max(d.textlength(l,font=f) for l in L)+70; h=lh*len(L)+44
    x0=W-60-w if right else 60
    d.rounded_rectangle([x0,y,x0+w,y+h],44,fill=bg)
    for i,l in enumerate(L): d.text((x0+35,y+22+i*lh),l,font=f,fill=fg)
    return y+h+30
def chat(t):
    im=Image.new('RGB',(W,H),DK); d=ImageDraw.Draw(im)
    d.text((W//2,250),'Frag die BDKNG-KI',font=F(BLACK,96),fill=GOLD,anchor='ma')
    f=F('Inter-Bold.otf',54); y=520
    q='Was geht am Wochenende?'; n=int(len(q)*min(1,t/0.9))
    y=bubble(d,(0,y),q[:n] or ' ',f,GOLD,DK,True)
    if t>1.0 and t<1.5:
        for i in range(3): d.ellipse([90+i*50,y+20-int(10*abs(math.sin(t*10+i))),120+i*50,y+50-int(10*abs(math.sin(t*10+i)))],fill=CR)
    if t>=1.5:
        for i,a in enumerate(['Sa 19 Uhr: Vortrag in der Rentmeisterei','Sa 15 Uhr: Fußball SG Bad König/Zell','So 14 Uhr: Handball HSG Odenwald']):
            if t>=1.5+i*0.45: y=bubble(d,(0,y),a,f,WH,DK,False)
    if t>2.6: d.text((W//2,H-330),'In Sekunden. Mit Quelle.',font=F(BLACK,80),fill=WH,anchor='ma')
    return im
def folg(t):
    im=slam(['Folg','uns!'],t,(255,90,60),WH,230,0.15).convert('RGBA')
    im2=Image.new('RGB',(W,H),(255,90,60)); d2=ImageDraw.Draw(im2)
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    f=F(BLACK,200); k=back_out(t/0.3); ld.text((W//2,330+int((1-k)*-300)),'Folg uns!',font=f,fill=WH+(255,),anchor='ma')
    pills(ld,760,t-0.3,66)
    im2=im2.convert('RGBA'); im2.alpha_composite(lay); return im2.convert('RGB')
def endcard(t):
    im=Image.new('RGB',(W,H),GOLD); d=ImageDraw.Draw(im)
    k=back_out(t/0.4); hh=int(HEAD.height*W/HEAD.width); hd=HEAD.resize((W,hh))
    im.paste(hd,(0,int(560-(1-k)*700)))
    f=F(BLACK,190*min(1,0.5+k/2)); d.text((W//2,1120),'bdkng.de',font=f,fill=DK,anchor='ma')
    d.text((W//2,1360),'Dein Info-Kanal',font=F(BLACK,84),fill=GR,anchor='ma'); d.text((W//2,1460),'rund um Bad König',font=F(BLACK,84),fill=GR,anchor='ma')
    return im
JUNG=[(1.7,lambda t:slam(['WAS','GEHT IN','BAD','KÖNIG?'],t,GOLD,DK,250,0.2)),
 (0.7,lambda t:pop('Müll?',t,GR,WH)),(0.7,lambda t:pop('Fußball?',t,(255,90,60),WH,200)),(0.7,lambda t:pop('Events?',t,DK,GOLD,240)),
 (1.3,lambda t:slam(['Frag','einfach.'],t,WH,GR,260,0.25)),
 (3.6,chat),
 (1.8,lambda t:slam(['News','Termine','Verkehr'],t,GR,WH,230,0.3)),
 (2.2,lambda t:folg(t)),
 (2.5,endcard)]
def render(scenes,out):
    tmp=out[:-4]+'.tmp.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',tmp],stdin=subprocess.PIPE)
    for dur,fn in scenes:
        for i in range(int(round(dur*FPS))): p.stdin.write(fn(i/FPS).tobytes())
    p.stdin.close(); assert p.wait()==0; os.replace(tmp,out)
if __name__=='__main__':
    w=sys.argv[1]
    if w=='probe':
        fr=[JUNG[0][1](1.2),JUNG[2][1](0.4),JUNG[5][1](3.2),JUNG[8][1](2),alt_frame(ALT[2],1.5,3),alt_frame(ALT[7],2,3,True)]
        c=Image.new('RGB',(360*6,640));[c.paste(x.resize((360,640)),(i*360,0)) for i,x in enumerate(fr)];c.save('/tmp/film/probe2.jpg')
    elif w=='jung': render(JUNG,'/tmp/film/bdkng-jung.mp4')
    else:
        sc=[]
        for i,tx in enumerate(ALT):
            if tx=='CHAT': sc.append((5,alt_chat))
            elif tx=='SOCIAL': sc.append((3.5,lambda t:alt_social(t,3.5)))
            else: sc.append((3,(lambda tx,last:(lambda t:alt_frame(tx,t,3,last)))(tx,i==len(ALT)-1)))
        render(sc,'/tmp/film/bdkng-alt.mp4')
