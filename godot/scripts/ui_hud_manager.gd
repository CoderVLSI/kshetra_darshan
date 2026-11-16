extends Control

## UIHudManager
## Responsive temple collection and in-game heritage/navigation controls.
## (sky controls, minimap, seva action bar, heritage guide with JSON loading, toast notifications).

# Main Menu UI Nodes (if present in scene)
@onready var cards_grid: GridContainer = _get_ui_node(["MainMenuRoot/ScrollContainer/CardsGrid", "ScrollContainer/CardsGrid"])
@onready var menu_title: Label = _get_ui_node(["MainMenuRoot/Header/Title", "Header/Title"])

# HUD UI Nodes (if present in scene)
@onready var seva_bar: HBoxContainer = _get_ui_node(["HUDRoot/SevaBar", "SevaBar"])
@onready var sky_bar: HBoxContainer = _get_ui_node(["HUDRoot/SkyBar", "SkyBar"])
@onready var minimap_panel: Control = _get_ui_node(["HUDRoot/Minimap", "Minimap"])
@onready var heritage_modal: PanelContainer = _get_ui_node(["HUDRoot/HeritageModal", "HeritageModal"])
@onready var toast_panel: PanelContainer = _get_ui_node(["HUDRoot/ToastPanel", "ToastPanel"])
@onready var toast_title: Label = _get_ui_node(["HUDRoot/ToastPanel/VBox/ToastTitle", "ToastPanel/VBox/ToastTitle"])
@onready var toast_desc: Label = _get_ui_node(["HUDRoot/ToastPanel/VBox/ToastDesc", "ToastPanel/VBox/ToastDesc"])
@onready var header_info: Label = _get_ui_node(["HUDRoot/TopBar/TempleInfo", "TopBar/TempleInfo"])
@onready var mobile_controls: Control = _get_ui_node(["HUDRoot/MobileControls", "MobileControls"])

func _get_ui_node(possible_paths: Array):
	for p in possible_paths:
		if has_node(p):
			return get_node(p)
	return null

var toast_timer: float = 0.0
var heritage_data_cache: Dictionary = {}
var modal_backdrop: ColorRect = null
var initial_sky_applied: bool = false
var shrine_map_window: PanelContainer
var shrine_list: VBoxContainer
var shrine_search: LineEdit
var shrine_scope_label: Label
var shrine_selected_label: RichTextLabel
var shrine_destinations: Array = []
var selected_shrine: String = ""
var map_marker_positions: Dictionary = {}
var narration_player: AudioStreamPlayer
var narration_button: Button

func _ready() -> void:
	_apply_theme()
	# If this is the Main Menu scene
	if cards_grid != null:
		_populate_temple_grid()
		_setup_menu()
	
	# If this is the Temple World HUD scene
	if seva_bar != null or header_info != null:
		_setup_hud()
	
	if GameManager:
		GameManager.seva_action_performed.connect(_on_seva_performed)
		GameManager.sound_toggled.connect(_on_sound_toggled)
		GameManager.temple_changed.connect(func(_id): _update_header())

func _process(delta: float) -> void:
	if toast_timer > 0.0:
		toast_timer -= delta
		if toast_timer <= 0.0 and toast_panel != null:
			toast_panel.visible = false
	
	# Update minimap if visible
	map_refresh_timer -= delta
	if minimap_panel != null and minimap_panel.is_visible_in_tree() and map_refresh_timer <= 0.0:
		map_refresh_timer = 0.1
		minimap_panel.queue_redraw()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_H or Input.is_action_just_pressed("heritage_guide"):
			toggle_heritage_panel()
		elif event.keycode == KEY_M or Input.is_action_just_pressed("minimap"):
			toggle_minimap()

# ==============================================================================
# MAIN MENU: RESPONSIVE TEMPLE COLLECTION
# ==============================================================================

const INK = Color("101919")
const PANEL = Color("182323")
const GOLD = Color("d6b780")
const TEXT = Color("eee9df")
const MUTED = Color("a0ada8")
var search_query: String = ""
var map_shapes: Array = []
var map_points: Array = []
var map_bounds: Rect2 = Rect2(-25, -25, 50, 50)
var map_refresh_timer: float = 0.0

func _populate_temple_grid() -> void:
	if cards_grid == null:
		return
	for child in cards_grid.get_children():
		child.free()
	var index = 0
	for tid in GameManager.temples:
		index += 1
		var info: Dictionary = GameManager.temples[tid]
		var searchable = (str(info.get("name", "")) + " " + str(info.get("location", ""))).to_lower()
		if not search_query.is_empty() and not search_query in searchable:
			continue
		cards_grid.add_child(_create_temple_card(tid, info, index))
	_update_grid_columns()

func _update_grid_columns() -> void:
	if cards_grid:
		cards_grid.columns = maxi(1, mini(4, int((size.x - 80.0) / 280.0)))
		for card in cards_grid.get_children():
			card.custom_minimum_size.x = maxf(240.0, (size.x - 80.0 - (cards_grid.columns - 1) * 18.0) / cards_grid.columns)

func _style_panel(bg: Color, border: Color, margin: float = 16.0) -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = bg
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	style.content_margin_left = margin
	style.content_margin_right = margin
	style.content_margin_top = margin
	style.content_margin_bottom = margin
	return style

func _label(text: String, font_size: int, color: Color) -> Label:
	var label = Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label

func _create_temple_card(tid: String, info: Dictionary, _index: int) -> PanelContainer:
	var card = PanelContainer.new()
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.add_theme_stylebox_override("panel", _style_panel(PANEL, Color("35413b"), 0.0))
	var column = VBoxContainer.new()
	column.add_theme_constant_override("separation", 0)
	card.add_child(column)
	var preview = TextureRect.new()
	preview.custom_minimum_size = Vector2(0, 145)
	preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var preview_path = "res://assets/ui/previews/%s.jpg" % tid
	if ResourceLoader.exists(preview_path):
		preview.texture = load(preview_path)
	else:
		var icon_path = "res://assets/ui/icon_%s.png" % tid
		if ResourceLoader.exists(icon_path):
			preview.texture = load(icon_path)
		preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	column.add_child(preview)
	var inset = MarginContainer.new()
	for edge in ["left", "top", "right", "bottom"]:
		inset.add_theme_constant_override("margin_" + edge, 15)
	column.add_child(inset)
	var content = VBoxContainer.new()
	content.add_theme_constant_override("separation", 7)
	inset.add_child(content)
	var badge = "SACRED DESTINATION"
	if tid in ["kalighat", "madurai_meenakshi", "tuljapur_bhavani"]:
		badge = "ADDITIONAL PILGRIMAGE"
	elif tid == "pradyumna_shrinkhala":
		badge = "CONCEPT RECONSTRUCTION"
	elif tid == "prayag_madhaveswari":
		badge = "PRAYAGRAJ  /  ALOPI TRADITION"
	content.add_child(_label(badge, 10, GOLD))
	var name_label = _label(info.get("short_name", tid), 20, TEXT)
	name_label.custom_minimum_size.y = 50
	content.add_child(name_label)
	var location_label = _label(info.get("location", ""), 12, MUTED)
	location_label.custom_minimum_size.y = 30
	content.add_child(location_label)
	var button = Button.new()
	button.text = "Enter darshan    →"
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.custom_minimum_size.y = 38
	button.pressed.connect(func(): GameManager.load_temple(tid))
	content.add_child(button)
	return card

func _setup_menu() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	resized.connect(_update_grid_columns)
	var search = get_node_or_null("MainMenuRoot/BrowseBar/Search") as LineEdit
	if search:
		search.text_changed.connect(func(value: String):
			search_query = value.strip_edges().to_lower()
			_populate_temple_grid())
	var sound = get_node_or_null("MainMenuRoot/Footer/BtnSound") as Button
	if sound:
		sound.text = "Sound: on" if GameManager.sound_enabled else "Sound: off"
		sound.pressed.connect(func():
			GameManager.toggle_sound()
			sound.text = "Sound: on" if GameManager.sound_enabled else "Sound: off")
	var mobile = get_node_or_null("MainMenuRoot/Footer/BtnMobile") as Button
	if mobile:
		mobile.text = "Touch controls: on" if GameManager.mobile_mode else "Touch controls: off"
		mobile.pressed.connect(func():
			GameManager.set_mobile_mode(not GameManager.mobile_mode)
			mobile.text = "Touch controls: on" if GameManager.mobile_mode else "Touch controls: off")

# ==============================================================================
# IN-GAME HUD SETUP & SEVA ACTIONS
# ==============================================================================

func _setup_hud() -> void:
	_update_header()
	_setup_touch_controls()
	if toast_panel:
		toast_panel.visible = false
	if heritage_modal:
		heritage_modal.visible = false
	if minimap_panel:
		minimap_panel.visible = false
	
	# Hook up Seva Bar buttons if present
	_setup_button_multi(["HUDRoot/SevaBar/BtnPrayer", "SevaBar/BtnPrayer"], func(): GameManager.trigger_seva("prayer"))
	_setup_button_multi(["HUDRoot/SevaBar/BtnPranam", "SevaBar/BtnPranam"], func(): GameManager.trigger_seva("pranam"))
	_setup_button_multi(["HUDRoot/SevaBar/BtnFlowers", "SevaBar/BtnFlowers"], func(): GameManager.trigger_seva("flower_offering"))
	_setup_button_multi(["HUDRoot/SevaBar/BtnBell", "SevaBar/BtnBell"], func(): GameManager.trigger_seva("ring_bell"))
	_setup_button_multi(["HUDRoot/SevaBar/BtnAarti", "SevaBar/BtnAarti"], func(): GameManager.trigger_seva("aarti"))
	_setup_button_multi(["HUDRoot/SevaBar/BtnPrasadam", "SevaBar/BtnPrasadam"], func(): GameManager.trigger_seva("prasadam"))
	_setup_button_multi(["HUDRoot/SevaBar/BtnConch", "SevaBar/BtnConch"], func(): GameManager.trigger_seva("conch"))
	_setup_button_multi(["HUDRoot/SevaBar/BtnMantra", "SevaBar/BtnMantra"], func(): GameManager.trigger_seva("mantra"))
	
	# Hook up Sky Presets
	var temple_world = find_parent("TempleWorld")
	for i in range(1, 6):
		var btn = _get_ui_node(["HUDRoot/SkyBar/Sky%d" % i, "SkyBar/Sky%d" % i])
		if btn and temple_world and temple_world.has_method("apply_sky_preset"):
			var idx = i
			btn.pressed.connect(func(): temple_world.apply_sky_preset(idx))
	
	# Hook up Navigation / Utility buttons
	_setup_button_multi(["HUDRoot/TopBar/BtnMenu", "TopBar/BtnMenu"], func(): GameManager.go_to_menu())
	_setup_button_multi(["HUDRoot/TopBar/BtnSound", "TopBar/BtnSound"], func(): GameManager.toggle_sound())
	_setup_button_multi(["HUDRoot/TopBar/BtnHeritage", "TopBar/BtnHeritage"], func(): toggle_heritage_panel())
	_setup_button_multi(["HUDRoot/TopBar/BtnMinimap", "TopBar/BtnMinimap"], func(): toggle_minimap())
	
	# Heritage Modal Close Button
	_setup_button_multi(["HUDRoot/HeritageModal/VBox/BtnClose", "HeritageModal/VBox/BtnClose"], func():
		if heritage_modal:
			_close_heritage()
	)
	
	# Minimap Custom Drawing
	if minimap_panel != null:
		minimap_panel.hide()
	_setup_shrine_map()

func _setup_button_multi(paths: Array, callback: Callable) -> void:
	var btn = _get_ui_node(paths)
	if btn is Button:
		btn.pressed.connect(callback)

func _update_header() -> void:
	if header_info == null:
		return
	var t = GameManager.get_current_temple()
	header_info.text = "%s  /  %s" % [t.get("short_name", "Temple"), t.get("location", "")]

func notify_sky_preset(_preset_idx: int, preset_name: String) -> void:
	if not initial_sky_applied:
		initial_sky_applied = true
		return
	show_toast(" Muhurta Changed", "Current Time: %s" % preset_name, 2.5)

func _on_seva_performed(_action_name: String, title: String, msg: String) -> void:
	show_toast(title, msg, 3.2)

func show_toast(title: String, desc: String, duration: float = 3.0) -> void:
	if toast_panel == null:
		return
	if toast_title:
		toast_title.text = title
	if toast_desc:
		toast_desc.text = desc
	toast_panel.visible = true
	toast_timer = duration

func _on_sound_toggled(enabled: bool) -> void:
	show_toast(" Audio Settings", "Temple Sound is now %s." % ("ENABLED" if enabled else "MUTED"), 1.8)

# ==============================================================================
# HERITAGE GUIDE WITH JSON DATA LOADING
# ==============================================================================

func toggle_heritage_panel() -> void:
	if heritage_modal == null:
		return
	if shrine_map_window and shrine_map_window.visible:
		_close_shrine_map()
	heritage_modal.visible = not heritage_modal.visible
	if modal_backdrop:
		modal_backdrop.visible = heritage_modal.visible
	if toast_panel:
		toast_panel.visible = false
	set_meta("modal_open", heritage_modal.visible)
	if heritage_modal.visible:
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		_load_heritage_guide_content(GameManager.current_temple_id)
	else:
		if not GameManager.mobile_mode:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _load_heritage_guide_content(temple_id: String) -> void:
	var info: Dictionary = GameManager.get_current_temple()
	
	# Load the 3 JSON files: architecture, mantras, heritage
	var arch_json = _read_json_file("res://data/%s_architecture.json" % temple_id)
	var mantras_json = _read_json_file("res://data/%s_mantras.json" % temple_id)
	var heritage_json = _read_json_file("res://data/%s_heritage.json" % temple_id)
	
	# Update modal title
	var title_lbl = _get_ui_node(["HUDRoot/HeritageModal/VBox/TitleLabel", "HeritageModal/VBox/TitleLabel"]) as Label
	if title_lbl:
		title_lbl.text = " Heritage & Darshan Guide: %s" % info.get("name", temple_id)
	
	# Fill Tab 1: Heritage & Mythology
	var txt_heritage = _get_ui_node(["HUDRoot/HeritageModal/VBox/TabContainer/Heritage/Content", "HeritageModal/VBox/TabContainer/Heritage/Content"]) as RichTextLabel
	if txt_heritage:
		var myth = heritage_json.get("mythology", "Sacred Mahatmya of the Divine Mother at this Mahapeetha.")
		var anga = heritage_json.get("devi_anga", info.get("anga", "Maha Shakti Peetha"))
		var bhairava = heritage_json.get("bhairava", info.get("bhairava", "Bhairava Swamy"))
		var festivals = ", ".join(heritage_json.get("festivals", ["Navaratri", "Shivaratri", "Vasantotsava"]))
		var significance = heritage_json.get("pilgrimage_significance", "A supreme source of spiritual power and divine grace.")
		
		txt_heritage.text = "[b][color=#ffcc66] Sacred Devi Anga (Body Part):[/color][/b] %s\n" % anga
		txt_heritage.text += "[b][color=#ffcc66] Kshetrapala Bhairava:[/color][/b] %s\n\n" % bhairava
		txt_heritage.text += "[b][color=#ffcc66] Sthala Purana & Mythology:[/color][/b]\n%s\n\n" % myth
		txt_heritage.text += "[b][color=#ffcc66] Pilgrimage Significance:[/color][/b]\n%s\n\n" % significance
		txt_heritage.text += "[b][color=#ffcc66] Major Festivals:[/color][/b] %s\n" % festivals
	
	# Fill Tab 2: Mantras & Stotram
	var txt_mantras = _get_ui_node(["HUDRoot/HeritageModal/VBox/TabContainer/Mantras/Content", "HeritageModal/VBox/TabContainer/Mantras/Content"]) as RichTextLabel
	if txt_mantras:
		var stotram = mantras_json.get("stotram_verse", "Ashtadasha Shakti Peetha Stotram verse for %s" % info.get("devi", "Devi"))
		var stotram_meaning = mantras_json.get("stotram_meaning", "Offering reverence to the primordial cosmic energy residing here.")
		var beej = mantras_json.get("beej_mantra", "Om Aim Hreem Kleem Chamundayai Vichche")
		var dhyana = mantras_json.get("dhyana_shloka", "Dhyana Shloka of %s" % info.get("devi", "Devi"))
		var aarti = mantras_json.get("aarti_first_line", "Jai Ambe Gauri, Maiya Jai Shyama Gauri")
		
		txt_mantras.text = "[b][color=#ffcc66] Ashtadasha Shakti Peetha Stotram:[/color][/b]\n[i]\"%s\"[/i]\n\n" % stotram
		txt_mantras.text += "[b][color=#ffcc66] Meaning:[/color][/b]\n%s\n\n" % stotram_meaning
		txt_mantras.text += "[b][color=#ffcc66] Moola Beeja Mantra:[/color][/b]\n[b]%s[/b]\n\n" % beej
		txt_mantras.text += "[b][color=#ffcc66] Dhyana Shloka:[/color][/b]\n%s\n\n" % dhyana
		txt_mantras.text += "[b][color=#ffcc66] Mangala Aarti:[/color][/b]\n\"%s\"\n" % aarti
	
	# Fill Tab 3: Architecture & Vastu
	var txt_arch = _get_ui_node(["HUDRoot/HeritageModal/VBox/TabContainer/Architecture/Content", "HeritageModal/VBox/TabContainer/Architecture/Content"]) as RichTextLabel
	if txt_arch:
		var style_name = arch_json.get("style", info.get("style", "Sacred Temple Architecture"))
		var period = arch_json.get("period", "Ancient / Medieval Heritage")
		var structures = ", ".join(arch_json.get("key_structures", ["Garbhagriha (Sanctum)", "Antarala", "Mukhamandapa", "Prakara Walls", "Sacred Kunda"]))
		var features = ", ".join(arch_json.get("special_features", ["Shikhara / Vimana", "Deepastambha", "Nandi Mandapa", "Carved Pillars"]))
		var materials = ", ".join(arch_json.get("materials", ["Granite stone", "Sandstone", "Gold kalasha", "Brass bells"]))
		
		txt_arch.text = "[b][color=#ffcc66] Architectural Style:[/color][/b] %s\n" % style_name
		txt_arch.text += "[b][color=#ffcc66]⏳ Historical Period:[/color][/b] %s\n\n" % period
		txt_arch.text += "[b][color=#ffcc66] Key Structures in Kshetra:[/color][/b]\n%s\n\n" % structures
		txt_arch.text += "[b][color=#ffcc66] Notable Architectural Features:[/color][/b]\n%s\n\n" % features
		txt_arch.text += "[b][color=#ffcc66] Sacred Building Materials:[/color][/b]\n%s\n" % materials

	# The current model collection is not identical to the stotram eighteen.
	# Research notes preserve the distinction between main murti, sacred symbol,
	# processional image, and unresolved reconstructions.
	var notes: Dictionary = GameManager.reference_notes.get(temple_id, {})
	if not notes.is_empty():
		if txt_arch:
			txt_arch.text = "[b][color=#d6b780]Architecture and setting[/color][/b]\n%s\n\n" % notes.get("architecture", "")
			if notes.get("reconstruction", false):
				txt_arch.text += "[color=#e4b781]This scene is an interpretive model. A verified historical plan has not been established.[/color]\n\n"
			txt_arch.text += "[color=#a0ada8]The map shows model footprints rather than a surveyed visitor plan.[/color]\n\n"
			for source in notes.get("sources", []):
				txt_arch.text += "[url=%s]%s[/url]\n" % [source.get("url", ""), source.get("title", "Source")]
			if notes.has("preservation_status"):
				txt_arch.text += "\n[b][color=#d6b780]Carvings and inscriptions[/color][/b]\n%s\n" % _safe_bbcode(str(notes["preservation_status"]))
			if not txt_arch.meta_clicked.is_connected(_open_reference):
				txt_arch.meta_clicked.connect(_open_reference)
		if txt_heritage:
			var form_text = "[b][color=#d6b780]The main sacred form[/color][/b]\n%s\nPosture: %s\nArms: %s\nAttributes: %s\n\n" % [notes.get("deity_form", "Unverified"), notes.get("posture", "Unverified"), notes.get("arms", "Unverified"), notes.get("attributes", "Unverified")]
			if notes.get("reconstruction", false):
				form_text = "[b][color=#e4b781]Interpretive reconstruction[/color][/b]\nThis model is an artistic interpretation. Its layout and iconography are not an authenticated reconstruction.\n\n" + form_text
			form_text += "[color=#a0ada8]Reference limits: %s[/color]\n\n" % notes.get("uncertainties", "")
			for source in notes.get("sources", []):
				form_text += "[url=%s]%s[/url]\n" % [source.get("url", ""), source.get("title", "Source")]
			txt_heritage.text = form_text + "\n" + txt_heritage.text
			if not txt_heritage.meta_clicked.is_connected(_open_reference):
				txt_heritage.meta_clicked.connect(_open_reference)

func _read_json_file(path: String) -> Dictionary:
	if heritage_data_cache.has(path):
		return heritage_data_cache[path]
	
	var target = path
	if not FileAccess.file_exists(target):
		var abs_target = ProjectSettings.globalize_path(target)
		if FileAccess.file_exists(abs_target):
			target = abs_target
		else:
			return {}
	
	var file = FileAccess.open(target, FileAccess.READ)
	if file == null:
		return {}
	var text = file.get_as_text()
	var json = JSON.new()
	var err = json.parse(text)
	if err == OK and json.data is Dictionary:
		heritage_data_cache[path] = json.data
		return json.data
	return {}

# ==============================================================================
# MINIMAP RADAR & NAVIGATION
# ==============================================================================

func toggle_minimap() -> void:
	if not shrine_map_window:
		return
	if shrine_map_window.visible:
		_close_shrine_map()
		return
	if heritage_modal and heritage_modal.visible:
		_close_heritage()
	_rebuild_model_map()
	_refresh_shrine_destinations()
	shrine_map_window.show()
	if modal_backdrop:
		modal_backdrop.show()
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	minimap_panel.queue_redraw()

func _rebuild_model_map() -> void:
	map_shapes.clear()
	map_points.clear()
	var world = find_parent("TempleWorld")
	if world == null:
		return
	var holder = world.get_node_or_null("TempleModelHolder")
	if holder == null:
		return
	_collect_map_shapes(holder)
	var registry = world.get("shrine_registry")
	if registry is Node:
		_collect_map_shapes(registry)
	if map_shapes.is_empty():
		return
	map_bounds = map_shapes[0]["rect"]
	for shape in map_shapes:
		map_bounds = map_bounds.merge(shape["rect"])
	map_bounds = map_bounds.grow(3.0)

func _collect_map_shapes(node: Node) -> void:
	if node is Node3D and not node.visible:
		return
	if node is Node3D and not node.is_visible_in_tree():
		return
	if node is MeshInstance3D and node.mesh != null:
		var key = str(node.name).to_lower()
		if not ("ground" in key or "terrain" in key or "priest" in key or "tree" in key or "flame" in key or "flower" in key):
			var box: AABB = node.global_transform * node.get_aabb()
			var rect = Rect2(Vector2(box.position.x, box.position.z), Vector2(box.size.x, box.size.z))
			if rect.size.x > 0.12 and rect.size.y > 0.12:
				var col = Color("69766c")
				if "water" in key or "tank" in key or "kunda" in key:
					col = Color("477d89")
				elif "wall" in key or "prakara" in key:
					col = Color("c1aa7c")
				elif "roof" in key or "shikhara" in key or "vimana" in key:
					col = Color("89977f")
				map_shapes.append({"rect": rect, "color": col})
		if "deity" in key or "ghanta" in key or "spawn" in key:
			var box: AABB = node.global_transform * node.get_aabb()
			map_points.append({"point": Vector2(box.get_center().x, box.get_center().z), "deity": "deity" in key})
	for child in node.get_children():
		_collect_map_shapes(child)

func _on_minimap_draw() -> void:
	if minimap_panel == null:
		return
	var panel = Rect2(Vector2.ZERO, minimap_panel.size)
	minimap_panel.draw_style_box(_style_panel(Color("101b1be8"), Color("607065"), 0), panel)
	minimap_panel.draw_string(ThemeDB.fallback_font, Vector2(12, 21), "COMPLEX MAP", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, GOLD)
	minimap_panel.draw_string(ThemeDB.fallback_font, Vector2(12, panel.size.y - 10), "Numbered shrines · select a marker or use the list", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, MUTED)
	if map_shapes.is_empty():
		return
	var usable = panel.size - Vector2(24, 60)
	var scale_factor = minf(usable.x / maxf(map_bounds.size.x, 1), usable.y / maxf(map_bounds.size.y, 1))
	var origin = Vector2(12, 32) + (usable - map_bounds.size * scale_factor) * 0.5
	for shape in map_shapes:
		var rect: Rect2 = shape["rect"]
		var mapped = Rect2(origin + (rect.position - map_bounds.position) * scale_factor, rect.size * scale_factor)
		minimap_panel.draw_rect(mapped, Color(shape["color"], 0.3), true)
		minimap_panel.draw_rect(mapped, Color(shape["color"], 0.65), false, 0.7)
	map_marker_positions.clear()
	for index in range(shrine_destinations.size()):
		var destination: Dictionary = shrine_destinations[index]
		var shrine_point: Vector3 = destination.get("target", destination.get("position", Vector3.ZERO))
		var marker = origin + (Vector2(shrine_point.x, shrine_point.z) - map_bounds.position) * scale_factor
		var actual_marker = marker
		# Worship locations can share an altar or cave. Separate their numbered
		# buttons while retaining a leader line to the shared physical location.
		for attempt in range(18):
			var crowded = false
			for previous_marker in map_marker_positions.values():
				if marker.distance_to(previous_marker) < 23:
					crowded = true
					break
			if not crowded:
				break
			var angle = float(attempt) * 2.39996
			marker = actual_marker + Vector2(cos(angle), sin(angle)) * (17.0 + float(attempt) * 3.0)
		marker = marker.clamp(Vector2(22, 44), panel.size - Vector2(22, 30))
		if marker.distance_to(actual_marker) > 1:
			minimap_panel.draw_line(actual_marker, marker, Color(GOLD, .65), 1, true)
		var shrine_id = str(destination.get("id", ""))
		map_marker_positions[shrine_id] = marker
		var selected = shrine_id == selected_shrine
		minimap_panel.draw_circle(marker, 12.0 if selected else 10.0, GOLD if selected else Color("244c50"))
		minimap_panel.draw_arc(marker, 10.0, 0, TAU, 24, GOLD, 1.0, true)
		var number = str(index + 1)
		var number_size = ThemeDB.fallback_font.get_string_size(number, HORIZONTAL_ALIGNMENT_LEFT, -1, 11)
		minimap_panel.draw_string(ThemeDB.fallback_font, marker + Vector2(-number_size.x * .5, 4), number, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, INK if selected else TEXT)
	var world = find_parent("TempleWorld")
	var player_node = world.get_node_or_null("Player") as Node3D if world else null
	if player_node:
		var pos = Vector2(player_node.global_position.x, player_node.global_position.z)
		var center = origin + (pos - map_bounds.position) * scale_factor
		center = center.clamp(Vector2(10, 30), panel.size - Vector2(10, 28))
		var forward = Vector2(-sin(player_node.rotation.y), -cos(player_node.rotation.y)) * 7.0
		var right = Vector2(-forward.y, forward.x) * 0.5
		minimap_panel.draw_colored_polygon(PackedVector2Array([center + forward, center - forward * 0.6 + right, center - forward * 0.6 - right]), TEXT)

func is_modal_open() -> bool:
	return (heritage_modal != null and heritage_modal.visible) or (shrine_map_window != null and shrine_map_window.visible)

func _close_heritage() -> void:
	if heritage_modal:
		heritage_modal.visible = false
	if modal_backdrop:
		modal_backdrop.visible = false
	set_meta("modal_open", false)
	if not GameManager.mobile_mode:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var typing = get_viewport().gui_get_focus_owner() is LineEdit
		if shrine_map_window and shrine_map_window.visible and (event.keycode == KEY_ESCAPE or event.keycode == KEY_M and not typing):
			_close_shrine_map()
			get_viewport().set_input_as_handled()
		elif heritage_modal and heritage_modal.visible and event.keycode in [KEY_ESCAPE, KEY_H]:
			_close_heritage()
			get_viewport().set_input_as_handled()

func _apply_theme() -> void:
	var ui_theme = Theme.new()
	ui_theme.default_font_size = 14
	ui_theme.set_color("font_color", "Label", TEXT)
	ui_theme.set_color("font_color", "Button", TEXT)
	ui_theme.set_color("font_hover_color", "Button", Color.WHITE)
	ui_theme.set_stylebox("normal", "Button", _style_panel(Color("1b2827e8"), Color("425348"), 9))
	ui_theme.set_stylebox("hover", "Button", _style_panel(Color("35453a"), GOLD, 9))
	ui_theme.set_stylebox("pressed", "Button", _style_panel(Color("3c4732"), GOLD, 9))
	ui_theme.set_stylebox("focus", "Button", _style_panel(Color.TRANSPARENT, GOLD, 9))
	ui_theme.set_stylebox("normal", "LineEdit", _style_panel(PANEL, Color("425348"), 10))
	ui_theme.set_stylebox("focus", "LineEdit", _style_panel(PANEL, GOLD, 10))
	theme = ui_theme
	if header_info:
		header_info.clip_text = true
		header_info.add_theme_color_override("font_color", TEXT)
		for name in ["BtnHeritage", "BtnMinimap", "BtnSound", "BtnMenu"]:
			var button = _get_ui_node(["TopBar/" + name, "HUDRoot/TopBar/" + name]) as Button
			if button:
				button.add_theme_font_size_override("font_size", 12)
		var map_button = _get_ui_node(["TopBar/BtnMinimap", "HUDRoot/TopBar/BtnMinimap"]) as Button
		if map_button:
			map_button.text = "Map [M]"
		var heritage_button = _get_ui_node(["TopBar/BtnHeritage", "HUDRoot/TopBar/BtnHeritage"]) as Button
		if heritage_button:
			heritage_button.text = "Heritage [H]"
		var menu_button = _get_ui_node(["TopBar/BtnMenu", "HUDRoot/TopBar/BtnMenu"]) as Button
		if menu_button:
			menu_button.text = "Destinations"
		var sound_button = _get_ui_node(["TopBar/BtnSound", "HUDRoot/TopBar/BtnSound"]) as Button
		if sound_button:
			sound_button.text = "Sound [B]"
	if sky_bar:
		sky_bar.offset_left = -390
		var sky_label = sky_bar.get_node_or_null("SkyLabel") as Label
		if sky_label:
			sky_label.visible = false
		var sky_labels = ["1 Dawn", "2 Day", "3 Afternoon", "4 Sunset", "5 Night"]
		for i in range(1, 6):
			var sky_button = sky_bar.get_node_or_null("Sky%d" % i) as Button
			if sky_button:
				sky_button.text = sky_labels[i - 1]
				sky_button.add_theme_font_size_override("font_size", 11)
	if seva_bar:
		var texts = ["Prayer [P]", "Pranam [K]", "Flowers [F]", "Bell [G]", "Aarti [R]", "Prasadam [T]", "Conch [C]", "Mantra [N]"]
		for i in range(mini(texts.size(), seva_bar.get_child_count())):
			var button = seva_bar.get_child(i) as Button
			if button:
				button.text = texts[i]
				button.add_theme_font_size_override("font_size", 12)
	if minimap_panel:
		minimap_panel.offset_right = 280
		minimap_panel.offset_top = -345
		minimap_panel.offset_bottom = -75
	if heritage_modal:
		heritage_modal.add_theme_stylebox_override("panel", _style_panel(INK, GOLD, 20))
		modal_backdrop = ColorRect.new()
		modal_backdrop.color = Color(0.01, 0.03, 0.03, 0.7)
		modal_backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		modal_backdrop.visible = false
		add_child(modal_backdrop)
		move_child(heritage_modal, -1)
		var close_button = _get_ui_node(["HeritageModal/VBox/BtnClose", "HUDRoot/HeritageModal/VBox/BtnClose"]) as Button
		if close_button:
			close_button.text = "Return to darshan  [Esc]"


func _open_reference(meta: Variant) -> void:
	var url = str(meta)
	if url.begins_with("https://"):
		OS.shell_open(url)

func _setup_touch_controls() -> void:
	if not GameManager.mobile_mode:
		return
	var player = find_parent("TempleWorld").get_node_or_null("Player")
	if player == null:
		return
	var directions = {"↑": Vector2(0, -1), "←": Vector2(-1, 0), "↓": Vector2(0, 1), "→": Vector2(1, 0)}
	var positions = {"↑": Vector2(78, -218), "←": Vector2(18, -158), "↓": Vector2(78, -158), "→": Vector2(138, -158)}
	var held: Dictionary = {}
	for key in directions:
		var button = Button.new()
		button.text = key
		button.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
		button.position = Vector2(positions[key].x, size.y + positions[key].y)
		button.size = Vector2(56, 56)
		button.focus_mode = Control.FOCUS_NONE
		add_child(button)
		button.button_down.connect(func():
			held[key] = directions[key]
			var movement = Vector2.ZERO
			for direction in held.values():
				movement += direction
			player.virtual_move_vector = movement.limit_length())
		button.button_up.connect(func():
			held.erase(key)
			var movement = Vector2.ZERO
			for direction in held.values():
				movement += direction
			player.virtual_move_vector = movement.limit_length())
	var look_pad = PanelContainer.new()
	look_pad.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	look_pad.position = Vector2(size.x - 190, size.y - 240)
	look_pad.size = Vector2(170, 155)
	look_pad.add_theme_stylebox_override("panel", _style_panel(Color("18232399"), Color("60706599"), 12))
	var hint = _label("Drag to look", 12, MUTED)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	look_pad.add_child(hint)
	add_child(look_pad)
	look_pad.gui_input.connect(func(event: InputEvent):
		if is_modal_open():
			return
		if event is InputEventScreenDrag:
			player._apply_look(event.relative.x, event.relative.y)
		elif event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_LEFT:
			player._apply_look(event.relative.x, event.relative.y))
func _setup_shrine_map() -> void:
	shrine_map_window = PanelContainer.new()
	shrine_map_window.name = "ShrineMapWindow"
	shrine_map_window.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shrine_map_window.offset_left = 36
	shrine_map_window.offset_top = 70
	shrine_map_window.offset_right = -36
	shrine_map_window.offset_bottom = -70
	shrine_map_window.add_theme_stylebox_override("panel", _style_panel(INK, GOLD, 18))
	add_child(shrine_map_window)
	var column = VBoxContainer.new()
	column.add_theme_constant_override("separation", 10)
	shrine_map_window.add_child(column)
	var header = HBoxContainer.new()
	column.add_child(header)
	var heading = _label("Shrines & darshan", 24, TEXT)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(heading)
	var close = Button.new()
	close.text = "Return  [Esc]"
	close.pressed.connect(_close_shrine_map)
	header.add_child(close)
	shrine_scope_label = _label("Within the main temple complex. Model footprints are not a surveyed visitor plan.", 12, MUTED)
	column.add_child(shrine_scope_label)
	var body = HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 16)
	column.add_child(body)
	var map_column = VBoxContainer.new()
	map_column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	map_column.size_flags_stretch_ratio = 1.45
	body.add_child(map_column)
	minimap_panel = Control.new()
	minimap_panel.name = "ShrineMapCanvas"
	minimap_panel.custom_minimum_size = Vector2(260, 220)
	minimap_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	minimap_panel.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	minimap_panel.draw.connect(_on_minimap_draw)
	minimap_panel.gui_input.connect(_on_shrine_map_input)
	map_column.add_child(minimap_panel)
	shrine_selected_label = RichTextLabel.new()
	shrine_selected_label.bbcode_enabled = true
	shrine_selected_label.text = "Choose a numbered shrine to read its tradition, sacred form and references. Use Teleport to arrive at its entrance."
	shrine_selected_label.custom_minimum_size.y = 145
	shrine_selected_label.add_theme_font_size_override("normal_font_size", 14)
	shrine_selected_label.meta_clicked.connect(_open_reference)
	map_column.add_child(shrine_selected_label)
	narration_player = AudioStreamPlayer.new()
	narration_player.name = "GuideNarration"
	narration_player.volume_db = -1.0
	add_child(narration_player)
	narration_button = Button.new()
	narration_button.text = "Listen to shrine guide"
	narration_button.visible = false
	narration_button.pressed.connect(_play_selected_narration)
	map_column.add_child(narration_button)
	var directory = VBoxContainer.new()
	directory.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	directory.size_flags_stretch_ratio = 1.0
	directory.custom_minimum_size.x = 300
	body.add_child(directory)
	shrine_search = LineEdit.new()
	shrine_search.placeholder_text = "Find a deity, shrine or acharya..."
	shrine_search.text_changed.connect(func(_query): _populate_shrine_list())
	directory.add_child(shrine_search)
	var scroll = ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	directory.add_child(scroll)
	shrine_list = VBoxContainer.new()
	shrine_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	shrine_list.add_theme_constant_override("separation", 8)
	scroll.add_child(shrine_list)
	shrine_map_window.hide()

func _refresh_shrine_destinations() -> void:
	shrine_destinations.clear()
	var world = find_parent("TempleWorld")
	var registry = world.get("shrine_registry") if world else null
	if registry and registry.has_method("get_destinations"):
		shrine_destinations = registry.get_destinations()
		if registry.has_signal("registry_ready") and not registry.is_connected("registry_ready", _on_registry_ready):
			registry.connect("registry_ready", _on_registry_ready)
	var catalog = _read_json_file("res://data/shrine_catalog.json")
	var complex_data: Dictionary = catalog.get("temples", {}).get(GameManager.current_temple_id, {})
	shrine_scope_label.text = str(complex_data.get("scope_note", "Only documented shrines within this main temple complex are listed.")) + " Model footprints and schematic placements are not a surveyed visitor plan."
	_populate_shrine_list()
	if minimap_panel:
		minimap_panel.queue_redraw()

func _populate_shrine_list() -> void:
	if not shrine_list:
		return
	for child in shrine_list.get_children():
		child.free()
	var query = shrine_search.text.strip_edges().to_lower() if shrine_search else ""
	var count = 0
	for index in range(shrine_destinations.size()):
		var destination: Dictionary = shrine_destinations[index]
		var label = str(destination.get("label", "Shrine"))
		if not query.is_empty() and not query in (label + " " + str(destination.get("deity", ""))).to_lower():
			continue
		count += 1
		var row = PanelContainer.new()
		row.add_theme_stylebox_override("panel", _style_panel(PANEL, Color("344842"), 10))
		shrine_list.add_child(row)
		var column = VBoxContainer.new()
		column.add_theme_constant_override("separation", 5)
		row.add_child(column)
		var title = _label("%02d  %s" % [index + 1, label], 15, TEXT)
		title.tooltip_text = str(destination.get("notes", ""))
		column.add_child(title)
		var status = str(destination.get("placement_status", "schematic_position"))
		var detail = str(destination.get("kind", "shrine")).capitalize()
		if status == "schematic_position":
			detail += " · schematic placement"
		elif status == "unavailable":
			detail += " · safe arrival unavailable"
		var subtitle = _label(detail, 11, MUTED)
		column.add_child(subtitle)
		var actions = HBoxContainer.new()
		column.add_child(actions)
		var locate = Button.new()
		locate.text = "Locate"
		locate.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var shrine_id = str(destination.get("id", ""))
		locate.pressed.connect(func(): _select_shrine(shrine_id))
		actions.add_child(locate)
		var teleport = Button.new()
		teleport.text = "Teleport  →"
		teleport.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		teleport.disabled = not bool(destination.get("available", true)) or status == "unavailable"
		teleport.pressed.connect(func(): _teleport_to_shrine(shrine_id))
		actions.add_child(teleport)
	if count == 0:
		shrine_list.add_child(_label("No matching shrine." if not shrine_destinations.is_empty() else "Shrine destinations are being prepared.", 14, MUTED))

func _select_shrine(shrine_id: String) -> void:
	selected_shrine = shrine_id
	if narration_button:
		narration_button.visible = not _narration_path(shrine_id).is_empty()
	for destination in shrine_destinations:
		if str(destination.get("id", "")) == shrine_id:
			shrine_selected_label.text = "[b][color=#d6b780]%s[/color][/b]\n" % _safe_bbcode(str(destination.get("label", "")))
			shrine_selected_label.text += _safe_bbcode(str(destination.get("tradition", destination.get("notes", "Tradition under reference review.")))) + "\n"
			shrine_selected_label.text += _safe_bbcode(str(destination.get("notes", ""))) + "\n"
			shrine_selected_label.text += "[color=#a0ada8]Sacred form: %s\nArtwork: %s[/color]\n" % [_safe_bbcode(str(destination.get("form", "Unverified")).replace("_", " ")), _safe_bbcode(str(destination.get("artwork_status", "Reference review pending.")))]
			var catalog = _read_json_file("res://data/shrine_catalog.json")
			var campus: Dictionary = catalog.get("temples", {}).get(GameManager.current_temple_id, {})
			for source in campus.get("sources", []):
				if source.get("id", "") in destination.get("source_ids", []):
					var url = str(source.get("url", ""))
					if url.begins_with("https://"):
						shrine_selected_label.text += "[url=%s]%s[/url]\n" % [url, _safe_bbcode(str(source.get("title", "Reference")))]
			break
	minimap_panel.queue_redraw()

func _safe_bbcode(value: String) -> String:
	return value.replace("[", "[lb]")

func _narration_path(shrine_id: String) -> String:
	var manifest = _read_json_file("res://data/narration_manifest.json")
	for item in manifest.get("items", []):
		if item.get("temple_id", "") == GameManager.current_temple_id and item.get("shrine_id", "") == shrine_id:
			var path = str(item.get("path", ""))
			if ResourceLoader.exists(path):
				return path
	return ""

func _play_selected_narration() -> void:
	if not GameManager.sound_enabled:
		show_toast("Sound is off", "Enable sound [B] to hear the guide.", 2.0)
		return
	if narration_player.playing:
		narration_player.stop()
		return
	var path = _narration_path(selected_shrine)
	if not path.is_empty():
		narration_player.stream = load(path)
		narration_player.play()

func _teleport_to_shrine(shrine_id: String) -> void:
	var world = find_parent("TempleWorld")
	var registry = world.get("shrine_registry") if world else null
	if registry and registry.teleport_to(shrine_id):
		var label = "Shrine"
		for destination in shrine_destinations:
			if str(destination.get("id", "")) == shrine_id:
				label = str(destination.get("label", "Shrine"))
		_close_shrine_map()
		show_toast(label, "Arrived at the shrine entrance.", 2.4)
	else:
		shrine_selected_label.text = "A safe entrance arrival could not be found. Please approach this shrine on foot."

func _close_shrine_map() -> void:
	if narration_player:
		narration_player.stop()
	if shrine_map_window:
		shrine_map_window.hide()
	if modal_backdrop:
		modal_backdrop.hide()
	if not GameManager.mobile_mode:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _on_shrine_map_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var nearest_id = ""
		var nearest_distance = 18.0
		for shrine_id in map_marker_positions:
			var distance = event.position.distance_to(map_marker_positions[shrine_id])
			if distance < nearest_distance:
				nearest_distance = distance
				nearest_id = shrine_id
		if not nearest_id.is_empty():
			_select_shrine(nearest_id)
			minimap_panel.accept_event()

func _on_registry_ready() -> void:
	_refresh_shrine_destinations()
	_rebuild_model_map()
