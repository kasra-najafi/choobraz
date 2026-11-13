"""Build the corrected three-page design 74 and append it to the catalog.
Dependencies: reportlab, pymupdf, pillow, arabic-reshaper, python-bidi.
The reference has a lateral sliding panel and a stationary rear-right lockbox.
Dimensions are parameters to measure on site, not numbers recovered from video.
"""
import io, json, math, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'tmp/pythondeps'))
import fitz, arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
W,H=595.92,842.88
INK='#171717'; ORANGE='#ec9d50'; YELLOW='#fff1ad'; BLUE='#274cff'; BROWN='#b84b19'
TITLE='باکس مخفی ریلی کابینت'; EN='Sliding Cabinet Lockbox'
SOURCE='https://www.instagram.com/reel/DffrLOMox3m/'
for n,f in [('Fa','DejaVuSans.ttf'),('FaB','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
def shape(s):return get_display(arabic_reshaper.reshape(str(s)))
def rect(c,x,y,w,h,fill=None,stroke='#777777',lw=.55):
    c.setLineWidth(lw);c.setStrokeColor(HexColor(stroke or '#ffffff'));c.setFillColor(HexColor(fill or '#ffffff'))
    c.rect(x,H-y-h,w,h,stroke=int(stroke is not None),fill=int(fill is not None))
def line(c,x,y,xx,yy,color=INK,lw=.6,dash=None):
    c.setStrokeColor(HexColor(color));c.setLineWidth(lw);c.setDash(dash or []);c.line(x,H-y,xx,H-yy);c.setDash([])
def poly(c,pts,fill=None,stroke=INK):
    p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
    for x,y in pts[1:]:p.lineTo(x,H-y)
    p.close();c.setLineWidth(.6);c.setStrokeColor(HexColor(stroke));c.setFillColor(HexColor(fill or '#ffffff'));c.drawPath(p,stroke=1,fill=bool(fill))
def rtl(c,s,x,y,size=9,bold=False,color=INK,center=False):
    c.setFont('FaB' if bold else 'Fa',size);c.setFillColor(HexColor(color));(c.drawCentredString if center else c.drawRightString)(x,H-y,shape(s))
def en(c,s,x,y,size=9,bold=False,color=INK,center=False):
    c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.setFillColor(HexColor(color));(c.drawCentredString if center else c.drawString)(x,H-y,s)
def wrap(c,s,x,y,width,size=8,leading=13):
    buf=''
    for word in s.split():
        test=(buf+' '+word).strip()
        if buf and pdfmetrics.stringWidth(shape(test),'Fa',size)>width:rtl(c,buf,x,y,size);y+=leading;buf=word
        else:buf=test
    if buf:rtl(c,buf,x,y,size);y+=leading
    return y
def heading(c,s,y,x=35,width=526):rtl(c,s,x+width,y,9.3,True);line(c,x,y+6,x+width,y+6,lw=.7)
def header(c):
    rect(c,35,29,526,45,'#ffffff',INK,1);rect(c,35,29,66,45,'#111111',None)
    en(c,'A-20',68,57,17,True,'#ffffff',True);line(c,172,29,172,74)
    rtl(c,'مخفی بودن',136,44,6.5,center=True)
    for i in range(5):
        c.setStrokeColor(HexColor(BROWN));c.setFillColor(HexColor(BROWN if i>=3 else '#ffffff'));c.circle(114+i*10,H-58,3.7,fill=1,stroke=1)
    rtl(c,'برآورد',136,69,5.3,color='#777777',center=True)
    rtl(c,TITLE,480,49,12.4,True);c.setFont('Helvetica',9);c.setFillColor(HexColor('#555555'));c.drawRightString(480,H-65,EN)
    rtl(c,'برگ',529,44,7,center=True);rtl(c,'۷۴ از ۷۴',529,61,10,True,center=True)
def footer(c,kind):
    line(c,35,811,561,811,'#888888',.5);en(c,'A-20 / 74 / '+kind,35,825,6.5,color='#666666')
    rtl(c,'ابعاد به میلی‌متر؛ شماتیک بدون مقیاس؛ ابعاد واقعی از ویدیو قابل تأیید نیست.',561,825,6.1,color='#666666')
def arrow(c,x,y,xx,yy,label=None):
    line(c,x,y,xx,yy,BLUE,1.1);a=math.atan2(yy-y,xx-x)
    poly(c,[(xx,yy),(xx-5*math.cos(a-.5),yy-5*math.sin(a-.5)),(xx-5*math.cos(a+.5),yy-5*math.sin(a+.5))],BLUE,BLUE)
    if label:rtl(c,label,(x+xx)/2,y-8,8,True,BLUE,True)
def hatch(c,x,y,w,h):
    rect(c,x,y,w,h,'#eeeeee',INK,.5);c.saveState();p=c.beginPath();p.rect(x,H-y-h,w,h);c.clipPath(p,stroke=0,fill=0)
    for z in range(-math.ceil(h),math.ceil(w),5):line(c,x+z,y+h,x+z+h,y,'#888888',.25)
    c.restoreState()
def rail(c,x,y,w):
    rect(c,x,y,w,7,'#c5c5c5',INK,.5);line(c,x+2,y+3.5,x+w-2,y+3.5,'#555555',.65)
    for xx in (x+6,x+w/2,x+w-6):c.setFillColor(HexColor('#333333'));c.circle(xx,H-y-3.5,.85,fill=1,stroke=0)
def num(c,n,x,y,tx,ty):
    line(c,x,y,tx,ty,'#555555',.45);c.setFillColor(HexColor('#ffffff'));c.setStrokeColor(HexColor(INK));c.circle(x,H-y,6,fill=1,stroke=1);en(c,str(n),x,y+2.5,7.5,center=True)
def dimh(c,x,xx,y,sy,s):
    for z in (x,xx):line(c,z,sy,z,y+3,BLUE,.4);line(c,z-2,y+3,z+2,y-3,BLUE,.5)
    line(c,x,y,xx,y,BLUE,.45);en(c,s,(x+xx)/2,y-4,8,True,BLUE,True)
def dimv(c,y,yy,x,sx,s):
    for z in (y,yy):line(c,sx,z,x-3,z,BLUE,.4);line(c,x-3,z+2,x+3,z-2,BLUE,.5)
    line(c,x,y,x,yy,BLUE,.45);c.saveState();c.translate(x-5,H-(y+yy)/2);c.rotate(90);c.setFont('Helvetica-Bold',8);c.setFillColor(HexColor(BLUE));c.drawCentredString(0,0,s);c.restoreState()
def tag(c,s,x,y,w,tx,ty):
    line(c,x+w/2,y+14,tx,ty,BLUE,.5);rect(c,x,y,w,15,'#ffffff',BLUE,.55);rtl(c,s,x+w/2,y+10.5,7.3,center=True)
def iso(c,x,y,w,h,d,opened=False):
    poly(c,[(x,y),(x+d,y-d*.5),(x+w+d,y-d*.5),(x+w,y)],'#d7d7d2')
    poly(c,[(x+w,y),(x+w+d,y-d*.5),(x+w+d,y+h-d*.5),(x+w,y+h)],'#bcbcb5');rect(c,x,y,w,h,'#f3f3ef',INK,.7)
    if not opened:
        rect(c,x+5,y+5,w/2-6,h-10,'#e1e1db',INK,.65);rect(c,x+w/2+1,y+5,w/2-6,h-10,'#e1e1db',INK,.65);return
    rect(c,x+7,y+7,w-14,h-14,'#e9e9e3',INK,.55);rx,ry,rw,rh=x+21,y+16,w-34,h-28
    rect(c,rx+rw*.51,ry+12,rw*.46,rh-24,YELLOW,INK,.6);rail(c,rx,ry,rw);rail(c,rx,ry+rh-7,rw);rect(c,rx,ry+1,rw*.51,rh-2,ORANGE,INK,.7)
    poly(c,[(x,y+4),(x-35,y+21),(x-35,y+h+17),(x,y+h-4)],'#e4e4de')
    poly(c,[(x+w,y+4),(x+w+44,y+24),(x+w+44,y+h+20),(x+w,y+h-4)],'#e4e4de')
    ix=rx+rw*.97;top=ry+12;bottom=ry+rh-12
    poly(c,[(ix,top),(ix+27,top+17),(ix+27,bottom+17),(ix,bottom)],'#e1e1db')
    rect(c,ix-2,top+18,5,6,'#555555');rect(c,ix-2,bottom-23,5,6,'#555555');c.setFillColor(HexColor('#666666'));c.circle(ix+22,H-(top+bottom)/2-14,2,fill=1,stroke=0)
def photo(c):
    im=Image.open(ROOT/'full-074.jpg');ww,hh=im.size;scale=min((W-48)/ww,(H-82)/hh);dw,dh=ww*scale,hh*scale
    c.drawImage(str(ROOT/'full-074.jpg'),(W-dw)/2,58+(H-82-dh)/2,width=dw,height=dh)
    rtl(c,'بازسازی واقع‌نما؛ سازوکار از ویدیوی مرجع، ابعاد از محل تعیین می‌شود.',W/2,H-40,7.5,color='#756d62',center=True)
    line(c,28,H-30,W-28,H-30,'#ddd4c6',.45);rtl(c,'چوب‌راز | کاتالوگ محفظه‌های مخفی',W-28,H-14,7,color='#756d62');en(c,'74 / A-20',28,H-14,8,color='#756d62');c.showPage()
def schematic(c):
    header(c)
    for y,label,x,w in [(83,'۱ · نمای سه‌بعدی بسته: درهای معمولی کابینت',267,285),(417,'۲ · نمای سه‌بعدی باز: پنل به چپ، محفظهٔ ثابت در راست',214,338)]:
        rect(c,35,y,526,326);rect(c,x,y+5,w,15,'#151515',None);rtl(c,label,547,y+16,8.1,True,'#ffffff')
    iso(c,155,156,255,168,40);tag(c,'دو درِ عادی؛ قفل مخفی دیده نمی‌شود',312,355,208,350,248)
    iso(c,130,488,285,174,34,True);arrow(c,270,479,180,479,'لغزش افقی به چپ')
    tag(c,'پنل پوشاننده پس از کنار رفتن',48,697,175,220,578);tag(c,'محفظهٔ ثابت با درِ قفل‌دار',349,701,194,355,586)
    rtl(c,'طبقاتِ جداشونده پیش از جابه‌جایی پنل برداشته می‌شوند.',298,769,8.5,center=True)
    for x,color,s in [(499,ORANGE,'قطعهٔ متحرک'),(337,YELLOW,'فضای محفظه'),(177,'#bdbdbd','بدنه و درها')]:rect(c,x,783,13,8,color);rtl(c,s,x-7,790,7)
    footer(c,'schematic');c.showPage()
def technical(c):
    header(c);rect(c,35,83,526,46);line(c,177,83,177,129);line(c,346,83,346,129)
    for x,title,text,size in [(551,'محل نصب','داخل کابینت یا کمد؛ پشت بخش سمت راست',8),(336,'ظرفیت','تابع ابعاد محفظه؛ مدارک و اشیای کوچک',7.6),(167,'دشواری و زمان','متوسط؛ پس از برداشت و انتخاب یراق',7.4)]:rtl(c,title,x,96,6.8,color='#777777');rtl(c,text,x,112,size)
    rect(c,35,138,526,312);line(c,299,148,299,430,'#aaaaaa',.5)
    x,y,w,h=66,184,207,167
    hatch(c,x,y,w,6);hatch(c,x,y+h-6,w,6);hatch(c,x,y,6,h);hatch(c,x+w-6,y,6,h)
    rail(c,x+9,y+12,w-18);rail(c,x+9,y+h-19,w-18);rect(c,x+w*.52,y+23,w*.43,h-46,YELLOW,INK,.6)
    rect(c,x+10,y+20,w*.47,h-40,ORANGE,INK,.7);rect(c,x+w*.54,y+26,w*.40,h-52,'#ffffff',INK,.7)
    c.setFillColor(HexColor('#555555'));c.circle(x+w*.58,H-y-84,2.5,fill=1,stroke=0);rect(c,x+w*.93,y+50,4,8,'#555555');rect(c,x+w*.93,y+120,4,8,'#555555')
    arrow(c,242,164,133,164,'پنل به چپ');dimh(c,x,x+w,374,y+h,'W');dimv(c,y,y+h,52,x,'H');dimh(c,x+w*.54,x+w*.94,402,y+h,'Wc')
    for args in [(1,97,213,131,258),(2,266,165,245,201),(3,242,322,235,275),(4,196,294,186,268)]:num(c,*args)
    rtl(c,'نمای روبه‌رو پس از کنار رفتن پنل',168,433,8.2,True,center=True)
    sx,sy,sw,sd=335,191,195,151
    hatch(c,sx,sy,sw,6);hatch(c,sx,sy,6,sd);hatch(c,sx+sw-6,sy,6,sd);rect(c,sx+sw*.54,sy+7,sw*.41,48,YELLOW,INK,.6);hatch(c,sx+sw*.52,sy+6,5,52)
    rect(c,sx+sw*.55,sy+57,sw*.39,5,'#dddddd',INK,.5);rect(c,sx+8,sy+66,sw*.49,6,ORANGE,INK,.65)
    line(c,sx+sw*.55,sy+69,sx+sw-8,sy+69,'#777777',.7,[3,2]);arrow(c,sx+155,sy+94,sx+35,sy+94,'S');line(c,sx,sy+sd,sx+sw,sy+sd,'#888888',.5,[4,3])
    rtl(c,'جلوی کابینت',sx+sw/2,sy+sd+15,7.1,color='#555555',center=True);dimv(c,sy,sy+sd,548,sx+sw,'D');dimv(c,sy+7,sy+55,515,sx+sw*.91,'Dc')
    num(c,5,479,166,482,220);num(c,6,355,319,354,264);rtl(c,'برش افقی از بالا؛ محفظه ثابت است',433,433,8.2,True,center=True)
    for x,color,s in [(525,ORANGE,'پنل متحرک'),(421,YELLOW,'فضای محفظه'),(197,'#777777','یراق')]:rect(c,x,463,12,7,color);rtl(c,s,x-7,470,6.5)
    hatch(c,313,463,12,7);rtl(c,'چوب در برش',306,470,6.5);line(c,84,467,101,467,'#777777',.6,[3,2]);rtl(c,'وضعیت بسته',80,470,6.5)
    heading(c,'ابعاد و مشخصات (میلی‌متر)',493,35,245)
    rows=[('W / H / D','عرض، ارتفاع و عمق: برداشت از محل'),('Wc / Dc','عرض و عمق مفید محفظه: برداشت'),('S','کورس حرکت تا آزاد شدن کامل در'),('t','ضخامت ورق مطابق سازهٔ موجود'),('پوشش لبه','هم‌پوشانی لازم برای پنهان شدن در'),('فضای چپ','به اندازهٔ حرکت کامل پنل آزاد باشد'),('طبقات','جداشونده؛ خارج از مسیر حرکت پنل')]
    for i,(key,value) in enumerate(rows):
        yy=503+i*22;rect(c,35,yy,245,22,'#f3f3f3' if i%2==0 else '#ffffff','#aaaaaa',.4);line(c,100,yy,100,yy+22,'#aaaaaa',.4)
        if re.match('[A-Za-z]',key):en(c,key,67.5,yy+14,8,True,center=True)
        else:rtl(c,key,67.5,yy+14,7,True,center=True)
        rtl(c,value,273,yy+14,7.1)
    rtl(c,'اعداد واقعی از ویدیو استخراج نشده‌اند.',280,672,7.4,True,BROWN);rtl(c,'اندازه‌گذاری نهایی پس از برداشت و انتخاب ریل.',280,686,7.1)
    heading(c,'راهنمای شماره‌ها و طرز کار',493,308,253)
    parts=['پنل کاذب؛ حرکت افقی به سمت چپ','ریل‌های افقی بالا و پایین پنل','درِ داخلی؛ لولا در راست، بازشو به جلو','قفل کلیدیِ در داخلی','محفظهٔ ثابت در پشتِ بخش سمت راست','فضای توقف پنل پس از برداشتن طبقات']
    for i,s in enumerate(parts):
        yy=515+i*18;rtl(c,s,543,yy,7.9);c.setFillColor(HexColor('#ffffff'));c.setStrokeColor(HexColor(INK));c.circle(555,H-yy+3,5.5,fill=1,stroke=1);en(c,str(i+1),555,yy-.5,7.3,center=True)
    yy=wrap(c,'ترتیب دسترسی: باز کردن درهای اصلی، برداشتن طبقات، لغزش پنل به چپ و سپس باز کردن قفل و درِ داخلی.',561,633,253,7.6,12)
    wrap(c,'یراق: ریل تلسکوپی افقی، لولای در داخلی، قفل کلیدی و نگهدارندهٔ طبقه؛ مدل دقیق یراق در مرجع مشخص نیست.',561,yy+4,253,7.4,12)
    heading(c,'نکات اجرا برای دیده نشدن',713)
    rtl(c,'• رنگ، ضخامت و درز پنل با اجزای داخلی هماهنگ باشد؛ هیچ باکسی به بیرون کشیده نمی‌شود.',561,734,8)
    rtl(c,'• ریل و دوبل‌شدن داخل کابینت می‌تواند محل را لو بدهد؛ امتیاز مخفی بودن ۲ از ۵ برآوردی است.',561,750,8)
    rect(c,35,762,526,34,'#fff7f0','#cf5c22',.6)
    rtl(c,'شرط اجرا: فضای کافی برای حرکت پنل و بازشدن هر دو در کنترل شود؛ قبل از برش، نمونهٔ خشک بسازید.',551,776,7.8,True)
    rtl(c,'مرجع: ویدیوی کابینت اکازیون؛ این نقشه بازخوانی شماتیک سازوکار است، نه نقشهٔ اندازه‌برداری‌شده.',551,789,7.2)
    c.linkURL(SOURCE,(35,H-796,561,H-762),relative=0);footer(c,'technical');c.showPage()
def overlay(doc,p,draw):
    b=io.BytesIO();c=canvas.Canvas(b,pagesize=(W,H),pageCompression=1);draw(c);c.save();o=fitz.open(stream=b.getvalue(),filetype='pdf');doc[p].show_pdf_page(doc[p].rect,o,0)
def build():
    c=canvas.Canvas(str(ROOT/'design-074.pdf'),pagesize=(W,H),pageCompression=1);c.setTitle('چوب‌راز | طرح ۷۴ - '+TITLE)
    photo(c);schematic(c);technical(c);c.save();extra=fitz.open(ROOT/'design-074.pdf')
    doc=fitz.open(ROOT/'catalog.pdf');toc=[t for t in doc.get_toc() if t[2]<=229]
    if len(doc)>229:doc.delete_pages(229,len(doc)-1)
    doc.insert_pdf(extra);assert len(doc)==232
    def index(c):
        y=H-110-25-24*25;rect(c,28,H-y-25,W-56,25,'#ffffff',None)
        rtl(c,'۷۴',W-48,H-y-8,10,True,'#884609',True);rtl(c,TITLE,W-82,H-y-8,9.5)
        en(c,'A-20',145,H-y-9,8,color='#756d62',center=True);rtl(c,'۲۳۰',93,H-y-8,9,color='#884609',center=True);rtl(c,'۲۳۲',49,H-y-8,9,center=True)
    overlay(doc,7,index);doc[7].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(28,710,W-28,735),'page':229})
    def scored(c):
        rect(c,35,369,526,17,'#111111',None);rtl(c,'A : افزودهٔ کابینت و کمد',555,381,8.3,True,'#ffffff');rect(c,35,386,526,19,'#ffffff','#888888',.4)
        for x in [95,148,346,495,532]:line(c,x,386,x,405,'#888888',.4)
        rtl(c,'۷۴',547,399,7.5,center=True);en(c,'A-20',514,399,7.6,True,center=True);rtl(c,TITLE,490,399,7.6,True);rtl(c,'داخل کابینت یا کمد',340,399,7.4)
        for j in range(5):
            c.setStrokeColor(HexColor(BROWN));c.setFillColor(HexColor(BROWN if j>=3 else '#ffffff'));c.circle(105+j*8,H-395,2.6,fill=1,stroke=1)
        rtl(c,'متوسط',65,399,7.4,center=True);rtl(c,'امتیاز طرح ۷۴ برآوردی است؛ توضیح و نقشه در انتهای سند.',561,420,7.3,color='#666666')
    overlay(doc,3,scored);doc[3].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(35,386,561,405),'page':229})
    for n,f in [('CFa','NotoSansArabic-Regular.ttf'),('CFaB','NotoSansArabic-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/noto/'+f))
    def cover(c):
        rect(c,36,79,W-72,68,'#f5f1e9',None);c.setFillColor(HexColor('#29251e'));c.setFont('CFaB',19);c.drawRightString(W-40,H-101,shape('۷۴ طرح چوبی با محفظهٔ مخفی'))
        c.setFillColor(HexColor('#756d62'));c.setFont('CFa',11);c.drawRightString(W-40,H-130,shape('نقشه‌های ۷۴ طرح، همراه ۷۴ جفت تصویر واقع‌نما'))
    overlay(doc,4,cover)
    for i in range(4,229):
        pg=doc[i];spans=[s for b in pg.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if s['text'].strip()==f'{i+1} / 229']
        for s in spans:pg.add_redact_annot(fitz.Rect(s['bbox']),fill=(245/255,241/255,233/255) if i==4 else (1,1,1))
        if spans:pg.apply_redactions(images=0,graphics=0)
        for s in spans:pg.insert_text(s['origin'],f'{i+1} / 232',fontsize=s['size'],fontname='helv',color=tuple(((s['color']>>n)&255)/255 for n in (16,8,0)))
    doc.set_toc(toc+[[1,'۷۴. '+TITLE+' (A-20)',230],[2,'تصویر شماتیک',231],[2,'نقشه و جزئیات اجرایی',232]])
    doc.set_metadata({**doc.metadata,'title':'چوب‌راز - کاتالوگ ۷۴ طرح با محفظهٔ مخفی'})
    temp=ROOT/'catalog.tmp.pdf';doc.save(temp,garbage=4,deflate=True);doc.close();temp.replace(ROOT/'catalog.pdf')
    meta=json.loads((ROOT/'design-074.json').read_text());meta.update({'revision':2,'mechanism':'باز کردن درهای اصلی، برداشتن طبقات جداشونده، لغزاندن پنل کاذب به چپ و باز کردن در قفل‌دار محفظهٔ ثابت در پشت قسمت راست؛ باکس به جلو کشیده نمی‌شود.','image_note':'بازسازی واقع‌نما با هوش مصنوعی؛ پنل جانبی متحرک و محفظهٔ ثابت، بدون ابعاد تأییدشده.','technical_note':'عکس جفتی، نمای شماتیک بسته و باز، نقشه با نما و برش افقی، راهنمای قطعات، مشخصات پارامتری، یراق و نکات اجرا.','technical_page':3,'catalog_photo_page':230,'catalog_schematic_page':231,'catalog_technical_page':232,'dimensions_verified':False,'dimensions_basis':'W/H/D/Wc/Dc/S/t پارامترهای برداشت از محل‌اند؛ عددی به ویدیو نسبت داده نشده است.','correction':'باکس بیرون‌کشیدنیِ تصویر قبلی با پنل لغزندهٔ جانبی و محفظهٔ ثابت جایگزین شد.'})
    (ROOT/'design-074.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    s=(ROOT/'index.html').read_text().replace('باکس ریلی با درِ قفل‌دار داخلی','پنل لغزنده به چپ؛ محفظهٔ ثابت در پشتِ سمت راست')
    s=s.replace('href="full-074.jpg"','href="full-074.jpg?v=2"').replace('src="thumb-074.webp"','src="thumb-074.webp?v=2"').replace('href="design-074.pdf#page=2"','href="design-074.pdf?v=2#page=3"').replace('>جزئیات اجرا</a>','>نقشهٔ فنی</a>')
    s=s.replace('۷۴ طرح با ۷۴ جفت تصویر واقع‌نما؛ نقشه‌های ۷۳ طرح نخست و جزئیات اجرای طرح جدید.','۷۴ طرح با ۷۴ جفت تصویر واقع‌نما، تصاویر شماتیک و نقشه‌های فنی؛ همراه راهنما و فهرست اصلی.').replace('href="catalog.pdf"','href="catalog.pdf?v=2"')
    (ROOT/'index.html').write_text(s)
    print(json.dumps({'pages':len(fitz.open(ROOT/'catalog.pdf')),'design_pages':len(extra),'bytes':(ROOT/'catalog.pdf').stat().st_size}))
if __name__=='__main__':build()
