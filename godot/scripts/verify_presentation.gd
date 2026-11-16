extends SceneTree

func _initialize() -> void:
	call_deferred("verify")

func screenshot(path: String) -> void:
	for i in range(6):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(path)

func verify() -> void:
	root.size = Vector2i(1280, 720)
	var gm = root.get_node("GameManager")
	var menu = load("res://scenes/main_menu.tscn").instantiate()
	root.add_child(menu)
	current_scene = menu
	await screenshot("D:/Kshetra_Darshan/output/review/menu_1280.png")
	var search = menu.get_node("MainMenuRoot/BrowseBar/Search")
	search.text = "Kanchi"
	search.text_changed.emit(search.text)
	assert(menu.cards_grid.get_child_count() == 1, "Search should return one temple")
	await screenshot("D:/Kshetra_Darshan/output/review/menu_search.png")
	search.text = ""
	search.text_changed.emit("")
	root.size = Vector2i(960, 720)
	await screenshot("D:/Kshetra_Darshan/output/review/menu_960.png")
	assert(menu.cards_grid.columns >= 1 and menu.cards_grid.columns <= 4, "Grid should fit the logical canvas width")
	menu.free()
	root.size = Vector2i(1280, 720)
	gm.current_temple_id = "kanchipuram_kamakshi"
	var world = load("res://scenes/temple_world.tscn").instantiate()
	root.add_child(world)
	current_scene = world
	var hud = world.get_node("UI_HUD/HUDRoot")
	hud.toggle_minimap()
	await screenshot("D:/Kshetra_Darshan/output/review/hud_map.png")
	assert(not hud.map_shapes.is_empty(), "Map should have projected model footprints")
	hud.toggle_heritage_panel()
	assert(hud.is_modal_open(), "Heritage should block player input")
	var heritage = hud.get_node("HeritageModal/VBox/TabContainer/Heritage/Content")
	assert("The main sacred form" in heritage.text, "Research deity notes should load")
	await screenshot("D:/Kshetra_Darshan/output/review/heritage_deity.png")
	hud._close_heritage()
	assert(not hud.is_modal_open())
	world.free()
	print("UI_CHECKS_PASS search responsive map deity_notes modal")
	quit()

