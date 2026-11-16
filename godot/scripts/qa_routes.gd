extends SceneTree

# Integration route probe: the actual TempleWorld and PlayerController, imported
# temple collision meshes, spawn orientation, and 150 physics frames of forward
# movement. This checks the arrival route, not every shrine or a surveyed plan.
var results: Array[Dictionary] = []

func _initialize() -> void:
	call_deferred("run")

func vector_values(v: Vector3) -> Array[float]:
	return [v.x, v.y, v.z]

func collider_name(collider: Object) -> String:
	if collider is Node:
		var node := collider as Node
		return str(node.get_parent().get_path()) if node.get_parent() else str(node.name)
	return str(collider)

func forward_obstacles(player: CharacterBody3D) -> Array[Dictionary]:
	var found: Array[Dictionary] = []
	for height in [0.15, 0.8, 1.7]:
		var start: Vector3 = player.global_position + Vector3.UP * height
		var end: Vector3 = start - player.global_basis.z * 8.0
		var query := PhysicsRayQueryParameters3D.create(start, end, player.collision_mask, [player.get_rid()])
		var hit: Dictionary = player.get_world_3d().direct_space_state.intersect_ray(query)
		if not hit.is_empty():
			found.append({"probe_height_m": height, "collider": collider_name(hit["collider"]), "point": vector_values(hit["position"]), "normal": vector_values(hit["normal"]), "distance_m": start.distance_to(hit["position"])})
	return found

func run() -> void:
	var manager = root.get_node("GameManager")
	# Headless mouse capture is unavailable; use the same keyboard movement path
	# with mobile mode enabled to avoid the desktop's deliberate released-mouse lock.
	manager.mobile_mode = true
	var scene: PackedScene = load("res://scenes/temple_world.tscn")
	var failed: int = 0
	for id in manager.temples:
		manager.current_temple_id = id
		var world = scene.instantiate()
		root.add_child(world)
		current_scene = world
		var player: CharacterBody3D = world.get_node("Player")
		for frame in range(30):
			await physics_frame
		var start := player.global_position
		var forward := -player.global_basis.z
		var max_drop: float = 0.0
		var maximum_progress: float = 0.0
		var minimum_height := start.y
		var collisions: Dictionary = {}
		var trace: Array[Dictionary] = [{"frame": 0, "position": vector_values(start)}]
		Input.action_press("move_forward")
		for frame in range(150):
			await physics_frame
			minimum_height = minf(minimum_height, player.global_position.y)
			max_drop = maxf(max_drop, start.y - player.global_position.y)
			maximum_progress = maxf(maximum_progress, (player.global_position - start).dot(forward))
			for index in range(player.get_slide_collision_count()):
				var collision := player.get_slide_collision(index)
				if collision.get_normal().dot(Vector3.UP) < 0.7:
					collisions[collider_name(collision.get_collider())] = vector_values(collision.get_normal())
			if (frame + 1) % 15 == 0:
				trace.append({"frame": frame + 1, "position": vector_values(player.global_position)})
		Input.action_release("move_forward")
		var finish := player.global_position
		var distance: float = Vector2(finish.x-start.x, finish.z-start.z).length()
		var passed: bool = distance > 4.0 and max_drop < 5.0
		if not passed:
			failed += 1
		var result: Dictionary = {"temple": id, "passed": passed, "horizontal_distance_m": distance, "maximum_forward_progress_m": maximum_progress, "max_drop_m": max_drop, "start": vector_values(start), "finish": vector_values(finish), "is_on_floor_at_finish": player.is_on_floor(), "blocking_collisions": collisions, "forward_rays_at_finish": forward_obstacles(player), "trace": trace}
		results.append(result)
		print("QA_ROUTE ", "PASS " if passed else "FAIL ", id, " distance_m=", snappedf(distance,0.001), " max_drop_m=", snappedf(max_drop,0.001), " blockers=", collisions.keys())
		current_scene = null
		world.queue_free()
		await process_frame
		await physics_frame
	var out := ProjectSettings.globalize_path("res://../output/review/route_qa.json")
	DirAccess.make_dir_recursive_absolute(out.get_base_dir())
	var report := FileAccess.open(out, FileAccess.WRITE)
	report.store_string(JSON.stringify({"scope": "150-frame arrival-route probe, not full temple navigation certification", "temples": results.size(), "failures": failed, "results": results}, "\t"))
	report.close()
	print("QA_ROUTES_COMPLETE ", results.size()-failed, "/", results.size(), " pass; report ", out)
	OS.delay_msec(80)
	await process_frame
	quit(0 if failed == 0 else 1)


