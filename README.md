# Kshetra Darshan

A Godot 4.7.1 pilgrimage exploration prototype with original procedural temple models authored through Blender 5.3.

The preview includes 21 scenes representing the traditional eighteen Shakti Peetha names plus Kalighat, Madurai and Tuljapur. It has 133 mapped destinations, searchable shrine teleports, deity/tradition notes, day and night lighting, animated birds, and recorded chants and guide narration.

This is **not an AAA or surveyed reconstruction**. Layouts and many subsidiary positions are schematic. Some Peetha identifications vary by tradition. Thirty-four subsidiary entries remain reference altars; installed-image matching, main-deity refinement, and inscription/building-sculpture preservation are incomplete. Sharada is represented as roofless ruins; Pandua's monuments are distinguished from its uncertain Shrinkhala association.

## Run

Import `godot/project.godot` in Godot 4.7.1 and run the project. Importing the bundled GLBs may take a few minutes. Windows export configuration is included; generated distributions and engine caches are excluded from source control.

Controls: WASD move, mouse look, Space jump, Shift sprint, V first/third person, P prayer, K Pranam, M shrine map and teleports, H heritage guide, N chant, B sound, 1–5 time presets. The selected shrine panel offers guide playback where a recording exists.

## Sources and fidelity

See [current implementation and limitations](research/2026-11-16/CURRENT_IMPLEMENTATION.md), [present-condition scene references](research/2026-11-16/present_day_sites/README.md), and [handoff](handoff.md). Source photographs were used for research; downloaded research media are not distributed as game textures. Original iconographic studies are distinguished from authenticated installed images.

The research catalogue is a documented working subset, not a guarantee of every shrine within every complex. No invented inscriptions have been added to fill gaps.

## Development and checks

Blender builders live in `blender/`; `scripts/rebuild_all_temples.py` runs the scene rebuild pipeline. Godot scripts in `godot/scripts/qa_*.gd`, `test_*.gd`, and `verify_*.gd` cover navigation, labels, movement, guide playback and rendering. Review checks passed for 21 scenes, 133 destination landings/labels, short arrival routes, two complete stair approaches and exported resources. These checks establish runtime behavior, not historical authenticity.

Audio generation scripts use `ELEVENLABS_API_KEY` from the local environment and the existing configured project voice. Credentials must never be placed in source or shipped to the game client. Generated recordings are included for playback; API access is only used during development.
