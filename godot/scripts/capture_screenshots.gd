extends SceneTree

## Visual Capture Script for QA Verification
## Captures screenshots of Main Menu, authentic Garbhagrihas, and the human devotee character at 1280x720.

var frame_count: int = 0
var stage: int = 0
var current_scene_node: Node = null

func _init() -> void:
	print("Starting Visual Capture Script at 1280x720...")

func _process(_delta: float) -> bool:
	frame_count += 1
	
	if stage == 0 and frame_count == 2:
		# Stage 0: Main Menu 18-Card Grid
		print("Capturing Main Menu...")
		var menu_res = load("res://scenes/main_menu.tscn")
		current_scene_node = menu_res.instantiate()
		root.add_child(current_scene_node)
		
	elif stage == 0 and frame_count >= 15:
		_save_screenshot("res://screenshots/screenshot_main_menu.png")
		if current_scene_node:
			current_scene_node.queue_free()
			current_scene_node = null
		stage = 1
		frame_count = 0
		
	elif stage == 1 and frame_count == 2:
		# Stage 1: Kamakhya Subterranean Bedrock Cave & Swayambhu Yoni Peetha
		print("Capturing Kamakhya Subterranean Cave & Yoni Peetha...")
		_setup_temple_stage("kamakhya",
			Vector3(-0.85, -2.2, -11.5),
			Vector3(0.0, -1.3, -10.2),
			Vector3(0.0, -1.9, -13.0))
		
	elif stage == 1 and frame_count >= 20:
		_save_screenshot("res://screenshots/screenshot_garbhagriha_kamakhya.png")
		if current_scene_node:
			current_scene_node.queue_free()
			current_scene_node = null
		stage = 2
		frame_count = 0
		
	elif stage == 2 and frame_count == 2:
		# Stage 2: Kolhapur Mahalakshmi Ambabai & Garuda Mandapa
		print("Capturing Kolhapur Ambabai & Garuda Mandapa...")
		_setup_temple_stage("kolhapur_mahalakshmi",
			Vector3(-0.85, 0.8, -6.8),
			Vector3(0.0, 1.8, -4.5),
			Vector3(0.0, 1.5, -8.5))
		
	elif stage == 2 and frame_count >= 20:
		_save_screenshot("res://screenshots/screenshot_garbhagriha_kolhapur.png")
		if current_scene_node:
			current_scene_node.queue_free()
			current_scene_node = null
		stage = 3
		frame_count = 0
		
	elif stage == 3 and frame_count == 2:
		# Stage 3: Ujjain Mahakali / Harasiddhi Twin Deepastambhas & Sabha Mandap
		print("Capturing Ujjain Twin Deepastambhas & Harasiddhi...")
		_setup_temple_stage("ujjain_mahakali",
			Vector3(-0.9, 0.0, 5.0),
			Vector3(0.0, 2.5, 9.5),
			Vector3(0.0, 3.5, 0.0))
		
	elif stage == 3 and frame_count >= 20:
		_save_screenshot("res://screenshots/screenshot_garbhagriha_ujjain.png")
		if current_scene_node:
			current_scene_node.queue_free()
			current_scene_node = null
		stage = 4
		frame_count = 0
		
	elif stage == 4 and frame_count == 2:
		# Stage 4: Devotee Player Character in Full Anatomical Detail
		print("Capturing Devotee Player Character in Full Anatomical Detail...")
		_setup_temple_stage("kamakhya",
			Vector3(0.0, 0.8, 0.0),
			Vector3(0.35, 1.35, 2.0),
			Vector3(0.0, 1.20, 0.0))
		
		var player_node = current_scene_node.find_child("Player", true, false)
		if player_node:
			# Look North (-Z) so the front of the devotee faces South toward the camera (+Z)
			player_node.look_at(Vector3(0.0, 0.8, -10.0), Vector3.UP)
			player_node.rotation.x = 0
			player_node.rotation.z = 0
			player_node.rotation.y += deg_to_rad(15.0)
			player_node.prayer_timer = 5.0
			
		# Add a warm portrait fill light so the devotee's facial features, tilak, and yajnopavita are clearly illuminated
		var fill_light = OmniLight3D.new()
		fill_light.name = "PortraitFillLight"
		fill_light.light_color = Color(1.0, 0.95, 0.88)
		fill_light.light_energy = 2.5
		fill_light.omni_range = 4.0
		fill_light.global_position = Vector3(0.2, 1.45, 1.5)
		current_scene_node.add_child(fill_light)
				
	elif stage == 4 and frame_count >= 25:
		_save_screenshot("res://screenshots/screenshot_devotee_player.png")
		if current_scene_node:
			current_scene_node.queue_free()
			current_scene_node = null
		print("All visual verification screenshots successfully captured!")
		quit(0)
		return true
		
	return false

func _setup_temple_stage(temple_id: String, player_pos: Vector3, cam_pos: Vector3, target_pos: Vector3) -> void:
	var gm_node = root.get_node_or_null("GameManager")
	if gm_node:
		gm_node.current_temple_id = temple_id
	
	var world_res = load("res://scenes/temple_world.tscn")
	current_scene_node = world_res.instantiate()
	root.add_child(current_scene_node)
	
	if current_scene_node.has_method("load_temple"):
		current_scene_node.load_temple(temple_id)
		
	# Update HUD header
	var header_lbl = current_scene_node.find_child("TempleInfo", true, false) as Label
	if header_lbl and gm_node and gm_node.temples.has(temple_id):
		var t = gm_node.temples[temple_id]
		header_lbl.text = "🏛️ %s   |   📍 %s   |   ⚜️ %s" % [t.get("name", ""), t.get("location", ""), t.get("anga", "")]
	
	# Position player
	var player_node = current_scene_node.find_child("Player", true, false)
	if player_node:
		player_node.global_position = player_pos
		var dir = target_pos - player_pos
		dir.y = 0
		if dir.length_squared() > 0.01:
			player_node.look_at(player_pos + dir, Vector3.UP)
			player_node.rotation.x = 0
			player_node.rotation.z = 0
	
	# Dedicated inspection camera that looks directly at the target
	var cam = Camera3D.new()
	cam.name = "InspectionCamera"
	current_scene_node.add_child(cam)
	cam.global_position = cam_pos
	cam.look_at(target_pos, Vector3.UP)
	cam.current = true

func _save_screenshot(rel_path: String) -> void:
	var img = root.get_texture().get_image()
	if img != null:
		var abs_path = ProjectSettings.globalize_path(rel_path)
		var err = img.save_png(abs_path)
		if err == OK:
			print("Saved: %s (%dx%d)" % [rel_path, img.get_width(), img.get_height()])
		else:
			print("Failed saving: %s, code %d" % [rel_path, err])


