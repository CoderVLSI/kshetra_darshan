extends SceneTree
var failures: Array[String] = []
var results: Array = []
func _initialize() -> void:
	call_deferred("run")
func check(ok: bool, message: String) -> void:
	if not ok:
		failures.append(message)
		push_error(message)
func run() -> void:
	var gm = root.get_node("GameManager")
	gm.mobile_mode = true
	var packed = load("res://scenes/temple_world.tscn")
	for id in gm.temples:
		gm.current_temple_id = id
		var world = packed.instantiate()
		root.add_child(world)
		current_scene = world
		var registry = world.shrine_registry
		for frame in range(120):
			await physics_frame
			if registry and registry.is_ready:
				break
		check(registry != null and registry.is_ready, id + " registry ready")
		if not registry or not registry.is_ready:
			world.free()
			continue
		await physics_frame
		var destinations = registry.get_destinations()
		var unavailable: Array = []
		var location_unverified: Array = []
		var teleported = 0
		for destination in destinations:
			if destination.placement_status == "location_unverified":
				location_unverified.append(destination.id)
				check(not destination.available and not registry.teleport_to(destination.id),
					id + " unverified location must never teleport: " + destination.id)
				continue
			if not destination.available:
				unavailable.append(destination.label)
				continue
			var success: bool = registry.teleport_to(destination.id)
			check(success, id + ": teleport " + destination.label)
			for frame in range(12):
				await physics_frame
			if not world.player.is_on_floor():
				print("UNSETTLED ", id, " ", destination.label, " landing=", destination.position, " current=", world.player.global_position, " velocity=", world.player.velocity)
			check(world.player.is_on_floor(), id + ": grounded at " + destination.label)
			check(world.player.global_position.distance_to(destination.position) < .6, id + ": stable landing " + destination.label)
			teleported += 1 if success else 0
		check(not destinations.is_empty(), id + " non-empty catalogue")
		check(unavailable.is_empty(), id + " unavailable shrines: " + str(unavailable))
		results.append({"temple":id,"destinations":destinations.size(),"teleports":teleported,
			"unavailable":unavailable,"location_unverified":location_unverified})
		print("SHRINE_QA ", id, " destinations=", destinations.size(), " teleports=", teleported,
			" unavailable=", unavailable, " location_unverified=", location_unverified)
		current_scene = null
		world.free()
		await process_frame
	var file = FileAccess.open(ProjectSettings.globalize_path("res://../output/review/shrine_qa.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify({"results":results,"failures":failures},"\t"))
	OS.delay_msec(80)
	await process_frame
	print("SHRINE_QA_COMPLETE failures=", failures.size())
	quit(0 if failures.is_empty() else 1)
