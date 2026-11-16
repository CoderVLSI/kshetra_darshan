"""Apply sourced present-condition Pandua metadata alongside its model."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'godot/data'
def read(name): return json.loads((DATA/name).read_text(encoding='utf-8-sig'))
def write(name, value): (DATA/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources = [
    {'id':'PANDUA_ASI_MINAR','title':'ASI Kolkata Circle: Pandua Minar, photographs and plan','url':'https://asikolkata.in/monument-sites/the-minar/'},
    {'id':'PANDUA_ASI_MOSQUE','title':'ASI Kolkata Circle: Bari Masjid ruins, photographs and plan','url':'https://asikolkata.in/monument-sites/the-mosque/'}]
catalog=read('shrine_catalog.json')
site=catalog['temples']['pradyumna_shrinkhala']
site['scope_note']='Present-day Pandua monument setting. Shrinkhala is a traditional association; the exact ancient shrine is unresolved. The minaret is not identified as a surviving temple tower.'
site['sources']+= [s for s in sources if s['id'] not in [x['id'] for x in site['sources']]]
site['shrines']=[
    {'id':'main','label':'Shrinkhala — traditional Pandua association','deity':'Shrinkhala tradition; no verified surviving shrine','form':'unknown','kind':'heritage','evidence':'Traditional association, not an archaeologically authenticated surviving sanctum.','source_ids':['PANDUA_ASI_MINAR','PANDUA_ASI_MOSQUE'],'model_anchor':'Pandua_Interpretation_Point','placement':None,'notes':'Interpretation viewpoint. No original murti or functioning temple is reconstructed.'},
    {'id':'pandua_minar','label':'Pandua Minar — protected monument','deity':'Historic minaret; not a deity shrine','form':'unknown','kind':'heritage','evidence':'ASI identifies a brick-built minar with four diminishing stages and restored upper portion.','source_ids':['PANDUA_ASI_MINAR'],'model_anchor':'Pandua_Minar','placement':None,'notes':'ASI records 127 feet height and several possible historical purposes. The scene has no accessible internal spiral stair.'},
    {'id':'bari_masjid','label':'Bari Masjid — roofless remains','deity':'Historic mosque remains; not a Shakti shrine','form':'unknown','kind':'heritage','evidence':'ASI documents the surviving mosque, lost domes, pillars and east-facing arcade.','source_ids':['PANDUA_ASI_MOSQUE'],'model_anchor':'BariMasjid_Ruins','placement':None,'notes':'Architecture study from ASI photos and site plan. Exact broken edges, reused carvings and inscriptions remain unrecorded.'}]
write('shrine_catalog.json',catalog)
notes=read('reference_notes.json')
entry=notes['pradyumna_shrinkhala']
entry.update({'architecture':'Present-day Pandua Minar and roofless Bari Masjid represented from ASI photographs and a published site plan. Profiles, damage and spacing remain approximate. This replaces the former hypothetical navaratna temple.','deity_form':'No verified surviving original Shrinkhala image is supplied.','posture':'Not established','arms':'Not established','attributes':'Not established','uncertainties':'The traditional Pradyumna/Pandua association does not authenticate the minaret as temple fabric. No daily worship or exact ancient temple footprint is asserted. Reused carvings and any inscriptions require object-level documentation.','reconstruction':True,'sources':sources})
write('reference_notes.json',notes)
heritage=read('pradyumna_shrinkhala_heritage.json')
heritage.update({'devi_anga':'Traditional associations vary; not an archaeological identification','bhairava':'Not securely established here','mythology':'The Ashtadasha tradition names Shrinkhala at Pradyumna. Pandua is one traditional identification. The exact original shrine and sacred image are unresolved.','festivals':[],'historical_notes':'ASI protects the Pandua Minar and Bari Masjid separately. The scene represents those surviving monuments, not proof of an intact Shrinkhala temple.','pilgrimage_significance':'A traditional Peetha association distinct from the documented surviving monument identities.'})
write('pradyumna_shrinkhala_heritage.json',heritage)
