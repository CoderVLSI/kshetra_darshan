from pathlib import Path
import concurrent.futures
import json
import requests
from PIL import Image
from io import BytesIO

ROOT=Path(__file__).resolve().parent
assets=ROOT/'deity_assets'
items=[
 ('kanchipuram_kamakshi','https://kanchikamakshi.org/wp-content/uploads/2018/10/PSX_20170720_141503.jpg','https://kanchikamakshi.org/about/','Temple-authority page image; subject must be visually checked'),
 ('jajpur_biraja','https://maabiraja.com/images/xmaaviraja.jpg.pagespeed.ic.eZgVUY4gyL.jpg','https://maabiraja.com/iconography.html','Trust iconography-page image; original photographer/date unstated'),
 ('mahur_renuka','https://shrirenukadevi.in/imagesOfTemples/faceOfRenukaDevi.jpg','https://shrirenukadevi.in/','Temple-portal face image; decoration and recording date unverified'),
 ('kolhapur_mahalakshmi','https://feeds.abplive.com/onecms/images/uploaded-images/2024/05/02/24b07f6d9def569a41dad2975979f3286d574.jpeg?impolicy=abp_cdn&imwidth=720','https://marathi.abplive.com/photo-gallery/news/kolhapur-kolhapur-news-former-chief-minister-uddhav-thackeray-visits-shri-ambabai-mandir-kolhapur-with-son-tejas-1278597','ABP Majha news photograph, article dated 2 May 2024; decorated shrine, not bare stone geometry'),
 ('prayag_madhaveswari','https://www.jagranimages.com/images/newimg/14082024/Alopi%20Devi%20Temple.jpg','https://www.jagran.com/spiritual/mukhye-dharmik-sthal-alopi-devi-temple-the-palm-of-the-right-hand-of-maa-sati-had-fallen-at-this-place-know-the-specialty-and-more-details-23778259.html','Dainik Jagran cradle-shrine reference, 2024 article; original photographer unconfirmed'),
 ('ujjain_mahakali','https://templesofindia.org/assets/compressed/3af8bce08e439d8bd6be1b1768a446fb_219.jpg','https://templesofindia.org/temple-view/harsiddhi-mandir-square-ujjain-madhya-pradesh-7qwg','Secondary Harsiddhi image; entire three-image arrangement may not be visible'),
 ('draksharama_manikyamba','https://templeconnect.com/wp-content/uploads/2022/06/Goddess-Manikyamba-of-Draksharamam.jpg','https://templeconnect.com/draksharamam-bhimeswara-swamy-temple/','Temple Connect decorated Manikyamba shrine reference; underlying hand geometry obscured'),
 ('pithapuram_puruhutika','https://static.toiimg.com/thumb/msid-104468042%2Cwidth-748%2Cheight-499%2Cresizemode%3D4%2Cimgsize-56768/Puruhutika-Devi-Temple-Andhra-Pradesh.jpg','https://timesofindia.indiatimes.com/travel/destinations/all-about-18-astadasha-shakti-peethas-holy-abodes-of-shakti/photostory/104467781.cms','Times of India captioned reference; exact main-versus-festival identity not authenticated'),
 ('mysore_chamundeshwari','https://akm-img-a-in.tosshub.com/sites/media2/indiatoday/images/stories/2016October/temple-mos2_102116094028.jpg','https://www.indiatoday.in/india/story/jayalalithaa-tamil-nadu-special-prayers-mysuru-temple-347871-2016-10-21','India Today, 21 October 2016; decorated deity photo; no bare-anatomy certification'),
 ('madurai_meenakshi','https://upload.wikimedia.org/wikipedia/commons/0/03/Minakshi.jpg','https://commons.wikimedia.org/wiki/File:Minakshi.jpg','Historical painting, circa 1820, British Museum 2007,3005.49; NOT a photograph of the main murti'),
 ('srisailam_bhramaramba','https://pbs.twimg.com/media/G1f2yn_XkAAX0lD?format=jpg&name=small','https://www.shanarthi.com/latest/karthika-masam-celebrations-begin-in-srisailam/','Decorated Bhramaramba portrait reproduced in a local news report; main/festival identity unverified')
]
def fetch(item):
 id,url,page,caption=item
 record={'id':id,'url':url,'source_page':page,'caption':caption,'rights':'Reference reproduction with source attribution; no game-asset reuse permission assumed','included':False}
 try:
  r=requests.get(url,timeout=30)
  r.raise_for_status()
  im=Image.open(BytesIO(r.content)).convert('RGB')
  im.save(assets/(id+'.jpg'),quality=95)
  record.update(file=id+'.jpg',size=list(im.size),download_status='ok')
 except Exception as e:
  record['download_status']=str(e)
 return record
records=list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(fetch,items))
(assets/'selected_images.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{k:x[k] for k in ['id','download_status']} for x in records],indent=2))
