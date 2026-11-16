extends SceneTree
var failures: Array[String] = []
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var gm = root.get_node("GameManager")
	gm.mobile_mode = true
	for id in ["draksharama_manikyamba", "kashmir_sharada"]:
		gm.current_temple_id = id
		var world = load("res://scenes/temple_world.tscn").instantiate()
		root.add_child(world)
		current_scene = world
		while not world.shrine_registry.is_ready: await physics_frame
		var player: CharacterBody3D = world.player
		player.rotation = Vector3.ZERO
		if id == "draksharama_manikyamba": player.global_position = Vector3(6.8,.1,3)
		for frame in range(30): await physics_frame
		Input.action_press("move_forward")
		var limit: float = -5.75 if id == "draksharama_manikyamba" else 13.0
		for frame in range(650):
			await physics_frame
			if player.global_position.z <= limit: break
		Input.action_release("move_forward")
		for frame in range(12): await physics_frame
		var expected: float = 3.15 if id == "draksharama_manikyamba" else 10.0
		if player.global_position.y < expected or not player.is_on_floor():
			failures.append(id + " stair route failed: " + str(player.global_position))
		print("PRESENT_ROUTE ",id," finish=",player.global_position," grounded=",player.is_on_floor())
		current_scene = null
		world.free()
		await process_frame
	for failure in failures: push_error(failure)
	print("PRESENT_ROUTES_RESULT ", failures.size(), " failures")
	OS.delay_msec(80)
	await process_frame
	quit(0 if failures.is_empty() else 1)
