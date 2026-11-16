extends SceneTree

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	root.size = Vector2i(1280, 720)
	var scene = load("res://scenes/temple_world.tscn").instantiate()
	scene.set_script(null)
	scene.get_node("UI_HUD").visible = false
	scene.get_node("UI_HUD/HUDRoot").set_script(null)
	root.add_child(scene)
	var player = scene.get_node("Player")
	player.position = Vector3.ZERO
	player.set_physics_process(false)
	var env: Environment = scene.get_node("WorldEnvironment").environment
	env.ambient_light_energy = 0.75
	var sun: DirectionalLight3D = scene.get_node("SunLight")
	sun.rotation_degrees = Vector3(-40, 20, 0)
	sun.light_energy = 1.2
	var floor_mesh = MeshInstance3D.new()
	floor_mesh.mesh = PlaneMesh.new()
	floor_mesh.mesh.size = Vector2(20, 20)
	var floor_mat = StandardMaterial3D.new()
	floor_mat.albedo_color = Color(0.22,0.25,0.22)
	floor_mesh.material_override = floor_mat
	scene.add_child(floor_mesh)
	var cam = Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	cam.fov = 40
	var out = ProjectSettings.globalize_path("res://../output/review/player")
	DirAccess.make_dir_recursive_absolute(out)
	for pose in ["idle_back", "idle_front", "prayer_front", "returned_front", "walk_back"]:
		player.prayer_timer = 3.5 if pose == "prayer_front" else 0.0
		for i in range(30):
			player._update_character_animation(1.0/60, false)
		if pose == "walk_back":
			player.walk_anim_phase = PI * 0.5
			player._update_limb_pose(1.0)
		cam.position = Vector3(0,1.25,3.2 if pose.ends_with("back") else -3.2)
		cam.look_at(Vector3(0,.95,0))
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(out.path_join(pose + ".png"))
		var left = player.arm_joints["L"]["hand"]
		var right = player.arm_joints["R"]["hand"]
		print("PLAYER_POSE ", pose, " blend=", player.prayer_blend, " palm_gap=", absf(left.position.x-right.position.x)-0.036)
	print("PLAYER_CAPTURE_COMPLETE")
	quit()
