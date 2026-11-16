extends SceneTree
func _initialize() -> void:
	call_deferred("capture")
func capture() -> void:
	root.size = Vector2i(1280, 900)
	root.get_node("GameManager").current_temple_id = "kamakhya"
	var world = load("res://scenes/temple_world.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	world.get_node("UI_HUD").hide()
	world.player.visual_mesh.hide()
	world.player.set_physics_process(false)
	var camera = Camera3D.new()
	world.add_child(camera)
	camera.current = true
	camera.fov = 54
	camera.near = .04
	camera.position = Vector3(0, -.48, -10.25)
	camera.look_at(Vector3(0, -1.67, -13.05))
	var fill = OmniLight3D.new()
	world.add_child(fill)
	fill.position = Vector3(.5, -.5, -11.7)
	fill.light_color = Color(1.0,.83,.62)
	fill.light_energy = 1.0
	fill.omni_range = 5
	for frame in range(16): await process_frame
	await RenderingServer.frame_post_draw
	var path = "D:/Kshetra_Darshan/output/review/kamakhya_main_deity_current.png"
	root.get_texture().get_image().save_png(path)
	print("CAPTURED ",path)
	world.free()
	OS.delay_msec(80)
	await process_frame
	quit()
