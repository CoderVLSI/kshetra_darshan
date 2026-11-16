extends SceneTree

# Isolated model inspection: no gameplay scene, singleton selection, or HUD.
func _initialize() -> void:
	call_deferred("capture_all")

func capture_all() -> void:
	root.size = Vector2i(1100, 850)
	var world = Node3D.new()
	root.add_child(world)
	var environment = WorldEnvironment.new()
	var env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.16, 0.19, 0.23)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.WHITE
	env.ambient_light_energy = 0.75
	environment.environment = env
	world.add_child(environment)
	var sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -25, 0)
	sun.light_energy = 1.0
	world.add_child(sun)
	var camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	world.add_child(camera)
	camera.current = true
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://screenshots/audit"))
	for file in DirAccess.get_files_at("res://assets/models"):
		if not file.ends_with("_kshetra_full.glb"):
			continue
		var id = file.trim_suffix("_kshetra_full.glb")
		var selected = OS.get_cmdline_user_args()
		if not selected.is_empty() and id != selected[0]:
			continue
		var doc = GLTFDocument.new()
		var state = GLTFState.new()
		if doc.append_from_file("res://assets/models/" + file, state) != OK:
			continue
		var model = doc.generate_scene(state)
		world.add_child(model)
		var bounds = get_bounds(model)
		var center = bounds.get_center()
		var span = max(bounds.size.x, bounds.size.z)
		camera.size = max(span * 0.9, 40.0)
		camera.far = 1000
		for view in ["overhead", "oblique"]:
			var offset = Vector3(0, span * 1.6, 0.01) if view == "overhead" else Vector3(span * 0.65, span * 0.85, span * 0.8)
			camera.position = center + offset
			camera.look_at(center)
			await process_frame
			await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png("res://screenshots/audit/%s_%s.png" % [id, view])
		print("AUDIT CAPTURED ", id)
		model.free()
	quit()

func get_bounds(node: Node) -> AABB:
	var result = AABB()
	if node is MeshInstance3D:
		result = node.global_transform * node.get_aabb()
	for child in node.get_children():
		var bounds = get_bounds(child)
		if bounds.size != Vector3.ZERO:
			result = bounds if result.size == Vector3.ZERO else result.merge(bounds)
	return result
