extends CharacterBody3D

## PlayerController
## Authentic Hindu devotee character with traditional dhoti, gold zari border,
## yajnopavita (sacred thread), saffron angavastram, and forehead tilak.
## Devotee rests with relaxed arms and joins palms only for Prayer [P]. Performs
## Sashtanga Pranam, Pushpanjali flower offering, Karpura Aarti, Bell ringing,
## and 8 sacred pilgrimage seva actions.

@export var walk_speed: float = 3.6
@export var sprint_speed: float = 6.8
@export var jump_velocity: float = 4.5
@export var mouse_sensitivity: float = 0.0025
@export var gravity: float = 9.8

@onready var camera_arm: SpringArm3D = $CameraArm
@onready var camera: Camera3D = $CameraArm/Camera3D
@onready var visual_mesh: Node3D = $VisualMesh
@onready var flower_particles: CPUParticles3D = $FlowerParticles
@onready var aarti_light: OmniLight3D = $AartiLight
@onready var aarti_particles: CPUParticles3D = $AartiParticles

var is_first_person: bool = false
var default_arm_length: float = 3.8
var pitch_angle: float = 0.0

# Virtual joystick inputs (for mobile HUD controls)
var virtual_move_vector: Vector2 = Vector2.ZERO
var virtual_look_vector: Vector2 = Vector2.ZERO

var pranam_timer: float = 0.0
var pranam_blend: float = 0.0
const PRANAM_DURATION: float = 3.2
var prayer_timer: float = 0.0
var aarti_active_timer: float = 0.0
var walk_anim_phase: float = 0.0

var devotee_instance: Node3D = null
var prayer_blend: float = 0.0
var gait_blend: float = 0.0
var arm_joints: Dictionary = {}
var leg_joints: Dictionary = {}

func _modal_is_open() -> bool:
	var hud_root = get_parent().get_node_or_null("UI_HUD/HUDRoot")
	return hud_root != null and hud_root.has_method("is_modal_open") and hud_root.is_modal_open()


func _ready() -> void:
	if not GameManager.mobile_mode:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	
	if aarti_light:
		aarti_light.visible = false
	if flower_particles:
		flower_particles.emitting = false
	if aarti_particles:
		aarti_particles.emitting = false
	
	_setup_devotee_model()
	# SpringArm must test the environment, never the player's own capsule.
	camera_arm.add_excluded_object(get_rid())
	camera_arm.spring_length = default_arm_length
	camera.near = 0.08
	floor_snap_length = 0.35

	
	if GameManager:
		GameManager.seva_action_performed.connect(_on_seva_triggered)

func _setup_devotee_model() -> void:
	if not visual_mesh:
		return
	
	# Clear previous children if any
	for child in visual_mesh.get_children():
		child.queue_free()
	
	# Load authentic human devotee GLB
	var devotee_scene = load("res://assets/models/devotee_player.glb")
	if devotee_scene:
		devotee_instance = devotee_scene.instantiate() as Node3D
		visual_mesh.add_child(devotee_instance)
		devotee_instance.position = Vector3.ZERO
		devotee_instance.rotation = Vector3.ZERO
		for side in ["L", "R"]:
			arm_joints[side] = {
				"upper": devotee_instance.find_child("UpperArm_" + side, true, false),
				"fore": devotee_instance.find_child("Forearm_" + side, true, false),
				"hand": devotee_instance.find_child("Hand_" + side, true, false)
			}
			leg_joints[side] = devotee_instance.find_child("Leg_" + side, true, false)
		_update_limb_pose(0.0)


func _unhandled_input(event: InputEvent) -> void:
	if _modal_is_open():
		return
	# Mouse look when captured
	if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		_apply_look(event.relative.x, event.relative.y)
	
	# Mouse capture toggle with Escape
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
				Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
			else:
				Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	
	# Mouse click recaptures if in visible mode
	if event is InputEventMouseButton and event.pressed and not GameManager.mobile_mode:
		if Input.get_mouse_mode() != Input.MOUSE_MODE_CAPTURED:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
			get_viewport().set_input_as_handled()
	
	# Action triggers mapped in project.godot
	if Input.is_action_just_pressed("toggle_camera"):
		toggle_camera_perspective()
	elif Input.is_action_just_pressed("prayer"):
		GameManager.trigger_seva("prayer")
	elif Input.is_action_just_pressed("pranam"):
		GameManager.trigger_seva("pranam")
	elif Input.is_action_just_pressed("flower_offering"):
		GameManager.trigger_seva("flower_offering")
	elif Input.is_action_just_pressed("ring_bell"):
		GameManager.trigger_seva("ring_bell")
	elif Input.is_action_just_pressed("aarti"):
		GameManager.trigger_seva("aarti")
	elif Input.is_action_just_pressed("prasadam"):
		GameManager.trigger_seva("prasadam")
	elif Input.is_action_just_pressed("conch"):
		GameManager.trigger_seva("conch")
	elif Input.is_action_just_pressed("mantra"):
		GameManager.trigger_seva("mantra")
	elif Input.is_action_just_pressed("toggle_sound"):
		GameManager.toggle_sound()

func _physics_process(delta: float) -> void:
	# Mobile virtual look
	if not _modal_is_open() and virtual_look_vector.length_squared() > 0.001:
		_apply_look(virtual_look_vector.x * 720.0 * delta, virtual_look_vector.y * 720.0 * delta)
	
	# Gravity
	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		velocity.y = 0.0
	
	var controls_enabled = not _modal_is_open() and (GameManager.mobile_mode or Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED)
	if controls_enabled and is_on_floor() and Input.is_action_just_pressed("jump") and pranam_timer <= 0.0:
		velocity.y = jump_velocity
		prayer_timer = 0.0
	# Movement input
	var input_dir = Vector2.ZERO
	if Input.is_action_pressed("move_forward"):
		input_dir.y -= 1.0
	if Input.is_action_pressed("move_backward"):
		input_dir.y += 1.0
	if Input.is_action_pressed("move_left"):
		input_dir.x -= 1.0
	if Input.is_action_pressed("move_right"):
		input_dir.x += 1.0
	
	# Add mobile virtual joystick input
	if virtual_move_vector.length_squared() > 0.01:
		input_dir += virtual_move_vector
	
	if not controls_enabled or pranam_timer > 0.0:
		input_dir = Vector2.ZERO
	input_dir = input_dir.limit_length(1.0)
	if input_dir.length_squared() > 0.01:
		prayer_timer = 0.0

	
	var is_sprinting = Input.is_action_pressed("sprint")
	var speed = sprint_speed if is_sprinting else walk_speed
	
	# Transform input direction according to player horizontal rotation
	var direction = transform.basis * Vector3(input_dir.x, 0, input_dir.y)
	
	if direction != Vector3.ZERO:
		velocity.x = direction.x * speed
		velocity.z = direction.z * speed
		walk_anim_phase += delta * (14.0 if is_sprinting else 8.5)
	else:
		velocity.x = move_toward(velocity.x, 0, speed * delta * 10.0)
		velocity.z = move_toward(velocity.z, 0, speed * delta * 10.0)
		walk_anim_phase = move_toward(walk_anim_phase, 0.0, delta * 6.0)
	
	var horizontal_motion := Vector3(velocity.x, 0, velocity.z) * delta
	if not _try_step_up(horizontal_motion):
		var before_slide := global_position
		move_and_slide()
		_recover_floor_slide(before_slide, horizontal_motion)
	
	# Character visual movement & prayer/pranam animations
	_update_character_animation(delta, direction.length() > 0.1)

func _recover_floor_slide(before_slide: Vector3, motion: Vector3) -> void:
	# A capsule resting just within its margin can report repeated upward
	# recovery contacts, with no horizontal travel, on a broad flat slab.
	if not is_on_floor() or motion.length_squared() < .00001 or get_slide_collision_count() < 2:
		return
	var progress := global_position - before_slide
	if Vector2(progress.x, progress.z).length_squared() >= motion.length_squared() * .01:
		return
	for index in range(get_slide_collision_count()):
		if get_slide_collision(index).get_normal().dot(Vector3.UP) < .999:
			return
	var raised := global_transform
	raised.origin.y += .016
	if test_move(raised, motion):
		return
	raised.origin += motion
	# Confirm the new point is supported by the same elevation. A capsule
	# sweep can miss this surface for the same reason as the original slide.
	var floor_probe := PhysicsRayQueryParameters3D.create(
		raised.origin, raised.origin + Vector3.DOWN * .026, collision_mask, [get_rid()]
	)
	var support := get_world_3d().direct_space_state.intersect_ray(floor_probe)
	if not support.is_empty() and support["normal"].dot(Vector3.UP) > .999:
		global_position = support["position"] + Vector3.UP * safe_margin

func _try_step_up(horizontal_motion: Vector3) -> bool:
	# Sweep the full capsule up, forward and down. Only accept a floor landing;
	# a head-height obstacle or blocked raised position must never be bypassed.
	if velocity.y > 0.0 or not is_on_floor() or horizontal_motion.length_squared() < 0.000001:
		return false
	if not test_move(global_transform, horizontal_motion):
		return false
	var step_height: float = 0.28
	var raised := global_transform
	if test_move(raised, Vector3.UP * step_height):
		return false
	raised.origin += Vector3.UP * step_height
	if test_move(raised, horizontal_motion):
		return false
	raised.origin += horizontal_motion
	var landing := KinematicCollision3D.new()
	if not test_move(raised, Vector3.DOWN * (step_height + 0.03), landing):
		return false
	# Rounded capsules report a diagonal contact at the stair nosing. Confirm
	# that the actual supporting surface just beyond the nosing is walkable.
	var probe := landing.get_position() + horizontal_motion.normalized() * 0.06
	var query := PhysicsRayQueryParameters3D.create(probe + Vector3.UP * 0.10, probe + Vector3.DOWN * 0.10, collision_mask, [get_rid()])
	var support: Dictionary = get_world_3d().direct_space_state.intersect_ray(query)
	if support.is_empty() or support["normal"].dot(Vector3.UP) < cos(floor_max_angle):
		return false
	var rise: float = step_height + landing.get_travel().y
	if rise < 0.005 or rise > step_height:
		return false
	global_position = raised.origin + landing.get_travel()
	velocity.y = 0.0
	return true

func _update_character_animation(delta: float, is_moving: bool) -> void:
	if not visual_mesh:
		return
		
	prayer_timer = maxf(0.0, prayer_timer - delta)
	prayer_blend = move_toward(prayer_blend, 1.0 if prayer_timer > 0.0 else 0.0, delta * 3.5)
	gait_blend = move_toward(gait_blend, 1.0 if is_moving else 0.0, delta * 5.0)
	pranam_blend = sin(clampf((PRANAM_DURATION - pranam_timer) / PRANAM_DURATION, 0.0, 1.0) * PI) if pranam_timer > 0.0 else 0.0
	_update_limb_pose(gait_blend)

	# Forward prostration: -X rotation moves the head along local -Z.
	if pranam_timer > 0.0:
		pranam_timer = maxf(0.0, pranam_timer - delta)
		var bow_amount = pranam_blend
		visual_mesh.rotation.x = deg_to_rad(-86.0 * bow_amount)
		visual_mesh.rotation.z = 0.0
		visual_mesh.position.y = bow_amount * 0.12
		if pranam_timer <= 0.0:
			visual_mesh.rotation.x = 0.0
			visual_mesh.position.y = 0.0
	elif is_moving:
		# Natural gentle step bobbing while walking
		var step_bob = abs(sin(walk_anim_phase)) * 0.04
		var side_tilt = sin(walk_anim_phase) * deg_to_rad(1.8)
		visual_mesh.position.y = lerp(visual_mesh.position.y, step_bob, delta * 12.0)
		visual_mesh.rotation.z = lerp(visual_mesh.rotation.z, side_tilt, delta * 10.0)
		visual_mesh.rotation.x = lerp(visual_mesh.rotation.x, deg_to_rad(-2.0), delta * 8.0) # gentle forward lean
	else:
		visual_mesh.position.y = lerp(visual_mesh.position.y, 0.0, delta * 8.0)
		visual_mesh.rotation.z = lerp(visual_mesh.rotation.z, 0.0, delta * 8.0)
		visual_mesh.rotation.x = lerp(visual_mesh.rotation.x, 0.0, delta * 8.0)

	# Handle Aarti flame illumination
	if aarti_active_timer > 0.0:
		aarti_active_timer -= delta
		if aarti_light:
			aarti_light.light_energy = randf_range(1.6, 2.8)
		if aarti_active_timer <= 0.0:
			if aarti_light:
				aarti_light.visible = false
			if aarti_particles:
				aarti_particles.emitting = false

func _update_limb_pose(gait: float) -> void:
	# Two-bone endpoint solve: keep upper arm and forearm connected while hands
	# blend from a relaxed swing to palms touching in front of the chest.
	for side in ["L", "R"]:
		if not arm_joints.has(side):
			continue
		var joints: Dictionary = arm_joints[side]
		if joints["upper"] == null or joints["fore"] == null or joints["hand"] == null:
			continue
		var sign_side: float = -1.0 if side == "L" else 1.0
		var swing: float = sin(walk_anim_phase) * sign_side * gait
		var shoulder := Vector3(sign_side * 0.235, 1.40, 0)
		var relaxed := Vector3(sign_side * 0.255, 0.865 + absf(swing) * 0.025, swing * 0.11)
		var praying := Vector3(sign_side * 0.018, 1.29, -0.245)
		var wrist := relaxed.lerp(praying, smoothstep(0.0, 1.0, prayer_blend))
		# Reach ahead toward the floor while bowing instead of leaving arms down.
		wrist = wrist.lerp(Vector3(sign_side * 0.12, 1.79, -0.02), smoothstep(0.0, 1.0, pranam_blend))
		var direction := (wrist - shoulder).normalized()
		var distance := clampf(shoulder.distance_to(wrist), 0.03, 0.549)
		var upper_length: float = 0.28
		var lower_length: float = 0.27
		var along: float = (upper_length * upper_length - lower_length * lower_length + distance * distance) / (2.0 * distance)
		var pole := Vector3(sign_side * 0.7, -0.8, 0.15)
		var bend := (pole - direction * pole.dot(direction)).normalized()
		var elbow := shoulder + direction * along + bend * sqrt(maxf(0.0, upper_length * upper_length - along * along))
		var upper: Node3D = joints["upper"]
		var fore: Node3D = joints["fore"]
		var hand: Node3D = joints["hand"]
		upper.position = shoulder
		upper.quaternion = Quaternion(Vector3.DOWN, (elbow - shoulder).normalized())
		fore.position = elbow
		fore.quaternion = Quaternion(Vector3.DOWN, (wrist - elbow).normalized())
		hand.position = wrist
		hand.quaternion = Quaternion(Vector3.RIGHT, PI).slerp(Quaternion.IDENTITY, smoothstep(0.0, 1.0, prayer_blend))
		var leg: Node3D = leg_joints.get(side)
		if leg:
			leg.rotation.x = -swing * 0.20

func _apply_look(rel_x: float, rel_y: float) -> void:
	rotate_y(-rel_x * mouse_sensitivity)
	pitch_angle = clamp(pitch_angle - rel_y * mouse_sensitivity, deg_to_rad(-80.0), deg_to_rad(65.0))
	if camera_arm:
		camera_arm.rotation.x = pitch_angle

func toggle_camera_perspective() -> void:
	is_first_person = not is_first_person
	if camera_arm:
		if is_first_person:
			camera_arm.spring_length = 0.0
			camera_arm.position = Vector3(0, 1.65, 0)
			if visual_mesh:
				visual_mesh.visible = false
		else:
			camera_arm.spring_length = default_arm_length
			camera_arm.position = Vector3(0, 1.5, 0)
			if visual_mesh:
				visual_mesh.visible = true

func _on_seva_triggered(action_name: String, _title: String, _msg: String) -> void:
	match action_name:
		"prayer":
			prayer_timer = 3.5
		"pranam":
			pranam_timer = PRANAM_DURATION
			prayer_timer = 0.0
			velocity.x = 0.0
			velocity.z = 0.0
		"flower_offering":
			if flower_particles:
				flower_particles.restart()
				flower_particles.emitting = true
		"aarti":
			aarti_active_timer = 4.0
			if aarti_light:
				aarti_light.visible = true
			if aarti_particles:
				aarti_particles.restart()
				aarti_particles.emitting = true
