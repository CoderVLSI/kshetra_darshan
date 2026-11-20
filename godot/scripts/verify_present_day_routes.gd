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
		var draksharama_heading := deg_to_rad(21)
		var draksharama_landing := Vector3(10.48, .1, -6.9).rotated(Vector3.UP, draksharama_heading)
		if id == "draksharama_manikyamba":
			player.global_position = Vector3(19.2, .1, -6.9).rotated(Vector3.UP, draksharama_heading)
			player.look_at(draksharama_landing)
		var heading := -player.global_basis.z
		for frame in range(30): await physics_frame
		var arrow := InputEventKey.new()
		arrow.keycode = KEY_UP
		arrow.pressed = true
		Input.parse_input_event(arrow)
		Input.flush_buffered_events()
		for frame in range(1000):
			await physics_frame
			if id == "draksharama_manikyamba" and (draksharama_landing - player.global_position).dot(heading) <= 0.0: break
			if id == "kashmir_sharada" and player.global_position.x >= -14.5: break
		arrow = arrow.duplicate()
		arrow.pressed = false
		Input.parse_input_event(arrow)
		Input.flush_buffered_events()
		for frame in range(12): await physics_frame
		var expected: float = 3.15 if id == "draksharama_manikyamba" else 15.7
		if player.global_position.y < expected or not player.is_on_floor():
			failures.append(id + " stair route failed: " + str(player.global_position))
		if id == "kashmir_sharada" and player.global_position.x < -14.6:
			failures.append(id + " route stopped outside the west gateway")
		print("PRESENT_ROUTE ",id," finish=",player.global_position," grounded=",player.is_on_floor())
		current_scene = null
		world.free()
		await process_frame
	for failure in failures: push_error(failure)
	print("PRESENT_ROUTES_RESULT ", failures.size(), " failures")
	OS.delay_msec(80)
	await process_frame
	quit(0 if failures.is_empty() else 1)
