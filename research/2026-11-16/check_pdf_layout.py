from pathlib import Path
from PIL import Image,ImageDraw
import fitz

ROOT=Path(__file__).resolve().parent
files=sorted((ROOT/'tmp/pdfs/poppler').glob('page-*.png'))
assert len(files)==51
for start in range(0,len(files),12):
    group=files[start:start+12]
    sheet=Image.new('RGB',(1000,((len(group)+3)//4)*365),'#dddddd')
    draw=ImageDraw.Draw(sheet)
    for i,file in enumerate(group):
        x,y=(i%4)*250,(i//4)*365
        with Image.open(file) as im:
            sheet.paste(im.resize((238,337)),(x+6,y+23))
        draw.text((x+6,y+5),file.stem,fill='black')
    sheet.save(ROOT/f'tmp/pdfs/qa_sheet_{start//12+1}.jpg',quality=91)
doc=fitz.open(ROOT/'output/pdf/Maha_Shakti_Peetha_Architecture_and_Deity_References.pdf')
out=[]
for i,page in enumerate(doc):
    for block in page.get_text('dict')['blocks']:
        if block['type']!=0:continue
        x0,y0,x1,y1=block['bbox']
        if x0<0 or y0<0 or x1>page.rect.width+1 or y1>page.rect.height+1:
            out.append((i+1,block['bbox']))
assert not out,out
print('51 pages rendered; no text blocks outside page; five QA sheets created.')
