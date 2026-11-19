extends Node3D

## TempleWorld
## Manages 3D temple scene loading, mesh collision generation, player spawning,
## sky/lighting presets (1-5: Dawn, Day, Afternoon, Sunset, Night), and sacred atmosphere.

@onready var world_env: WorldEnvironment = $WorldEnvironment
@onready var sun_light: DirectionalLight3D = $SunLight
@onready var temple_holder: Node3D = $TempleModelHolder
@onready var player: CharacterBody3D = $Player
@onready var hud: Control = $UI_HUD/HUDRoot
@onready var ambient_audio: AudioStreamPlayer = $AmbientAudio
@onready var sfx_audio: AudioStreamPlayer = $SFXAudio

var current_sky_preset: int = 2 # Default to Midday
var model_instance: Node = null
var spawn_position := Vector3.ZERO
var sanctum_lights: Node3D
var shrine_registry: Node3D
var atmosphere: Node3D
var daylight_fill: DirectionalLight3D

func _physics_process(_delta: float) -> void:
	# Recover from an accidental drop beyond the authored terrain.
	if player and player.global_position.y < spawn_position.y - 25.0:
		player.global_position = spawn_position
		player.velocity = Vector3.ZERO

func _exit_tree() -> void:
	# Release active procedural playback before the scene's audio nodes leave
	# the tree, including during rapid destination changes and application exit.
	for audio in [ambient_audio, sfx_audio]:
		if is_instance_valid(audio):
			audio.stop()
			audio.stream = null

# Sky Presets definition
const SKY_PRESETS = {
	1: {
		"name": "Dawn (Pratah-Kala / Nirmalya Darshan)",
		"sun_rotation": Vector3(-12.0, 70.0, 0.0),
		"sun_color": Color(1.0, 0.78, 0.58),
		"sun_energy": 0.85,
		"ambient_color": Color(0.38, 0.32, 0.35),
		"ambient_energy": 0.30,
		"sky_top": Color(0.25, 0.40, 0.70),
		"sky_horizon": Color(0.95, 0.65, 0.48),
		"ground_bottom": Color(0.18, 0.15, 0.20),
		"ground_horizon": Color(0.65, 0.45, 0.35),
		"fog_enabled": true,
		"fog_color": Color(0.90, 0.70, 0.55),
		"fog_density": 0.002
	},
	2: {
		"name": "Midday (Madhyahna / Abhijit Muhurta)",
		"sun_rotation": Vector3(-65.0, 45.0, 0.0),
		"sun_color": Color(1.0, 0.96, 0.88),
		"sun_energy": 0.95,
		"ambient_color": Color(0.40, 0.38, 0.35),
		"ambient_energy": 0.35,
		"sky_top": Color(0.18, 0.45, 0.82),
		"sky_horizon": Color(0.68, 0.78, 0.90),
		"ground_bottom": Color(0.20, 0.20, 0.18),
		"ground_horizon": Color(0.55, 0.52, 0.48),
		"fog_enabled": false,
		"fog_color": Color(0.7, 0.75, 0.85),
		"fog_density": 0.001
	},
	3: {
		"name": "Afternoon (Aparahna)",
		"sun_rotation": Vector3(-35.0, 115.0, 0.0),
		"sun_color": Color(1.0, 0.85, 0.65),
		"sun_energy": 0.90,
		"ambient_color": Color(0.42, 0.38, 0.32),
		"ambient_energy": 0.32,
		"sky_top": Color(0.22, 0.42, 0.75),
		"sky_horizon": Color(0.85, 0.72, 0.55),
		"ground_bottom": Color(0.20, 0.18, 0.16),
		"ground_horizon": Color(0.60, 0.52, 0.42),
		"fog_enabled": false,
		"fog_color": Color(0.75, 0.68, 0.58),
		"fog_density": 0.001
	},
	4: {
		"name": "Sunset (Sandhya-Kala / Pradosham)",
		"sun_rotation": Vector3(-6.0, 165.0, 0.0),
		"sun_color": Color(1.0, 0.48, 0.18),
		"sun_energy": 0.75,
		"ambient_color": Color(0.35, 0.22, 0.25),
		"ambient_energy": 0.28,
		"sky_top": Color(0.20, 0.18, 0.45),
		"sky_horizon": Color(0.96, 0.45, 0.20),
		"ground_bottom": Color(0.12, 0.10, 0.15),
		"ground_horizon": Color(0.55, 0.25, 0.18),
		"fog_enabled": true,
		"fog_color": Color(0.82, 0.38, 0.26),
		"fog_density": 0.003
	},
	5: {
		"name": "Night (Nisha-Kala / Deepotsava Aarti)",
		"sun_rotation": Vector3(-45.0, -110.0, 0.0),
		"sun_color": Color(0.35, 0.45, 0.75),
		"sun_energy": 0.15,
		"ambient_color": Color(0.10, 0.12, 0.20),
		"ambient_energy": 0.22,
		"sky_top": Color(0.03, 0.04, 0.10),
		"sky_horizon": Color(0.06, 0.08, 0.16),
		"ground_bottom": Color(0.02, 0.02, 0.04),
		"ground_horizon": Color(0.05, 0.06, 0.10),
		"fog_enabled": true,
		"fog_color": Color(0.05, 0.07, 0.15),
		"fog_density": 0.004
	}
}

func _ready() -> void:
	load_temple(GameManager.current_temple_id)
	apply_sky_preset(current_sky_preset)
	_setup_audio()
	
	if GameManager:
		GameManager.temple_changed.connect(_on_temple_changed)
		GameManager.seva_action_performed.connect(_on_seva_action)
		GameManager.sound_toggled.connect(_on_sound_toggled)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1:
				apply_sky_preset(1)
			KEY_2:
				apply_sky_preset(2)
			KEY_3:
				apply_sky_preset(3)
			KEY_4:
				apply_sky_preset(4)
			KEY_5:
				apply_sky_preset(5)

func _on_temple_changed(new_id: String) -> void:
	load_temple(new_id)

func load_temple(temple_id: String) -> void:
	# Clear previous model
	if model_instance != null and is_instance_valid(model_instance):
		# Remove physics bodies immediately before placing the next model.
		temple_holder.remove_child(model_instance)
		model_instance.queue_free()
		model_instance = null
	if is_instance_valid(sanctum_lights):
		sanctum_lights.queue_free()
	
	for previous in [shrine_registry, atmosphere, daylight_fill]:
		if is_instance_valid(previous):
			remove_child(previous)
			previous.queue_free()
	var glb_rel_path = "res://assets/models/%s_kshetra_full.glb" % temple_id
	var glb_abs_path = ProjectSettings.globalize_path(glb_rel_path)
	var loaded_node: Node = null
	
	# Prefer Godot's imported PackedScene: avoids reparsing GLTF and creating
	# transient meshes on every visit; works with exported resource packs.
	if ResourceLoader.exists(glb_rel_path):
		var packed = load(glb_rel_path) as PackedScene
		if packed:
			loaded_node = packed.instantiate()
	elif FileAccess.file_exists(glb_rel_path) or FileAccess.file_exists(glb_abs_path):
		var target_path = glb_rel_path if FileAccess.file_exists(glb_rel_path) else glb_abs_path
		var gltf = GLTFDocument.new()
		var state = GLTFState.new()
		var err = gltf.append_from_file(target_path, state)
		if err == OK:
			loaded_node = gltf.generate_scene(state)
	
	if loaded_node == null:
		push_error("Temple model could not be loaded: %s" % temple_id)
		# A different generic sanctum must never silently stand in for a site.
		GameManager.call_deferred("go_to_menu")
		return
	
	model_instance = loaded_node
	temple_holder.add_child(model_instance)
	
	# Generate collision shapes for meshes
	generate_mesh_collisions(model_instance)
	_setup_sanctum_lighting()
	atmosphere = load("res://scripts/temple_atmosphere.gd").new()
	atmosphere.name = "TempleAtmosphere"
	add_child(atmosphere)
	atmosphere.setup(model_instance, world_env.environment)
	daylight_fill = DirectionalLight3D.new()
	daylight_fill.name = "CourtyardBounce"
	daylight_fill.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_ONLY
	daylight_fill.light_specular = 0.0
	daylight_fill.shadow_enabled = false
	add_child(daylight_fill)
	
	# Position player at Spawn_Point
	var spawn_node = _find_node_fuzzy(model_instance, "Spawn")
	if spawn_node is Node3D:
		player.global_position = spawn_node.global_position + Vector3(0, 0.4, 0)
	else:
		player.global_position = Vector3(0, 1.2, 16.0)
	player.velocity = Vector3.ZERO
	spawn_position = player.global_position
	var deity = _find_node_fuzzy(model_instance, "Deity") as Node3D
	if not deity:
		var primary_anchor = {"jwalamukhi_vaishnavi": "SacredFlame_Mahakali", "draksharama_manikyamba": "Bhimeswara_Linga"}
		if primary_anchor.has(GameManager.current_temple_id):
			deity = _find_node_fuzzy(model_instance, primary_anchor[GameManager.current_temple_id]) as Node3D
	var arrival_facing := model_instance.find_child("Arrival_Facing", true, false) as Node3D
	var arrival_target = arrival_facing if arrival_facing else deity
	if arrival_target:
		var target = arrival_target.global_position
		target.y = player.global_position.y
		if player.global_position.distance_to(target) > .1:
			player.look_at(target)
	player.rotation.x = 0
	player.rotation.z = 0
	if hud and hud.has_method("_rebuild_model_map"):
		hud._rebuild_model_map()
	shrine_registry = load("res://scripts/shrine_registry.gd").new()
	shrine_registry.name = "ShrineRegistry"
	add_child(shrine_registry)
	shrine_registry.setup(temple_id, model_instance, player)

func generate_mesh_collisions(root: Node) -> void:
	if root is MeshInstance3D:
		var mi = root as MeshInstance3D
		var mesh_name = String(mi.name).to_lower()
		# Decorative surfaces and water are not invisible barriers to a pilgrim.
		for tag in ["flame", "garland", "flower", "water", "priest", "cloth", "silk", "ornamentdetail"]:
			if tag in mesh_name:
				return
		if mi.mesh != null and mi.mesh.get_faces().size() > 0:
			var parent = mi.get_parent()
			var already_has_collision = false
			if parent is StaticBody3D:
				already_has_collision = true
			else:
				for child in mi.get_children():
					if child is StaticBody3D:
						already_has_collision = true
						break
			if not already_has_collision:
				mi.create_trimesh_collision()
	
	for child in root.get_children():
		generate_mesh_collisions(child)

func _setup_sanctum_lighting() -> void:
	# A restrained warm practical fill keeps the sacred form readable indoors.
	# No extra masonry or speculative shrine positions are added here.
	sanctum_lights = Node3D.new()
	sanctum_lights.name = "InteriorLighting"
	add_child(sanctum_lights)
	var deity = _find_node_fuzzy(model_instance, "Deity") as Node3D
	if not deity:
		var anchor_names = {"jwalamukhi_vaishnavi": "SacredFlame_Mahakali", "draksharama_manikyamba": "Bhimeswara_Linga"}
		if anchor_names.has(GameManager.current_temple_id):
			deity = _find_node_fuzzy(model_instance, anchor_names[GameManager.current_temple_id]) as Node3D
	if deity:
		var light = OmniLight3D.new()
		light.name = "SanctumLampFill"
		light.light_color = Color(1.0, .69, .38)
		light.light_energy = 1.5
		light.omni_range = 6.0
		light.omni_attenuation = 1.5
		sanctum_lights.add_child(light)
		var lamp_position := model_instance.find_child("Sanctum_Lamp_Position", true, false) as Node3D
		light.global_position = lamp_position.global_position if lamp_position else deity.global_position + Vector3(0, 1.8, 1.0)
	if GameManager.current_temple_id == "draksharama_manikyamba":
		var devi_location = _find_node_fuzzy(model_instance, "Manikyamba_Main_Reference") as Node3D
		if devi_location:
			var lamp = OmniLight3D.new()
			lamp.light_color = Color(1.0, .78, .52)
			lamp.light_energy = 1.1
			lamp.omni_range = 5.0
			sanctum_lights.add_child(lamp)
			lamp.global_position = devi_location.global_position + Vector3(0, 1.5, 1)

func apply_sky_preset(index: int) -> void:
	if not SKY_PRESETS.has(index):
		return
	current_sky_preset = index
	var preset: Dictionary = SKY_PRESETS[index]
	
	# Update Sun Direction and Color
	var rot_deg: Vector3 = preset["sun_rotation"]
	sun_light.rotation_degrees = rot_deg
	sun_light.light_color = preset["sun_color"]
	sun_light.light_energy = preset["sun_energy"]
	if is_instance_valid(daylight_fill):
		daylight_fill.rotation_degrees = Vector3(-38, rot_deg.y + 180.0, 0)
		daylight_fill.light_color = Color(.72, .80, 1.0)
		daylight_fill.light_energy = .20 if index == 2 or index == 3 else (.035 if index == 5 else .10)
	if is_instance_valid(atmosphere):
		atmosphere.set_preset(preset, index)
	
	# Update World Environment Sky
	if world_env and world_env.environment:
		var env = world_env.environment
		env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
		env.ambient_light_color = preset["ambient_color"]
		env.ambient_light_energy = preset["ambient_energy"]
		# Daylight bounce must preserve detail on the shaded entrance facade.
		if index == 2 or index == 3:
			env.ambient_light_color = preset["ambient_color"].lerp(Color(.82, .85, .9), .5)
			env.ambient_light_energy = .65
		
		if env.sky and env.sky.sky_material is ProceduralSkyMaterial:
			var mat = env.sky.sky_material as ProceduralSkyMaterial
			mat.sky_top_color = preset["sky_top"]
			mat.sky_horizon_color = preset["sky_horizon"]
			mat.ground_bottom_color = preset["ground_bottom"]
			mat.ground_horizon_color = preset["ground_horizon"]
		
		# Volumetric Fog / Distance Fog
		if env.has_method("set_fog_enabled"):
			env.fog_enabled = preset["fog_enabled"]
			env.fog_light_color = preset["fog_color"]
			env.fog_density = preset["fog_density"]
	
	if hud and hud.has_method("notify_sky_preset"):
		hud.notify_sky_preset(index, preset["name"])

func _setup_audio() -> void:
	# Generate ambient temple drone
	if ambient_audio:
		ambient_audio.stream = _create_drone_wav()
		ambient_audio.volume_db = -12.0
		ambient_audio.autoplay = true
		ambient_audio.play()

func _on_seva_action(action_name: String, _title: String, _msg: String) -> void:
	if not GameManager.sound_enabled:
		return
	match action_name:
		"ring_bell":
			if sfx_audio:
				sfx_audio.stream = _create_bell_wav()
				sfx_audio.volume_db = -4.0
				sfx_audio.play()
		"conch":
			if sfx_audio:
				sfx_audio.stream = _create_conch_wav()
				sfx_audio.volume_db = -2.0
				sfx_audio.play()
		"mantra":
			if sfx_audio:
				var mantra_res = "res://assets/audio/mantra_%s.mp3" % GameManager.current_temple_id
				if ResourceLoader.exists(mantra_res):
					sfx_audio.stream = load(mantra_res)
					sfx_audio.volume_db = 2.0
					sfx_audio.play()

func _on_sound_toggled(enabled: bool) -> void:
	if ambient_audio:
		ambient_audio.stream_paused = not enabled

func _find_node_fuzzy(root: Node, text: String) -> Node:
	if root == null:
		return null
	if text.to_lower() in root.name.to_lower():
		return root
	for child in root.get_children():
		var found = _find_node_fuzzy(child, text)
		if found != null:
			return found
	return null

# Procedural audio synthesis for sacred temple ambiance
func _create_drone_wav() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	wav.stereo = false
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	wav.loop_begin = 0
	wav.loop_end = 22050 * 2
	
	var length_seconds = 2.0
	var num_samples = int(22050 * length_seconds)
	var data = PackedByteArray()
	data.resize(num_samples * 2)
	
	# Gentle warm Tanpura drone: Sa (130.8 Hz) and Pa (196.0 Hz)
	for i in range(num_samples):
		var t = float(i) / 22050.0
		var s1 = sin(2.0 * PI * 130.81 * t) * 0.45
		var s2 = sin(2.0 * PI * 196.00 * t) * 0.35
		var s3 = sin(2.0 * PI * 261.63 * t) * 0.20
		var sample_f = (s1 + s2 + s3) * 0.35
		var s16 = int(clamp(sample_f * 32767.0, -32767, 32767))
		data.encode_s16(i * 2, s16)
	
	wav.data = data
	return wav

func _create_bell_wav() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	wav.stereo = false
	var length_seconds = 1.8
	var num_samples = int(22050 * length_seconds)
	var data = PackedByteArray()
	data.resize(num_samples * 2)
	
	# Temple brass bell frequencies: 1175Hz, 2350Hz, 3520Hz with exponential decay
	for i in range(num_samples):
		var t = float(i) / 22050.0
		var decay = exp(-3.2 * t)
		var val = (sin(2.0 * PI * 1174.6 * t) * 0.60 + sin(2.0 * PI * 2349.3 * t) * 0.25 + sin(2.0 * PI * 3520.0 * t) * 0.15) * decay
		var s16 = int(clamp(val * 32767.0 * 0.75, -32767, 32767))
		data.encode_s16(i * 2, s16)
	
	wav.data = data
	return wav

func _create_conch_wav() -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	wav.stereo = false
	var length_seconds = 2.4
	var num_samples = int(22050 * length_seconds)
	var data = PackedByteArray()
	data.resize(num_samples * 2)
	
	# Resonant Shankha sound (around 293 Hz D4 with subtle vibrato and crescendo)
	for i in range(num_samples):
		var t = float(i) / 22050.0
		var envelope = 1.0
		if t < 0.35:
			envelope = t / 0.35
		else:
			envelope = exp(-1.1 * (t - 0.35))
		var vibrato = sin(2.0 * PI * 5.0 * t) * 3.0
		var freq = 293.66 + vibrato
		var val = (sin(2.0 * PI * freq * t) * 0.65 + sin(2.0 * PI * (freq * 2.0) * t) * 0.25 + sin(2.0 * PI * (freq * 3.0) * t) * 0.10) * envelope
		var s16 = int(clamp(val * 32767.0 * 0.8, -32767, 32767))
		data.encode_s16(i * 2, s16)
	
	wav.data = data
	return wav
