# Kshetra Darshan handoff

Updated 20 November 2026 after the Kamakhya rebuild.

Current status is a playable procedural preview with 21 scenes and 249 mapped destinations. Kamakhya has 20 named stops in the main compound. Its west-facing hall sequence and descent to the shared cave follow the published measured plan, and the two kunds have separate map destinations. Srisailam has 45 named stops in its satellite-led enclosure, including both principal sanctuaries, the Sri Chakra, the Pancha Sivalaya and Nava Brahma rows, four gateways and three ritual springs. Exact installed images, inscriptions and building sculptures still need site-by-site review. The files under `research/2026-11-16/` record the earlier audit, and `godot/data/reference_notes.json` contains the sources and limits for the current scenes.

## Run

- Latest Windows preview: `builds/windows/AshtaDashaShaktiPeetha.exe`, with `AshtaDashaShaktiPeetha.pck` beside it. The older reviewed build is retained separately.
- Original Gemini distribution retained in `builds/windows/`.
- Project: `godot/project.godot` (Godot4.7.1); Blender builders in `blender/` (Blender5.3).
- Desktop controls: WASD or arrow keys move, Space jump, Shift sprint, mouse look, Esc release/capture cursor, V first/third person, P prayer, K forward Pranam, F flowers, G bell, R aarti, T prasadam, C conch, N mantra, B sound, H heritage, M searchable shrine map/teleports, 1–5 time presets. Five selected shrine details offer narration in the existing project voice.

## What changed

Player now faces away from the rear camera, rests with relaxed arms, and joins palms only during P prayer. Walking limbs and safe step-up are implemented. Eighteen existing models rebuilt with corrected architectural dimensions, connected walls/tiers/stairs and exported stone detail. Specific cave/plateau/approach defects repaired. Renuka face-form and Shrinkhala uncertainty corrected. Searchable responsive menu, actual previews, model map and sourced main-deity heritage notes replace the earlier presentation. Scene loading, spawn handling, lighting, decorative collisions and release resource packaging improved.

## Validation and evidence

Kamakhya's western approach, hall sequence and descent to the cave floor were exercised by walking with the Up arrow. All four arrow bindings were checked separately. The general arrival probes cover about nine metres per site. Test scripts include `godot/scripts/test_player.gd`, `qa_worlds.gd`, `qa_routes.gd`, `qa_shrines.gd`, `verify_presentation.gd` and `qa_release.gd`. Logs are in `output/review/`. Earlier independent model views are in `godot/screenshots/audit/`.

## Research and limits

The51-page architecture/deity PDF and primary research files are under `research/2026-11-16/`. Main-murti uncertainties and reconstruction caveats ship in `godot/data/reference_notes.json`.

Playable collection: the traditional eighteen names plus Kalighat, Madurai and Tuljapur. The added Draksharamam, Jwalamukhi and roofless Sharada scenes are approximate present-condition studies. Pandua's hypothetical temple was replaced with an ASI-reference minaret/mosque-ruin study; no intact original Shrinkhala shrine is asserted. Current layouts and artwork remain schematic. Temple-specific high-quality architecture, installed deity artwork, and object-level carvings/epigraphy still need substantial work. Names, dimensions and passing navigation tests are not proof of authenticity.

GitHub origin is configured. Publication uses a fresh `codex/publish-preview` source snapshot targeting remote `main`; earlier local history is retained on `codex/complex-shrines-navigation`. The old audio generator contained a hard-coded credential, removed from current source; never publish it through previous history. Credentials now come from the environment. Generated narration is local MP3; API credentials must never ship in the game. Builds and downloaded research media remain local.

Finished Gemini baseline sources/models/handoff are preserved in `output/review/gemini_baseline.zip`, with SHA256 manifest beside it. Do not revert unrelated user changes or generated research.
