extends SceneTree
var failures: Array[String] = []
func _initialize() -> void:
	call_deferred("run")
func check(ok: bool, message: String) -> void:
	if not ok: failures.append(message)
func run() -> void:
	root.size = Vector2i(1280,720)
	var gm = root.get_node("GameManager")
	gm.current_temple_id = "kanchipuram_kamakshi"
	var world = load("res://scenes/temple_world.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	while not world.shrine_registry.is_ready: await physics_frame
	var hud = world.get_node("UI_HUD/HUDRoot")
	hud.toggle_minimap()
	hud._select_shrine("arupa_lakshmi")
	check(hud.shrine_selected_label.text.contains("Arupa Lakshmi"), "Selected shrine identity missing")
	check(hud.shrine_selected_label.text.contains("Reference"), "Unreconstructed image disclosure missing")
	check(hud.narration_button.visible, "Narration not discoverable")
	hud._play_selected_narration()
	await create_timer(.2).timeout
	check(hud.narration_player.playing, "Guide audio did not start")
	check(hud.narration_player.stream.get_length() > 5, "Guide clip is truncated")
	for frame in range(10): await process_frame
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("D:/Kshetra_Darshan/output/review/kanchi_guide_narration.png")
		root.size = Vector2i(960,720)
		for frame in range(10): await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("D:/Kshetra_Darshan/output/review/kanchi_guide_narration_960.png")
		check(hud.narration_button.get_global_rect().end.y <= hud.get_viewport_rect().size.y, "Narration control outside narrow viewport")
		root.size = Vector2i(1280,720)
	hud._close_shrine_map()
	check(not hud.narration_player.playing, "Guide should stop when panel closes")
	world.free()
	await process_frame
	gm.current_temple_id = "pradyumna_shrinkhala"
	world = load("res://scenes/temple_world.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	while not world.shrine_registry.is_ready: await physics_frame
	check(world.shrine_registry.get_destinations().size() == 3, "Pandua heritage destinations missing")
	if DisplayServer.get_name() != "headless":
		world.get_node("UI_HUD").hide()
		world.player.visual_mesh.hide()
		var camera = Camera3D.new()
		world.add_child(camera)
		camera.current = true
		camera.global_position = Vector3(76,43,79)
		camera.look_at(Vector3(4,10,-4))
		for frame in range(12): await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("D:/Kshetra_Darshan/output/review/pandua_present_day.png")
	world.free()
	OS.delay_msec(80)
	await process_frame
	print("SHRINE_GUIDE_RESULT ", failures)
	quit(0 if failures.is_empty() else 1)
