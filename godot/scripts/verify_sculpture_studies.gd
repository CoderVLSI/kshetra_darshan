extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var scene = Node3D.new()
	root.add_child(scene)
	current_scene = scene
	var camera = Camera3D.new()
	scene.add_child(camera)
	camera.position = Vector3(0,1.4,5.5)
	camera.fov = 38
	camera.look_at(Vector3(0,1.05,0))
	camera.current = true
	var sun = DirectionalLight3D.new()
	scene.add_child(sun)
	sun.rotation_degrees = Vector3(-35,-25,0)
	sun.light_energy = 1.8
	var env = WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(.15,.17,.19)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(.8,.85,1)
	env.environment.ambient_light_energy = .7
	scene.add_child(env)
	var index = 0
	var extended = "--extended" in OS.get_cmdline_user_args()
	var entries = [{"id":"annapurna"},{"id":"surya"},{"id":"nabhigaya"},{"id":"devi_footprints"},{"id":"sosthi_tala"}] if extended else [{"id":"kalvar_perumal","form":"vishnu"},{"id":"saraswati"},{"id":"murugan"},{"id":"varahi"},{"id":"ganesha","form":"ganesha"}]
	for entry in entries:
		var sculpt = load("res://scripts/shrine_sculpture.gd").new().build(entry)
		scene.add_child(sculpt)
		sculpt.position.x = float(index-2)*1.1
		index += 1
	for frame in range(8): await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("D:/Kshetra_Darshan/output/review/sculpture_studies_extended.png" if extended else "D:/Kshetra_Darshan/output/review/sculpture_studies.png")
	print("SCULPTURE_STUDIES five distinct figures rendered")
	quit()
