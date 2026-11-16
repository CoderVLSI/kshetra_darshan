"""Keep visitor-facing heritage text factual rather than authoring directions."""
import json
from pathlib import Path
data=Path(__file__).resolve().parents[1]/'godot/data'
p=data/'reference_notes.json'
notes=json.loads(p.read_text(encoding='utf-8-sig'))
updates={
 'lanka_shankari':'The present Dravidian Koneswaram complex stands on a narrow sea cliff. Its modern buildings are distinct from the ancient temple destroyed in the Portuguese period; the lost original Shankari footprint remains unresolved.',
 'srisailam_bhramaramba':'A shared Shiva–Shakti complex with enclosure walls, gateway towers and connected pillared spaces. Bhramaramba and Mallikarjuna are distinct principal sanctuaries within the ensemble.',
 'mahur_renuka':'Hilltop temple with a sanctum and assembly hall, a silver-clad doorway and a large worshipped face/head form. Steps and the hill approach are part of its setting.',
 'gaya_mangalagauri':'Compact hill shrine approached by steps and road. The principal sacred form is symbolic; the sanctum also contains old relief work.',
 'kalighat':'Bengali atchala-roofed shrine with decorated surfaces and a later natmandir in a dense urban precinct.',
 'tuljapur_bhavani':'Hemadpanti stone temple approached by descending steps, with successive gateways, tirthas and ritual spaces.',
 'jwalamukhi_vaishnavi':'Hillside temple complex with a gilded dome. Natural flames in rock fissures are worshipped as the central manifestation. Nine named flames share the sacred precinct.',
 'pradyumna_shrinkhala':'Present-day Pandua Minar and roofless Bari Masjid, based on ASI photographs and a published site plan. The precise ancient Shrinkhala shrine remains unresolved. The model dimensions, spacing and damage are approximate.'}
for key,text in updates.items(): notes[key]['architecture']=text
for key,value in notes.items():
 value['preservation_status']='This is an interpretive scene, not a complete record of surviving carvings or inscriptions. Exact epigraphy and object-by-object sculpture matching remain incomplete.'
p.write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for key,text in {
 'draksharama_manikyamba':'Manikyamba is venerated here in the Ashtadasha Shakti Peetha tradition, within the Bhimeswara temple complex.',
 'kashmir_sharada':'The ruins preserve the memory of Sharada worship and a historic centre of learning. The modern Teetwal shrine is a separate site.',
 'jwalamukhi_vaishnavi':'The Goddess is worshipped here through natural flames. A figurative main idol is not the central sacred form.'}.items():
 p=data/(key+'_heritage.json');d=json.loads(p.read_text(encoding='utf-8-sig'));d['pilgrimage_significance']=text;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
