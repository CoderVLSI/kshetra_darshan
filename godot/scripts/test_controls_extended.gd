extends SceneTree
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, title: String) -> void:
	print("CONTROL_CHECK ", "PASS " if condition else "FAIL ", title)
	if not condition:
		failures.append(title)

func key(code: int, pressed: bool) -> void:
	var event = InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)

func run() -> void:
	root.get_node("GameManager").mobile_mode = true
	var world = load("res://scenes/temple_world.tscn").instantiate()
	world.set_script(null)
	world.get_node("UI_HUD/HUDRoot").set_script(null)
	root.add_child(world)
	var floor = StaticBody3D.new()
	var collision = CollisionShape3D.new()
	collision.shape = BoxShape3D.new()
	collision.shape.size = Vector3(80, .2, 80)
	floor.add_child(collision)
	floor.position.y = -.1
	world.add_child(floor)
	var player = world.get_node("Player")
	player.position = Vector3(0, .02, 0)
	for frame in range(20): await physics_frame
	check(player.is_on_floor(), "spawn floor")
	key(KEY_SPACE, true)
	var max_height: float = 0
	for frame in range(45):
		await physics_frame
		max_height = maxf(max_height, player.position.y)
	key(KEY_SPACE, false)
	check(max_height > .8, "Space input jumps")
	for frame in range(30): await physics_frame
	check(player.is_on_floor(), "jump lands")
	key(KEY_W, true)
	for frame in range(30): await physics_frame
	var walk_velocity: float = Vector2(player.velocity.x, player.velocity.z).length()
	key(KEY_SHIFT, true)
	for frame in range(30): await physics_frame
	var sprint_velocity: float = Vector2(player.velocity.x, player.velocity.z).length()
	check(sprint_velocity > walk_velocity * 1.6, "Shift input sprints faster than walking")
	key(KEY_W, false)
	key(KEY_SHIFT, false)
	for frame in range(15): await physics_frame
	player.position = Vector3.ZERO
	key(KEY_K, true)
	for frame in range(96): await physics_frame
	key(KEY_K, false)
	var head = player.devotee_instance.find_child("Head", true, false)
	check(player.visual_mesh.rotation.x < -1.3, "Pranam rotates forward")
	check(head.global_position.z < -.9 and head.global_position.y < .5, "head reaches forward near the ground")
	check(player.velocity.length() < .05, "Pranam stops walking")
	print("PRANAM_HEAD ", head.global_position)
	for frame in range(120): await physics_frame
	check(absf(player.visual_mesh.rotation.x) < .02, "Pranam returns upright")
	world.free()
	OS.delay_msec(80)
	await process_frame
	print("CONTROL_CHECK_RESULT ", failures.size(), " failures")
	quit(0 if failures.is_empty() else 1)
