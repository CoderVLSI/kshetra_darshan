# Review procedure after Gemini completes

Prepared 16 November 2026. Research artifacts only; do not begin model or gameplay corrections while Gemini is working.

## 1. Establish the final baseline

- Wait for an explicit completion report from Gemini or the user. A quiet filesystem is not proof of completion.
- Read the final handoff and inspect the final diff. Preserve all existing user/agent changes.
- Record the final builder and GLB hashes. The earlier inspection screenshots describe a pre-completion snapshot and may be stale.
- Confirm whether the product retains the current eighteen destinations or adopts the stotram eighteen. Keep the three additional destinations as optional content unless their removal is authorized.

## 2. Check the highest-impact errors first

| Priority | Check | Evidence needed |
|---|---|---|
| P0 | Destination identity and correct site | Stotram plus primary location source; no Samalkota/Draksharamam, Sringeri/Kashmir, or Alopi/Lalita mix-ups |
| P0 | Exported material colours | Inspect final GLB material factors/textures in Godot; earlier Madurai granite and paving lacked base colour and appeared white |
| P0 | Shared geometry dimensions | Verify unit-cube dimensions versus scale. Several existing builders use cube size=1 with half-dimension scale, leaving undersized parts |
| P0 | Screenshot identity | Fresh independently loaded model for each ID; retain temple ID in metadata; earlier Madurai and Kamakhya PNG hashes were identical |
| P1 | Actual compound footprint | North-up overhead view, outer boundary, entry axis and verified scale reference |
| P1 | Connected halls and sanctuaries | Trace entrance to main sanctum and circumambulation; no floating capitals or disconnected walls |
| P1 | Shrine inventory and placement | Match each modelled shrine to an inventory record and a plan/photo; keep nearby regional sites separate |
| P1 | Main sacred form | Seated Kamakshi; two-armed Biraja; Renuka face/head; Alopi cradle; Jwala flames; symbolic Mangala Gauri; Kamakhya cave evidence |
| P1 | Lost or ruined sites | Shrinkhala reconstruction labelled hypothetical; Sharada present ruins separate from historical reconstruction |
| P2 | Roof family and silhouette | Nilachala vs atchala vs Dravidian vs Kalinga vs Kashmiri; match roof hierarchy and period |
| P2 | Urban/terrain context | Kashi lanes, Mahur/Chamundi/Gaya hills, Koneswaram cliff, Srisailam enclosed complex |
| P2 | Real minimap | Trace verified building boundaries, doors, halls, tanks and player route; current radar dots are not a floor plan |
| P3 | Decoration and visual polish | Correct materials, carvings, weathering, lamps and vegetation after footprint/scale/circulation are correct |

## 3. Geometry and evidence workflow

For each temple: select a dated reference baseline; authenticate exact site; mark north and coordinate frame; obtain a measurable plan; draw a labelled footprint; map main and subsidiary shrines; build a simple connected blockout; compare overhead and street-height views; verify material export; then add detail.

Do not infer interior doors or shrine identity from roofs alone. Satellite imagery dates may differ across tiles. Queues, festival tents, scaffolding and proposed corridor renderings must not silently become permanent historical architecture. Google Maps place coordinates are lookup pins, not surveyed control points.

## 4. Acceptance record per temple

Record model hash, builder hash, reference URLs/dates, footprint source, north source, scale source, main shrine form, each subsidiary shrine with scope and evidence, unresolved reconstruction choices, overhead capture, four exterior views, playable route and final review outcome. Use 'unverified' when evidence is absent.

A GLB node-name smoke test establishes structural loading only. It does not certify architectural, historical, devotional or navigational accuracy.

