"""Build research documents and contact sheets; never touches game files."""
import csv
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'temples.json').read_text(encoding='utf-8-sig'))
sources = {s['id']: s for s in data['sources']}
assert len(data['temples']) == 21
assert sorted(t['stotram_order'] for t in data['temples'] if t['stotram_order']) == list(range(1, 19))
assert len({t['id'] for t in data['temples']}) == 21
for temple in data['temples']:
    for sid in temple['source_ids']:
        assert sid in sources, (temple['id'], sid)
    for group in temple['inventory']:
        for sid in group['source_ids']:
            assert sid in sources, (temple['id'], sid)

capture_dir = ROOT / 'output' / 'playwright'
capture_text_path = capture_dir / 'capture_run.txt'
captures = []
if capture_text_path.exists():
    text = capture_text_path.read_text(encoding='utf-8-sig')
    if '### Result' in text:
        text = text.split('### Result', 1)[1].lstrip()
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
        captures, _ = json.JSONDecoder().raw_decode(text)
        (capture_dir / 'capture_log.json').write_text(json.dumps(captures, ensure_ascii=False, indent=2), encoding='utf-8')
by_id = {x['id']: x for x in captures}
reviews_path = ROOT / 'map_visual_review.json'
reviews = {x['id']: x for x in json.loads(reviews_path.read_text(encoding='utf-8'))} if reviews_path.exists() else {}
for item in captures:
    if item['id'] in reviews:
        item['visual_review'] = reviews[item['id']]
        item['status'] = 'qualitative context reviewed; not a survey'
close_records = []
close_run = capture_dir / 'close_capture_run.txt'
if close_run.exists():
    close_text = close_run.read_text(encoding='utf-8-sig')
    if '### Result' in close_text:
        close_text = close_text.split('### Result', 1)[1].lstrip()
        close_records, _ = json.JSONDecoder().raw_decode(close_text)
        (capture_dir / 'close_capture_log.json').write_text(json.dumps(close_records, ensure_ascii=False, indent=2), encoding='utf-8')
        for close in close_records:
            if close['id'] in by_id:
                by_id[close['id']]['close_view'] = close
        jwala = by_id.get('jwalamukhi_vaishnavi')
        if jwala:
            jwala['original_lookup_warning'] = 'Initial lookup selected Jawalamukhi town. Use corrected temple close view at 31.8753944, 76.3240824.'
            jwala['corrected_place_url'] = 'https://www.google.com/maps/place/Shri+Jwalamukhi+Mata+Shaktipeeth/data=!4m2!3m1!1s0x391b312f2171643f:0xa49c70e95f333bc1'

def link(sid):
    s = sources[sid]
    return f"[{s['title']}]({s['url']})"

if captures:
    (capture_dir / 'capture_log.json').write_text(json.dumps(captures, ensure_ascii=False, indent=2), encoding='utf-8')

md = ['# Temple architecture reference dossier', '',
      'Research date: 16 November 2026 (Asia/Calcutta). Research only; Gemini must finish before implementation.', '',
      '## Scope and confidence', '',
      'The stotram eighteen and three additional destinations already in the game are covered. Use the stotram on PDF pages 2-3 of ' + link('STOTRAM') + ' for membership; its later table has an extra Danteswari row. No game destination has been removed or replaced.', '',
      'Inventories list documented shrines AND halls, images, water features, ritual objects and regional sites. They are not certified exhaustive shrine counts. Scope and confidence are recorded for every group. Exact positions and measured dimensions remain unknown unless independently established.', '',
      'Satellite screenshots record current map imagery, not historical ground plans. Provider imagery dates are unknown. Place pins are not survey control points. Aerial/drone links are separately labelled candidates; not every clip has been watched or authenticated. No reuse licence is assumed.', '',
      'See [maps and satellite captures](MAPS.md), [machine-readable evidence](temples.json), [inventory CSV](shrine_and_feature_inventory.csv), [source caveats](SOURCE_CAVEATS.md), [evidence gaps](EVIDENCE_GAPS.md) and [post-Gemini review procedure](POST_GEMINI_REVIEW.md).', '',
      '## Coverage', '',
      '| Order | Destination | Satellite capture | External aerial/elevated lead |',
      '|---|---|---|---|']
for t in data['temples']:
    cap = by_id.get(t['id'])
    image_path = capture_dir / (t['id'] + '_satellite.png')
    satellite = f'[Captured](output/playwright/{image_path.name})' if image_path.exists() else 'Pending'
    md.append(f"| {t['stotram_order'] or 'Extra'} | [{t['name']}](#{t['id'].replace('_', '-')}) | {satellite} | {'Located; review pending' if t['aerial_references'] else 'No authenticated candidate'} |")
    if cap:
        t['satellite_capture'] = cap
for t in data['temples']:
    md += ['', f'<a id="{t["id"].replace("_", "-")}"></a>', '',
           f"## {t['stotram_order'] or 'Extra'}. {t['name']}", '',
           f"**Location:** {t['location']}. **Game/proposed ID:** `{t['id']}`.", '',
           '**Architecture baseline:** ' + t['architecture'], '', '**Documented inventory:**', '']
    for g in t['inventory']:
        md.append(f"- **{g['scope'].replace('_', ' ')}** ({g['confidence']}): {'; '.join(g['names'])}. Evidence: {'; '.join(link(s) for s in g['source_ids'])}. Positions unverified.")
    md += ['', f"**Map links:** [Satellite lookup]({t['map_links']['google_satellite_lookup']}) / [Place lookup]({t['map_links']['google_place_lookup']})."]
    if t['id'] in by_id:
        cap = by_id[t['id']]
        md += ['', f"**Captured map:** [Full screenshot](output/playwright/{cap.get('file', '')}) / [Capture URL]({cap.get('captureUrl', '')}). Capture date 16 November 2026; imagery date unknown. Satellite roof outline is not an interior shrine survey."]
        if cap.get('close_view'):
            md += ['', f"**Closer view:** [Satellite detail](output/playwright/{cap['close_view']['file']})."]
        if cap.get('original_lookup_warning'):
            md += ['', '**Lookup correction:** ' + cap['original_lookup_warning']]
        if cap.get('visual_review'):
            md += ['', '**Visual review:** ' + cap['visual_review']['note']]
    md += ['', '**Aerial / elevated candidates:** ' + t['aerial_status'], '']
    for a in t['aerial_references']:
        md.append(f"- [{a['title']}]({a['page_url']})" + (f" / [preview]({a['image_url']})" if a['image_url'] else '') + f". {a['kind'].replace('_', ' ')}. {a['notes']} North/scale unverified.")
    md += ['', '**Ground photographs / walkthroughs:**', '']
    for p in t['photo_references']:
        md.append(f"- [{p['title']}]({p['page_url']})" + (f" / [image]({p['image_url']})" if p['image_url'] else '') + '. ' + p['notes'])
    md += ['', '**Correction checks after Gemini finishes:**', ''] + ['- ' + x for x in t['correction_checks']]
    md += ['', '**Unresolved:**', ''] + ['- ' + x for x in t['uncertainties']]
    md += ['', '**Architecture / identity sources:** ' + ' / '.join(link(s) for s in t['source_ids']) + '.']
md += ['', '## Source register', '', 'Access status distinguishes pages read from search excerpts, incomplete extraction and blocked documents.', '']
for s in data['sources']:
    md.append(f"- **{s['id']}:** [{s['title']}]({s['url']}) - {s['type']}; {s['access']}. {s['notes']}")
(ROOT / 'DOSSIER.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
(ROOT / 'temples.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

with (ROOT / 'shrine_and_feature_inventory.csv').open('w', encoding='utf-8-sig', newline='') as out:
    writer = csv.writer(out)
    writer.writerow(['temple_id', 'stotram_order', 'destination', 'feature_name', 'scope', 'confidence', 'position_status', 'source_urls'])
    for t in data['temples']:
        for g in t['inventory']:
            for name in g['names']:
                writer.writerow([t['id'], t['stotram_order'] or 'extra', t['name'], name, g['scope'], g['confidence'], g['positions_status'], ' | '.join(sources[s]['url'] for s in g['source_ids'])])

maps = ['# Satellite and aerial reference index', '',
        'Captured 16 November 2026 through Google Maps in a browser. Full screenshots retain attribution. Exposure dates are unknown. No dimensions or complete interior layout have been established from these captures.', '',
        'Shrinking screenshots into contact sheets makes provider attribution small; use the linked originals for inspection. External drone/elevated links remain candidates rather than measured evidence.', '']
for batch in range(3):
    group = data['temples'][batch * 9:(batch + 1) * 9]
    if not group:
        continue
    rows = (len(group) + 2) // 3
    sheet = Image.new('RGB', (1500, rows * 385), '#18202a')
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    for i, t in enumerate(group):
        x, y = (i % 3) * 500, (i // 3) * 385
        draw.text((x + 8, y + 8), f"{t['stotram_order'] or 'Extra'}. {t['id']}", font=font, fill='white')
        f = capture_dir / (t['id'] + '_satellite_close.png')
        if not f.exists():
            f = capture_dir / (t['id'] + '_satellite.png')
        if f.exists():
            with Image.open(f) as im:
                im.thumbnail((500, 347))
                sheet.paste(im, (x, y + 35))
    filename = f'satellite_contact_sheet_{batch + 1}.jpg'
    sheet.save(ROOT / filename, quality=94)
    maps += [f'![Satellite reference sheet {batch + 1}]({filename})', '']
for t in data['temples']:
    cap = by_id.get(t['id'], {})
    maps += [f"## {t['stotram_order'] or 'Extra'}. {t['name']}", '',
             f"[Full satellite screenshot](output/playwright/{t['id']}_satellite.png) / [Place lookup]({t['map_links']['google_place_lookup']})", '']
    if cap:
        maps += [f"Selected page: {cap.get('selectedTitle', '')}. [Selected pin/source]({cap.get('pinUrl', '')}). Lookup coordinates: {cap.get('lookup_position')} (not surveyed).", '']
        if cap.get('close_view'):
            maps += [f"[Closer satellite screenshot](output/playwright/{cap['close_view']['file']}) / [Closer view URL]({cap['close_view']['captureUrl']}).", '']
        if cap.get('original_lookup_warning'):
            maps += ['**Correction:** ' + cap['original_lookup_warning'], '']
        if cap.get('visual_review'):
            maps += ['**Visual review:** ' + cap['visual_review']['note'], '']
    for a in t['aerial_references']:
        maps.append(f"- [{a['title']}]({a['page_url']}) - {a['kind']}; {a['notes']}")
    maps += ['']
(ROOT / 'MAPS.md').write_text('\n'.join(maps), encoding='utf-8')

count = sum(len(g['names']) for t in data['temples'] for g in t['inventory'])
sat_count = sum((capture_dir / (t['id'] + '_satellite.png')).exists() for t in data['temples'])
readme = f'''# Maha Shakti Peetha reference pack

Prepared 16 November 2026. Research only; wait for Gemini's completion before implementation.

- **21 destination records:** the stotram eighteen plus Madurai, Kalighat and Tuljapur already in the game.
- **{len(data['sources'])} cited sources**, with access status and source caveats.
- **{count} named shrine/feature records**, including aliases, halls, images, water features and regional sites. This is not a claim of {count} distinct shrines or exhaustive coverage.
- **{sat_count} location map captures plus {len(close_records)} closer views**, provider attribution retained; imagery dates unknown. Use the corrected close view for Jwalamukhi.
- **{sum(bool(t['aerial_references']) for t in data['temples'])} external aerial/elevated reference leads**, with authentication/measurement limitations recorded.

Start with [the full dossier](DOSSIER.md), [maps and contact sheets](MAPS.md), [the shrine/feature inventory](shrine_and_feature_inventory.csv), or [structured data](temples.json).

See [visual findings](VISUAL_FINDINGS.md) and [per-map review notes](map_visual_review.json). Alopi, Gaya and Kamakhya imagery has haze/softness limitations. External drone leads are not all frame-verified.

Before correction, read [the review procedure](POST_GEMINI_REVIEW.md), [evidence gaps](EVIDENCE_GAPS.md), and [conflicting/rejected sources](SOURCE_CAVEATS.md).

The canonical list discrepancy is documented; no destination was removed or substituted. Shrinkhala's historical plan, Sharada's missing fabric, exact dimensions and exhaustive modern shrine inventories remain unresolved. Satellite roofs do not establish interior walls or shrine identities.

Only files inside this research directory are authored by this research task. No game scripts, Blender builders, GLBs, scenes, builds or handoff were modified during this research.
'''
(ROOT / 'README.md').write_text(readme, encoding='utf-8')
print(json.dumps({'destinations': len(data['temples']), 'sources': len(sources), 'named_records': count, 'satellite_files': sat_count, 'capture_metadata_records': len(captures), 'validation': 'passed'}, indent=2))
