extends SceneTree

# Integration check: imported scenes, real collision bodies and settled spawn.
# This is a runtime check, not a certification of architectural accuracy.
var failures: Array[String] = []
var records: Array = []

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var gm = root.get_node("GameManager")
	for id in gm.temples:
		gm.current_temple_id = id
		var scene = load("res://scenes/temple_world.tscn").instantiate()
		root.add_child(scene)
		current_scene = scene
		await physics_frame
		var player = scene.get_node("Player")
		var start: Vector3 = player.global_position
		for frame in range(50):
			await physics_frame
		var settled: Vector3 = player.global_position
		var floor_ok: bool = player.is_on_floor()
		if not floor_ok or settled.y < start.y - 8:
			failures.append("%s: spawn does not settle on a floor" % id)
		var model = scene.get_node("TempleModelHolder").get_child(0)
		var record = {"id":id,"floor":floor_ok,"spawn":[start.x,start.y,start.z],"settled":[settled.x,settled.y,settled.z],"meshes":count_meshes(model),"materials_with_textures":count_textured(model)}
		records.append(record)
		print("WORLD ", JSON.stringify(record))
		scene.free()
		await process_frame
	var target = ProjectSettings.globalize_path("res://../output/review/world_qa.json")
	var file = FileAccess.open(target, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify({"records":records,"failures":failures},"\t"))
	for failure in failures:
		push_error(failure)
	print("WORLD QA: ", records.size(), " destinations; ", failures.size(), " failures")
	# With --fixed-fps the test can finish before the real audio mixing thread
	# has released its final playback reference. Let that thread drain once.
	OS.delay_msec(80)
	await process_frame
	quit(0 if failures.is_empty() else 1)

func count_meshes(node: Node) -> int:
	var total = 1 if node is MeshInstance3D else 0
	for child in node.get_children():
		total += count_meshes(child)
	return total

func count_textured(node: Node) -> int:
	var total = 0
	if node is MeshInstance3D and node.mesh:
		for index in range(node.mesh.get_surface_count()):
			var material = node.get_active_material(index)
			if material is StandardMaterial3D and material.albedo_texture:
				total += 1
	for child in node.get_children():
		total += count_textured(child)
	return total
