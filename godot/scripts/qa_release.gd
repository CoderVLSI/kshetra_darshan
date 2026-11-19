extends SceneTree
var failures: Array[String] = []

func check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
		push_error(message)

# Run externally against the exported PCK from the build directory. No editor
# cache or project source files are required by the loaded game resources.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var gm = root.get_node("GameManager")
	check(gm.temples.size() == 21, "Expected traditional eighteen plus three additional destinations")
	check(gm.reference_notes.size() == 21, "Reference JSON must ship in the PCK")
	var narration_file = FileAccess.open("res://data/narration_manifest.json",FileAccess.READ)
	check(narration_file != null, "Narration manifest must ship")
	if narration_file:
		var narration = JSON.parse_string(narration_file.get_as_text())
		for item in narration.get("items", []):
			var audio = load(item.path) as AudioStream
			check(audio != null and audio.get_length() > 5, "Missing or truncated guide audio " + str(item.id))
	for id in gm.temples:
		check(ResourceLoader.exists("res://assets/models/%s_kshetra_full.glb" % id), "Missing exported model " + id)
		check(FileAccess.file_exists("res://data/%s_heritage.json" % id), "Missing heritage JSON " + id)
	gm.current_temple_id = "srisailam_bhramaramba"
	var world = load("res://scenes/temple_world.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	var player = world.get_node("Player")
	for frame in range(45):
		await physics_frame
	check(player.is_on_floor(), "Release player must settle on a floor")
	check(player.prayer_blend < .01, "Release player must spawn with relaxed arms")
	check(player.arm_joints.size() == 2, "Articulated player must ship in the pack")
	check(world.shrine_registry.is_ready, "Release shrine registry must populate")
	var srisailam_destinations: Array = world.shrine_registry.get_destinations()
	check(srisailam_destinations.size() == 45, "Release shrine catalogue must populate all 45 Srisailam destinations")
	for destination in srisailam_destinations:
		check(destination.available, "Release destination must have a landing: " + str(destination.id))
		check(destination.placement_status == "existing_model_anchor", "Srisailam destinations must have authored anchors: " + str(destination.id))
	gm.trigger_seva("prayer")
	for frame in range(30):
		await physics_frame
	check(player.prayer_blend > .95, "Prayer must animate in the release")
	world.free()
	OS.delay_msec(80)
	await process_frame
	print("RELEASE_CHECK: ", failures.size(), " failures; 21 models, 21 reference records, 21 heritage files, grounded player, neutral/prayer poses")
	quit(0 if failures.is_empty() else 1)
