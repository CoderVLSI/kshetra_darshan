extends SceneTree
var out := "D:/Kshetra_Darshan/output/review/"
func _initialize() -> void:
	call_deferred("run")
func capture(file: String) -> void:
	for frame in range(5): await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out + file)
func run() -> void:
	root.size = Vector2i(1280,720)
	var gm = root.get_node("GameManager")
	gm.current_temple_id = "kanchipuram_kamakshi"
	var world = load("res://scenes/temple_world.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	while not world.shrine_registry.is_ready:
		await physics_frame
	var hud = world.get_node("UI_HUD/HUDRoot")
	hud.toggle_minimap()
	await capture("shrine_map_kanchi.png")
	assert(hud.shrine_destinations.size() == 19)
	assert(hud.map_shapes.any(func(shape: Dictionary) -> bool:
		var edge: Vector2 = shape.outline[1] - shape.outline[0]
		return absf(edge.x) > 5.0 and absf(edge.y) > 5.0
	))
	var vishnu_id = ""
	for destination in hud.shrine_destinations:
		if destination.form == "vishnu": vishnu_id = destination.id
	assert(not vishnu_id.is_empty())
	hud._teleport_to_shrine(vishnu_id)
	for frame in range(12): await physics_frame
	assert(world.player.is_on_floor())
	assert(not hud.is_modal_open())
	await capture("shrine_vishnu_arrival.png")
	var camera = Camera3D.new()
	world.add_child(camera)
	camera.current = true
	world.player.visual_mesh.hide()
	camera.fov = 90
	camera.position = world.player.position + Vector3(0,1.7,0)
	camera.look_at(camera.position + world.sun_light.global_basis.z * 100)
	await capture("sky_sun_clouds.png")
	camera.position = Vector3(15,7,17)
	camera.look_at(Vector3(0,4,-6))
	await capture("complex_shrines_exterior.png")
	world.player.visual_mesh.show()
	camera.current = false
	hud.toggle_minimap()
	root.size = Vector2i(960,720)
	await capture("shrine_map_960.png")
	world.free()
	OS.delay_msec(80)
	await process_frame
	print("SHRINE_VISUAL_PASS map, Vishnu teleport, sky, exterior, 960px layout")
	quit()
