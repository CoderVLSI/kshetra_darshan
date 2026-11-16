"""Produce and render a source-linked research PDF without changing game files."""
from pathlib import Path
from html import escape
import json
import re
import textwrap
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'pdf'
RENDER=ROOT/'tmp'/'pdfs'/'rendered'
OUT.mkdir(parents=True,exist_ok=True)
RENDER.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'temples.json').read_text(encoding='utf-8'))
deities=json.loads((ROOT/'deities.json').read_text(encoding='utf-8'))
profiles={x['id']:x for x in deities['deities']}
sources={x['id']:x for x in data['sources']}
pdfmetrics.registerFont(TTFont('Body','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Bold','C:/Windows/Fonts/arialbd.ttf'))
W,H=595.28,841.89
M=42
CW=W-2*M
INK=colors.HexColor('#18303b')
TEAL=colors.HexColor('#176c73')
GOLD=colors.HexColor('#ba8630')
MUTED=colors.HexColor('#586b75')
PALE=colors.HexColor('#edf3f4')
PATH=OUT/'Maha_Shakti_Peetha_Architecture_and_Deity_References.pdf'
c=canvas.Canvas(str(PATH),pagesize=(W,H))
c.setTitle('Maha Shakti Peetha - Architecture and Main Deity Reference Dossier')
c.setAuthor('Kshetra Darshan research dossier')
PAGE=0
warnings=[]

def clean(value):
    return str(value).replace('\u2014',' - ').replace('\u2013','-').replace('\u2011','-').replace('\u2019',"'").replace('\u2018',"'").replace('\u201c','"').replace('\u201d','"')

def para(text,x,y,width=CW,size=9.2,leading=12.6,color=INK,bold=False):
    style=ParagraphStyle('p',fontName='Bold' if bold else 'Body',fontSize=size,leading=leading,textColor=color,spaceAfter=0)
    p=Paragraph(text,style)
    _,height=p.wrap(width,1000)
    if y>45 and y-height<45:
        warnings.append({'page':PAGE,'bottom':round(y-height,2),'text':re.sub('<[^>]+>','',text)[:90]})
    p.drawOn(c,x,y-height)
    return y-height

def text(value,x,y,**kw):return para(escape(clean(value)),x,y,**kw)
def head(label,y):
    return text(label.upper(),M,y,size=9,leading=12,color=TEAL,bold=True)-5

def page(title,kicker):
    global PAGE
    PAGE+=1
    c.setFillColor(INK);c.rect(0,H-13,W,13,fill=1,stroke=0)
    text('KSHETRA DARSHAN  /  REFERENCE DOSSIER',M,H-31,size=8,leading=10,color=MUTED,bold=True)
    y=text(title,M,H-61,size=21,leading=25,bold=True)
    y=text(kicker,M,y-8,size=9,leading=12,color=MUTED)
    c.setStrokeColor(colors.HexColor('#ccd8dc'));c.line(M,42,W-M,42)
    text('Research only | 16 November 2026 | Source confidence is stated per record',M,31,size=7,leading=9,color=MUTED)
    c.setFont('Body',8);c.setFillColor(MUTED);c.drawRightString(W-M,23,str(PAGE))
    return y-18

def finish():c.showPage()
def source_line(label,url,y):
    return para('<link href="'+escape(url,quote=True)+'" color="#176c73">'+escape(clean(label))+'</link>',M,y,size=8,leading=10.5)-4
def picture(path,x,y,width,height):
    with Image.open(path) as source:
        source=source.convert('RGB')
        source.thumbnail((1280,1100))
        encoded=BytesIO()
        source.save(encoded,format='JPEG',quality=88)
        encoded.seek(0)
    im=ImageReader(encoded);iw,ih=im.getSize();scale=min(width/iw,height/ih)
    rw,rh=iw*scale,ih*scale
    c.drawImage(im,x+(width-rw)/2,y-height+(height-rh)/2,width=rw,height=rh,preserveAspectRatio=True,mask='auto')

y=page('Architecture and Main Deity References','The stotram eighteen, plus three destinations already present in the game')
y=text('A correction reference for the final Gemini build',M,y-20,size=24,leading=30,bold=True)
y=text('21 destination dossiers  |  42 satellite captures  |  21 deity profiles',M,y-18,size=11,leading=15,color=TEAL,bold=True)
y=text('This PDF combines the architecture research with temple-specific main-murti and sacred-form checks. It is designed to prevent a generic temple or generic goddess model from being mistaken for a verified reconstruction.',M,y-22,size=11,leading=16)
y=head('What each destination contains',y-25)
for line in ['An overhead map reference, architecture baseline and documented shrine/feature inventory.','A main deity profile: sacred form, posture, arms, attributes, adornment and associated deities.','A reference photograph where a usable source was found, with limits stated in its caption.','Correction checks, unresolved details and clickable source links.']:
    y=text('- '+line,M,y,size=10,leading=14)-9
y=head('Evidence boundaries',y-22)
y=text('Eight visual references are reproduced: decorated shrine photographs and one illustrative sculpture. They are not eight certified bare-murti surveys. No image was generated. Main images, festival/utsava images, kavacha coverings, historical artwork and sacred natural forms must remain distinct.',M,y,size=10,leading=14)
y=text('Unknown hand geometry, historical images and unmeasured plans remain unknown. In particular, lost Shrinkhala and Sharada images must not be reconstructed as exact originals. Satellite roofs do not establish interior shrine locations.',M,y-15,size=10,leading=14)
y=text('Implementation remains on hold until Gemini completes. No gameplay, temple model or builder was modified to produce this PDF.',M,y-20,size=10,leading=14,bold=True)
finish()

y=page('How to use this reference','Read the evidence label before copying a visual feature')
for title,body in [
 ('Main murti versus decoration','A sari, jewellery, face mask or kavacha may conceal the permanent sculpture. An ornamented photograph does not reveal all arms, attributes or body proportions.'),
 ('Deity-side left and right','Hand descriptions use the deity\'s own right and left unless explicitly stated otherwise. A frontal photograph reverses those sides for the viewer. Never mirror an image merely to match a convenient pose.'),
 ('Sacred forms without a human idol','Kamakhya, Alopi, Jwalamukhi and Mangala Gauri require evidence of their temple-specific sacred forms. Do not manufacture a full anthropomorphic body because the game expects a Deity node.'),
 ('Confidence and conflicts','Primary temple/government accounts are preferred, but conflicts are retained. Secondary reports and image captions remain provisional. Generic goddess iconography is not proof of the exact installed murti.'),
 ('Photograph credit','Images remain credited to their source pages. A research reproduction does not confer permission to reuse a photograph as a commercial game texture or redistribute it without checking rights.'),
 ('Membership','The stotram eighteen are the numbered entries. Madurai, Kalighat and Tuljapur are retained as game extras. No scene replacement or removal is implied.'),
 ('Post-completion review','Recheck the final assets: sacred form first, then arm count and attributes, then architecture and routes. The earlier model screenshots predate Gemini\'s completion and may be stale.')]:
    y=head(title,y);y=text(body,M,y,size=10,leading=14)-17
finish()

y=page('Destination index','Each destination has one architecture page and one deity-reference page')
for i,t in enumerate(data['temples']):
    start=4+2*i
    label=str(t['stotram_order']) if t['stotram_order'] else 'Extra'
    y=text(f"{label:>5}  {clean(t['name'])}  -  pages {start}-{start+1}",M,y,size=10,leading=14)-9
finish()

for t in data['temples']:
    # There are three front-matter pages; destination pages begin at page 4.
    p=profiles[t['id']]
    n=str(t['stotram_order']) if t['stotram_order'] else 'Extra'
    y=page(n+'. '+clean(t['name']),clean(t['location'])+'  |  Architecture and site layout')
    cap=t.get('satellite_capture',{})
    chosen=cap.get('close_view',{}).get('file') or cap.get('file')
    image=ROOT/'output'/'playwright'/chosen if chosen else None
    if image and image.exists():
        image_h=292
        picture(image,M,y,CW,image_h)
        y-=image_h+8
        y=text('Google Maps satellite reference. Attribution is retained in the image. Capture: 16 November 2026; exposure date unknown. Qualitative context, not a measured survey.',M,y,size=7.5,leading=10,color=MUTED)-12
    y=head('Architecture baseline',y)
    y=text(t['architecture'],M,y,size=9,leading=12)-12
    y=head('Documented shrines and features',y)
    for g in t['inventory']:
        label=g['scope'].replace('_',' ')
        y=para('<b>'+escape(clean(label))+':</b> '+escape(clean('; '.join(g['names'])))+'.',M,y,size=8.4,leading=11.3)-6
    if cap.get('visual_review'):
        y=text('Map review: '+cap['visual_review']['note'],M,y-3,size=8.3,leading=11,color=MUTED)-7
    if y>110:
        y=head('Sources and map',y)
        for sid in t['source_ids'][:2]:y=source_line(sid+' - '+sources[sid]['title'],sources[sid]['url'],y)
        y=source_line('Open captured map / satellite source',cap.get('close_view',{}).get('captureUrl') or cap.get('captureUrl') or t['map_links']['google_satellite_lookup'],y)
    finish()

    y=page(n+'. '+p['name'],'Main murti / sacred form - compare identity before sculptural detail')
    top=y
    left=208
    right_x=M+left+17
    right_w=CW-left-17
    im=p.get('image')
    if im:
        picture(ROOT/'deity_assets'/im['file'],M,top,left,238)
        ly=top-245
        ly=text(im['kind'].upper(),M,ly,width=left,size=7.3,leading=10,color=TEAL,bold=True)-6
        ly=text(im['caption'],M,ly,width=left,size=7.8,leading=10.5,color=MUTED)
    else:
        c.setFillColor(PALE);c.roundRect(M,top-210,left,210,6,fill=1,stroke=0)
        ly=text('NO AUTHENTICATED MAIN-MURTI PHOTO INCLUDED',M+14,top-28,width=left-28,size=12,leading=16,color=TEAL,bold=True)-15
        ly=text('The sourced description is retained. An unrelated deity, festival bronze or generated picture has not been substituted.',M+14,ly,width=left-28,size=10,leading=14,color=MUTED)
        ly=top-225
        ly=text(p['photo_status'],M,ly,width=left,size=8,leading=11,color=MUTED)
    ry=top
    for label,key in [('Sacred form','form'),('Posture / configuration','posture'),('Arms','arms'),('Attributes','attributes'),('Adornments / covering','adornment')]:
        ry=text(label.upper(),right_x,ry,width=right_w,size=7.5,leading=10,color=TEAL,bold=True)-4
        ry=text(p[key],right_x,ry,width=right_w,size=9.3,leading=12.5)-11
    y=min(ly,ry)-20
    y=head('Correction check',y);y=text(p['checks'],M,y,size=10,leading=14,bold=True)-14
    y=head('Associated deities and ritual objects',y);y=text(p['associated'],M,y,size=9.3,leading=12.5)-14
    y=head('Unresolved evidence',y);y=text(p['uncertainties'],M,y,size=9.3,leading=12.5,color=MUTED)-14
    y=head('Sources',y)
    refs=[(sid+' - '+sources[sid]['title'],sources[sid]['url']) for sid in p['source_ids']]
    refs += [(x['title'],x['url']) for x in p.get('additional_sources',[])]
    if im:refs.append(('Image source / credit',im['source_page']))
    for label,url in refs:y=source_line(label,url,y)
    finish()

# Appendix: documentary and deity source register with actual URLs, split by measured height.
y=page('Source register','Clickable references; access limitations are preserved in the research data')
registry=[(s['id']+' - '+s['title'],s['url'],s['access']) for s in data['sources']]
seen={x[1] for x in registry}
for p in deities['deities']:
    for ref in p.get('additional_sources',[]):
        if ref['url'] not in seen:registry.append((ref['title'],ref['url'],'deity research source'));seen.add(ref['url'])
    if p.get('image') and p['image']['source_page'] not in seen:
        registry.append(('Image source - '+p['name'],p['image']['source_page'],'reference image with limitations'));seen.add(p['image']['source_page'])
for title,url,status in registry:
    chunks=textwrap.wrap(url,84,break_long_words=True,break_on_hyphens=False)
    needed=32+len(chunks)*9
    if y-needed<65:
        finish();y=page('Source register - continued','Documentary, deity and image references')
    y=source_line(title,url,y)
    y=text('Access / status: '+status,M,y,size=7.3,leading=9,color=MUTED)-3
    y=para('<link href="'+escape(url,quote=True)+'">'+escape('<br/>'.join(chunks)).replace('&lt;br/&gt;','<br/>')+'</link>',M,y,size=7,leading=9,color=MUTED)-12
finish()
c.save()

doc=fitz.open(PATH)
for index,p in enumerate(doc):
    pix=p.get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False)
    pix.save(RENDER/f'page_{index+1:02}.png')
(OUT/'layout_report.json').write_text(json.dumps({'pages':len(doc),'layout_warnings':warnings,'pdf':str(PATH),'rendered_pages':str(RENDER)},indent=2),encoding='utf-8')
print(json.dumps({'pages':len(doc),'warnings':warnings,'pdf':str(PATH)},indent=2))
