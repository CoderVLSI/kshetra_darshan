# Kshetra Darshan handoff

Updated 20 November 2026 after the Kolhapur rebuild.

Current status is a playable procedural preview with 21 scenes and 357 mapped destinations. Kolhapur has 64 named destinations spanning the western timber hall, the three sanctums, the upper Matulinga shrine, the four gates and the named court bays. Madurai has 59 named stops. Its twin east-facing sanctuaries, inner prakaras, Golden Lily Tank, northeastern Thousand Pillar Hall and separate approach halls follow the archival plans and aerial imagery. Jwalamukhi has 18 named stops across the flame chamber and terraces. Sharada Peeth has eight stops around its roofless sanctuary and enclosure. Kamakhya has 20 stops in its main compound, and Srisailam has 45. The files under `research/2026-11-16/` record the earlier audit, and `godot/data/reference_notes.json` contains the sources and limits for current scenes.

## Run

- Latest Windows preview: `builds/windows/AshtaDashaShaktiPeetha.exe`, with `AshtaDashaShaktiPeetha.pck` beside it. The older reviewed build is retained separately.
- Original Gemini distribution retained in `builds/windows/`.
- Project: `godot/project.godot` (Godot4.7.1); Blender builders in `blender/` (Blender5.3).
- Desktop controls: WASD or arrow keys move, Space jump, Shift sprint, mouse look, Esc release/capture cursor, V first/third person, P prayer, K forward Pranam, F flowers, G bell, R aarti, T prasadam, C conch, N mantra, B sound, H heritage, M searchable shrine map/teleports, 1–5 time presets. Five selected shrine details offer narration in the existing project voice.

## What changed

Player now faces away from the rear camera, rests with relaxed arms, and joins palms only during P prayer. Walking limbs and safe step-up are implemented. Eighteen existing models rebuilt with corrected architectural dimensions, connected walls/tiers/stairs and exported stone detail. Specific cave/plateau/approach defects repaired. Renuka face-form and Shrinkhala uncertainty corrected. Searchable responsive menu, actual previews, model map and sourced main-deity heritage notes replace the earlier presentation. Scene loading, spawn handling, lighting, decorative collisions and release resource packaging improved.

## Validation and evidence

The Up arrow route tests cover both Madurai sanctuary approaches, Jwalamukhi's flame chamber and stairs, Sharada's western ascent, Draksharamam's upper stair, and Kamakhya's western approach and cave floor. All four arrow bindings were checked separately. The general arrival probes cover about nine metres per site. Test scripts include `godot/scripts/test_player.gd`, `qa_worlds.gd`, `qa_routes.gd`, `qa_shrines.gd`, `verify_present_day_routes.gd`, `verify_presentation.gd` and `qa_release.gd`. Logs are in `output/review/`. Earlier independent model views are in `godot/screenshots/audit/`.

## Research and limits

The 51-page architecture and deity PDF and primary research files are under `research/2026-11-16/`. Main-murti uncertainties and reconstruction caveats ship in `godot/data/reference_notes.json`.

The playable collection covers the traditional eighteen names plus Kalighat, Madurai and Tuljapur. Pandua uses the minaret and mosque ruins from Archaeological Survey of India records. The historic Shrinkhala shrine's location remains unresolved. At Madurai the footprint, gate axes and eight named Ashta Shakti figures follow the published references. Exact installed deity finishes, lesser shrine positions, and the complete inventory of carvings, paintings and inscriptions still need further review across the collection.

Kolhapur's roof axis and footprint follow the Esri aerial. The lower and upper plans are based on Prabhudesai's field survey and the adjoining shrine bays follow the numbered precinct diagram. The metadata records documented inscriptions in the western approach, at Navagraha Mandapa and near the east gate. Installed secondary art, ceiling relief motifs, epigraphy and the exact north court levels need further field verification. Some mapped shrines are documented bays without a reproduced installed image.

The remaining source asset anchor gaps are four at Jajpur and one each at Pithapuram, Ujjain and Draksharamam. A successful teleport alone establishes landing safety.

GitHub origin is configured. Publication uses a fresh `codex/publish-preview` source snapshot targeting remote `main`; earlier local history is retained on `codex/complex-shrines-navigation`. The old audio generator contained a hard-coded credential, removed from current source; never publish it through previous history. Credentials now come from the environment. Generated narration is local MP3; API credentials must never ship in the game. Builds and downloaded research media remain local.

Finished Gemini baseline sources/models/handoff are preserved in `output/review/gemini_baseline.zip`, with SHA256 manifest beside it. Do not revert unrelated user changes or generated research.
