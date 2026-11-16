extends SceneTree
var failures: Array[String] = []
var checked := 0
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var gm = root.get_node("GameManager")
	gm.mobile_mode = true
	for id in gm.temples:
		gm.current_temple_id = id
		var world = load("res://scenes/temple_world.tscn").instantiate()
		root.add_child(world)
		current_scene = world
		while not world.shrine_registry.is_ready: await physics_frame
		var registry = world.shrine_registry
		for destination in registry.get_destinations():
			checked += 1
			var identity = registry.get_node_or_null("ShrineIdentity_" + str(destination.id).validate_node_name())
			if identity == null:
				failures.append(str(id) + ": missing label " + str(destination.id))
				continue
			var title = identity.get_node_or_null("ShrineLabel")
			if title == null or title.text != str(destination.label):
				failures.append(str(id) + ": incorrect label " + str(destination.id))
			if str(destination.get("tradition", "")).is_empty():
				failures.append(str(id) + ": missing tradition " + str(destination.id))
		world.free()
		await process_frame
	print("SHRINE_LABEL_CHECK ", checked, " identities; ", failures.size(), " failures ", failures)
	OS.delay_msec(80)
	await process_frame
	quit(0 if failures.is_empty() else 1)
