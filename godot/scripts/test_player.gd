extends SceneTree
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func box(world: Node, position: Vector3, size: Vector3) -> void:
	var body = StaticBody3D.new()
	var shape = CollisionShape3D.new()
	shape.shape = BoxShape3D.new()
	shape.shape.size = size
	body.add_child(shape)
	world.add_child(body)
	body.position = position

func check(condition: bool, title: String) -> void:
	print("PLAYER_TEST ", "PASS " if condition else "FAIL ", title)
	if not condition: failures.append(title)

func run() -> void:
	root.get_node("GameManager").mobile_mode = true
	var world = load("res://scenes/temple_world.tscn").instantiate()
	world.set_script(null)
	world.get_node("UI_HUD/HUDRoot").set_script(null)
	root.add_child(world)
	var player = world.get_node("Player")
	box(world, Vector3(0,-.1,0), Vector3(40,.2,40))
	box(world, Vector3(0,.1,-1), Vector3(2,.2,.6))
	box(world, Vector3(0,.2,-1.6), Vector3(2,.4,.6))
	box(world, Vector3(0,.3,-2.4), Vector3(2,.6,1.0))
	box(world, Vector3(0,1.3,-3.6), Vector3(2,2.6,.4))
	player.position = Vector3(0,.02,0)
	for i in range(15): await physics_frame
	check(player.is_on_floor(), "initial floor contact")
	check(player.prayer_blend == 0, "neutral arms on spawn")
	var press = InputEventKey.new()
	press.keycode = KEY_P
	press.pressed = true
	Input.parse_input_event(press)
	for i in range(30): await physics_frame
	check(player.prayer_blend > .95, "P raises palms into prayer")
	var hand_l = player.arm_joints["L"]["hand"]
	var hand_r = player.arm_joints["R"]["hand"]
	check(absf(hand_l.position.distance_to(hand_r.position) - .036) < .001, "palms touch without overlap")
	press = InputEventKey.new()
	press.keycode = KEY_P
	press.pressed = false
	Input.parse_input_event(press)
	Input.action_press("move_forward")
	var max_height: float = 0
	for i in range(120):
		await physics_frame
		max_height = maxf(max_height, player.position.y)
	Input.action_release("move_forward")
	print("PLAYER_MEASURE position=",player.position," max_height=",max_height)
	check(max_height > .58, "ascends three 0.2m steps")
	check(player.position.z > -3.1, "full-height wall blocks movement")
	check(player.prayer_blend < .01, "walking returns hands to neutral")
	# A 0.2m stair under a ceiling only 0.1m above the capsule blocks stepping.
	box(world, Vector3(5,1.95,-.5), Vector3(2,.1,2))
	box(world, Vector3(5,.1,-1), Vector3(2,.2,.6))
	player.position = Vector3(5,.02,0)
	player.velocity = Vector3.ZERO
	for i in range(20): await physics_frame
	Input.action_press("move_forward")
	for i in range(60): await physics_frame
	Input.action_release("move_forward")
	check(player.position.y < .1 and player.position.z > -.6, "ceiling clearance blocks unsafe step-up")
	player.toggle_camera_perspective()
	check(not player.visual_mesh.visible and player.camera_arm.spring_length == 0, "first-person hides own mesh")
	player.toggle_camera_perspective()
	check(player.visual_mesh.visible and is_equal_approx(player.camera_arm.spring_length, player.default_arm_length), "third-person restores rear camera")
	print("PLAYER_TEST_RESULT ", failures.size(), " failures")
	quit(0 if failures.is_empty() else 1)

