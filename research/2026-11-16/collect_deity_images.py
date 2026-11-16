import concurrent.futures
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import requests
import fitz

ROOT = Path(__file__).resolve().parent
TMP = ROOT / 'tmp' / 'pdfs'
ASSETS = ROOT / 'deity_assets'
TMP.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(exist_ok=True)
URL = 'https://nsktu.ac.in/wp-content/uploads/2022/01/M35-Eighteen-Shaktipeethas-Prof-Korada-subrahmanyam.pdf'
r = requests.get(URL, timeout=60)
r.raise_for_status()
(TMP / 'university_reference.pdf').write_bytes(r.content)
doc = fitz.open(stream=r.content, filetype='pdf')
manifest = []
for index, page in enumerate(doc):
    for number, im in enumerate(page.get_images(full=True)):
        image = doc.extract_image(im[0])
        if image['width'] < 180 or image['height'] < 150:
            continue
        name = f'course_page_{index+1:02}_{number:02}.{image["ext"]}'
        (ASSETS / name).write_bytes(image['image'])
        manifest.append({'file':name, 'pdf_page':index+1, 'width':image['width'], 'height':image['height'], 'page_text':page.get_text()[:900], 'source_url':URL, 'kind':'university course image; exact original photographer/subject must be checked'})
(ASSETS / 'course_image_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'img':
            self.items.append({'src':a.get('src') or a.get('data-src'), 'alt':a.get('alt','')})

pages = {
    'kanchi':'https://kanchikamakshi.org/about/',
    'biraja':'https://maabiraja.com/iconography.html',
    'renuka':'https://shrirenukadevi.in/',
    'ambabai':'https://www.mahalaxmikolhapur.com/',
    'jwala':'https://kangratemples.hp.gov.in/shri-jawala-mata-mandir/',
    'chamundi':'https://chamundeshwaritemple.in/about.aspx',
    'jogulamba':'https://gadwal.telangana.gov.in/tourist-place/jogulamba-devi/',
    'srisailam':'https://www.srisailadevasthanam.org/en-in/about/the-temple/bhramaramba-devi',
}
def get_page(item):
    key, url = item
    try:
        response = requests.get(url, timeout=25)
        response.raise_for_status()
        p = Images()
        p.feed(response.text)
        return key, {'page_url':url, 'images':[dict(x, src=urljoin(url,x['src'])) for x in p.items if x['src']]}
    except Exception as e:
        return key, {'page_url':url, 'error':str(e)}
results = dict(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(get_page,pages.items()))
(ASSETS / 'page_image_candidates.json').write_text(json.dumps(results,ensure_ascii=False,indent=2), encoding='utf-8')
print(json.dumps({'course_images':len(manifest), 'pages':{k:len(v.get('images',[])) for k,v in results.items()}}, indent=2))
