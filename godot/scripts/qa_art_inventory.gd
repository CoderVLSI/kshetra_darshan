extends SceneTree
var items: Array = []
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var gm = root.get_node("GameManager")
	gm.mobile_mode = true
	for id in gm.temples:
		gm.current_temple_id = id
		var world = load("res://scenes/temple_world.tscn").instantiate()
		root.add_child(world)
		current_scene = world
		while not world.shrine_registry.is_ready: await physics_frame
		for destination in world.shrine_registry.get_destinations():
			items.append({"temple_id":id,"id":destination.id,"label":destination.label,"form":destination.form,"artwork_status":destination.artwork_status,"placement_status":destination.placement_status,"source_ids":destination.source_ids})
		current_scene = null
		world.free()
		await process_frame
	var report = {"scope":"Actual runtime artwork disclosures; an existing anchor is not proof of authentic artwork.","items":items}
	var file = FileAccess.open("res://../research/2026-11-16/current_art_inventory.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	print("ART_INVENTORY ",items.size()," destinations recorded")
	OS.delay_msec(80)
	await process_frame
	quit()
