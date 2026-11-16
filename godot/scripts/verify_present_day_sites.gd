extends SceneTree
var failures: Array[String] = []
var sites := ["draksharama_manikyamba", "jwalamukhi_vaishnavi", "kashmir_sharada"]
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	root.size = Vector2i(1280, 720)
	var gm = root.get_node("GameManager")
	gm.mobile_mode = true
	for id in sites:
		gm.current_temple_id = id
		var world = load("res://scenes/temple_world.tscn").instantiate()
		root.add_child(world)
		current_scene = world
		while not world.shrine_registry.is_ready: await physics_frame
		for frame in range(30): await physics_frame
		if not world.player.is_on_floor(): failures.append(id + " spawn not grounded")
		var destinations: Array = world.shrine_registry.get_destinations()
		for d in destinations:
			if not d.available or not world.shrine_registry.teleport_to(d.id):
				failures.append(id + " unavailable destination " + d.id)
				continue
			for frame in range(18): await physics_frame
			if not world.player.is_on_floor(): failures.append(id + " landing not grounded " + d.id)
		print("PRESENT_SITE ",id," destinations=",destinations.size())
		if not DisplayServer.get_name() == "headless":
			world.get_node("UI_HUD").hide()
			world.player.visual_mesh.hide()
			var camera = Camera3D.new()
			world.add_child(camera)
			camera.current = true
			camera.fov = 65
			if id == "kashmir_sharada":
				camera.global_position = Vector3(23, 27, 33)
				camera.look_at(Vector3(0, 11, -2))
			elif id == "jwalamukhi_vaishnavi":
				camera.global_position = Vector3(25, 24, 26)
				camera.look_at(Vector3(-3, 1, -4))
			else:
				camera.global_position = Vector3(35, 29, 38)
				camera.look_at(Vector3(0, 2, -5))
			for frame in range(12): await process_frame
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png("D:/Kshetra_Darshan/output/review/" + id + "_present_day.png")
		current_scene = null
		world.free()
		await process_frame
	for failure in failures: push_error(failure)
	print("PRESENT_SITES_RESULT ",failures.size()," failures")
	OS.delay_msec(80)
	await process_frame
	quit(0 if failures.is_empty() else 1)
