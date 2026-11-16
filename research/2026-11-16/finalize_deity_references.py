import json
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parent
assets=ROOT/'deity_assets'
images=json.loads((assets/'selected_images.json').read_text(encoding='utf-8'))
for id,url,page,caption in [
 ('madurai_meenakshi','https://upload.wikimedia.org/wikipedia/commons/3/3c/Minakshi.jpg','https://commons.wikimedia.org/wiki/File:Minakshi.jpg','Historical gouache, circa 1820, unknown artist, British Museum 2007,3005.49. Public-domain artwork. NOT the installed main murti.'),
 ('tuljapur_bhavani','https://images.bhaskarassets.com/thumb/730x0/web2images/5483/2018/11/12/tuljabhavani_1542004949.jpg','https://divyamarathi.bhaskar.com/news/the-devotees-queue-for-mother-tuljabhavani-abhishek-pooja-5980741.html','Divya Marathi shrine photograph accompanying 2018 report. Alankara obscures the underlying arm/weapon arrangement.')
]:
 record={'id':id,'url':url,'source_page':page,'caption':caption,'rights':'Reference image; source credit retained. No commercial game-asset reuse permission inferred.','included':False}
 try:
  r=requests.get(url,timeout=30);r.raise_for_status()
  im=Image.open(BytesIO(r.content)).convert('RGB');im.save(assets/(id+'.jpg'),quality=95)
  record.update(file=id+'.jpg',size=list(im.size),download_status='ok')
 except Exception as e:record['download_status']=str(e)
 images=[x for x in images if x['id']!=id]+[record]
reject={'kanchipuram_kamakshi':'Page photograph shows temple exterior, not the murti. Excluded from deity plate.', 'mysore_chamundeshwari':'Heavily concealed image; exact main-versus-other sacred image identity is not secure. Excluded.'}
for im in images:
 im['included']=im.get('download_status')=='ok' and im['id'] not in reject
 im['visual_review']='Contact sheet reviewed; temple-specific physical details remain limited by decoration.'
 if im['id'] in reject:im['visual_review']=reject[im['id']]
 if im['id']=='jajpur_biraja':
  im['caption']='Illustrative pale sculpture reproduced on Biraja Trust iconography page. NOT authenticated as the installed ancient main image. Use only for the two-arm/buffalo relationship.'
  im['kind']='illustrative sculpture, not main-murti photograph'
 elif im['id']=='madurai_meenakshi':im['kind']='historical painting, not main-murti photograph'
 else:im['kind']='decorated shrine photograph; underlying sculpture not fully visible'
(assets/'selected_images.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')

profiles=json.loads((ROOT/'deities.json').read_text(encoding='utf-8'))
by_id={x['id']:x for x in images if x['included']}
extra_sources={
 'kanchipuram_kamakshi':[
  ['Kamakshi temple authority: posture, attributes and sannadhis','https://kanchikamakshi.org/about/'],
  ['Incredible India: padmasana and four attributes','https://www.prod.incredibleindia.gov.in/content/incredible-india-v2/en/destinations/kanchipuram/sri-kamakshi-temple.html']],
 'mysore_chamundeshwari':[
  ['Eight-arm report (secondary; not final sculptural authority)','https://en.wikipedia.org/wiki/Chamundeshwari_Temple'],
  ['Conflicting eighteen-arm description (do not adopt without corroboration)','https://www.srichamundeshwaridevi.in/about'],
  ['Separate Dasara utsava murti held by Palace Board','https://starofmysore.com/dasara-utsava-murthy-of-chamundeshwari-handed-over-to-temple-authority/']],
 'alampur_jogulamba':[['Jogulamba Gadwal district: corpse seat and head fauna','https://gadwal.telangana.gov.in/tourist-place/jogulamba-devi/']],
 'srisailam_bhramaramba':[['Eight arms and Sri Yantra (secondary account)','https://temple.yatradham.org/temple/bhramaramba-ammavari-temple']],
 'tuljapur_bhavani':[['Maharashtra Tourism: eight-armed black-stone image','https://maharashtratourism.gov.in/temple/tuljapur/']],
 'madurai_meenakshi':[['British Museum: Minaksi historical painting','https://www.britishmuseum.org/collection/object/A_2007-3005-49'],['Commons provenance and public-domain artwork','https://commons.wikimedia.org/wiki/File:Minakshi.jpg']],
 'draksharama_manikyamba':[['Leftward-looking description (secondary only)','https://epaperimages.blob.core.windows.net/statetimes/files/1020211004333281.pdf']],
 'mahur_renuka':[['Temple portal: face-form reference image','https://shrirenukadevi.in/']]
}
for p in profiles['deities']:
 p['image']=by_id.get(p['id'])
 p['additional_sources']=[{'title':title,'url':url} for title,url in extra_sources.get(p['id'],[])]
 p['photo_status']='Reference included with explicit limitations' if p['image'] else 'No authenticated main-murti photograph included; use text/source links and obtain temple-authority confirmation.'
 if p['id']=='kanchipuram_kamakshi':p['uncertainties']+=' The official page image inspected was an exterior, so it was not substituted for a murti portrait.'
(ROOT/'deities.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'profiles':len(profiles['deities']),'included_visual_refs':len(by_id),'excluded':reject},indent=2))
