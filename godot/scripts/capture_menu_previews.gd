extends SceneTree

func _initialize() -> void:
	call_deferred("capture")

func bounds_of(node: Node) -> AABB:
	var bounds = AABB()
	if node is MeshInstance3D and not ("ground" in str(node.name).to_lower() or "terrain" in str(node.name).to_lower()):
		bounds = node.global_transform * node.get_aabb()
	for child in node.get_children():
		var child_bounds = bounds_of(child)
		if child_bounds.size != Vector3.ZERO:
			bounds = child_bounds if bounds.size == Vector3.ZERO else bounds.merge(child_bounds)
	return bounds

func capture() -> void:
	root.size = Vector2i(560, 300)
	var world = Node3D.new()
	root.add_child(world)
	var we = WorldEnvironment.new()
	var env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("506869")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("a8bab2")
	env.ambient_light_energy = 0.7
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	we.environment = env
	world.add_child(we)
	var sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-42, -40, 0)
	sun.light_color = Color("ffdfb5")
	sun.light_energy = 1.5
	sun.shadow_enabled = true
	world.add_child(sun)
	var camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.current = true
	camera.far = 800
	world.add_child(camera)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://assets/ui/previews"))
	for filename in DirAccess.get_files_at("res://assets/models"):
		if not filename.ends_with("_kshetra_full.glb"):
			continue
		var id = filename.trim_suffix("_kshetra_full.glb")
		var selected = OS.get_cmdline_user_args()
		if not selected.is_empty() and id != selected[0]:
			continue
		var doc = GLTFDocument.new()
		var state = GLTFState.new()
		if doc.append_from_file("res://assets/models/" + filename, state) != OK:
			continue
		var model = doc.generate_scene(state)
		world.add_child(model)
		var box = bounds_of(model)
		var center = box.get_center()
		var span = maxf(box.size.x, box.size.z)
		camera.size = maxf(20, maxf(span * 1.2, box.size.y * 1.5))
		camera.position = center + Vector3(span * 0.55, span * 0.55, span * 0.7)
		camera.look_at(center)
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_jpg("res://assets/ui/previews/%s.jpg" % id, 0.88)
		print("PREVIEW ", id)
		model.free()
	quit()
