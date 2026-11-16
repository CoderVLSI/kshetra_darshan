extends SceneTree
var failures: Array[String] = []
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	root.size = Vector2i(1280,720)
	var gm = root.get_node("GameManager")
	gm.current_temple_id = "kanchipuram_kamakshi"
	var world = load("res://scenes/temple_world.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	while not world.shrine_registry.is_ready: await physics_frame
	var registry = world.shrine_registry
	var destinations: Array = registry.get_destinations()
	for destination in destinations:
		var node = registry.get_node_or_null("ShrineIdentity_" + str(destination.id).validate_node_name())
		if node == null or node.get_node_or_null("ShrineLabel") == null:
			failures.append("Missing identity: " + str(destination.id))
		if str(destination.get("tradition", "")).is_empty():
			failures.append("Missing tradition: " + str(destination.id))
	for destination in destinations:
		if destination.id != "arupa_lakshmi": continue
		if not registry.teleport_to(destination.id): failures.append("Arupa teleport failed")
		for frame in range(30): await physics_frame
		var camera = Camera3D.new()
		world.add_child(camera)
		camera.current = true
		world.player.visual_mesh.hide()
		camera.global_position = world.player.global_position + Vector3(0,1.65,0)
		camera.look_at(destination.target + Vector3(0,.25,0))
		for frame in range(15): await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("D:/Kshetra_Darshan/output/review/kanchi_labels_player_view.png")
	print("SHRINE_LABEL_CHECK ", destinations.size(), " identities; ", failures)
	world.free()
	OS.delay_msec(80)
	await process_frame
	quit(0 if failures.is_empty() else 1)
