extends SceneTree

## Main Script
## Handles --qa-smoke structural checks of the playable GLB collection.
## and normal startup routing to main_menu.tscn.

const TEMPLE_IDS: Array[String] = [
	"draksharama_manikyamba",
	"jwalamukhi_vaishnavi",
	"kashmir_sharada",
	"kamakhya",
	"kalighat",
	"kashi_vishalakshi",
	"kanchipuram_kamakshi",
	"madurai_meenakshi",
	"mysore_chamundeshwari",
	"kolhapur_mahalakshmi",
	"tuljapur_bhavani",
	"mahur_renuka",
	"alampur_jogulamba",
	"srisailam_bhramaramba",
	"pithapuram_puruhutika",
	"jajpur_biraja",
	"ujjain_mahakali",
	"prayag_madhaveswari",
	"gaya_mangalagauri",
	"pradyumna_shrinkhala",
	"lanka_shankari"
]

func _init() -> void:
	var args = OS.get_cmdline_args()
	var user_args = OS.get_cmdline_user_args()
	var is_smoke: bool = false
	
	for a in args:
		if a == "--qa-smoke":
			is_smoke = true
	for a in user_args:
		if a == "--qa-smoke":
			is_smoke = true
	
	if is_smoke:
		quit(run_qa_smoke())
	else:
		change_scene_to_file("res://scenes/main_menu.tscn")

func run_qa_smoke() -> int:
	print("==================================================")
	print("  ASHTA DASHA MAHA SHAKTI PEETHA - QA SMOKE TEST  ")
	print("==================================================")
	print("Verifying %d playable GLB models in res://assets/models/ ...\n" % TEMPLE_IDS.size())
	
	var pass_count: int = 0
	var fail_count: int = 0
	
	for id in TEMPLE_IDS:
		var glb_rel_path = "res://assets/models/%s_kshetra_full.glb" % id
		var glb_abs_path = ProjectSettings.globalize_path(glb_rel_path)
		
		# Check existence
		if not FileAccess.file_exists(glb_rel_path) and not FileAccess.file_exists(glb_abs_path):
			print("[FAIL] %s: GLB file not found at %s" % [id, glb_rel_path])
			fail_count += 1
			continue
		
		var target_path = glb_rel_path if FileAccess.file_exists(glb_rel_path) else glb_abs_path
		
		# Load GLTF scene
		var gltf = GLTFDocument.new()
		var state = GLTFState.new()
		var err = gltf.append_from_file(target_path, state)
		if err != OK:
			print("[FAIL] %s: GLTF parse error code %d" % [id, err])
			fail_count += 1
			continue
		
		var root_node = gltf.generate_scene(state)
		if root_node == null:
			print("[FAIL] %s: generate_scene returned null" % id)
			fail_count += 1
			continue
		# Ruins and natural-flame sites must not acquire invented priests,
		# bells or anthropomorphic idols to satisfy an old generic smoke test.
		var special_anchor = {"pradyumna_shrinkhala": "Pandua_Minar", "kashmir_sharada": "Sanctuary_Ruins", "jwalamukhi_vaishnavi": "SacredFlame_Mahakali", "draksharama_manikyamba": "Bhimeswara_Linga"}
		if special_anchor.has(id):
			var present = _find_node_fuzzy(root_node, special_anchor[id]) != null and _find_node_fuzzy(root_node, "Spawn") != null
			if present:
				pass_count += 1
				print("[PASS] %s: present-condition landmark and spawn found (not an authenticity certification)" % id)
			else:
				fail_count += 1
				print("[FAIL] %s: missing present-condition landmark or spawn" % id)
			root_node.free()
			continue
		
		# Check required nodes: Garbhagriha, Deity_*, Priest, Ghanta
		var node_garbhagriha = _find_node_fuzzy(root_node, "Garbhagriha")
		var node_deity = _find_node_fuzzy(root_node, "Deity")
		var node_priest = _find_node_fuzzy(root_node, "Priest")
		var node_ghanta = _find_node_fuzzy(root_node, "Ghanta")
		if node_ghanta == null:
			node_ghanta = _find_node_fuzzy(root_node, "Bell")
		
		# Optional / helpful nodes
		var node_mandapa = _find_node_fuzzy(root_node, "Mandapa")
		var node_spawn = _find_node_fuzzy(root_node, "Spawn")
		
		var missing: Array[String] = []
		if node_garbhagriha == null:
			missing.append("Garbhagriha")
		if node_deity == null:
			missing.append("Deity_*")
		if node_priest == null:
			missing.append("Priest")
		if node_ghanta == null:
			missing.append("Ghanta")
		
		if missing.is_empty():
			var deity_name = node_deity.name if node_deity else "Deity"
			var priest_name = node_priest.name if node_priest else "Priest"
			var ghanta_name = node_ghanta.name if node_ghanta else "Ghanta"
			print("[PASS] %s: verified (Garbhagriha, %s, %s, %s)" % [id, deity_name, priest_name, ghanta_name])
			pass_count += 1
		else:
			print("[FAIL] %s: missing required nodes [%s]" % [id, ", ".join(missing)])
			fail_count += 1
		
		root_node.free()
	
	print("\n==================================================")
	print("QA Smoke Test Completed: %d PASS, %d FAIL / %d Total" % [pass_count, fail_count, TEMPLE_IDS.size()])
	print("==================================================")
	return 1 if fail_count > 0 else 0

func _find_node_fuzzy(root: Node, search_text: String) -> Node:
	if root == null:
		return null
	var lower_search = search_text.to_lower()
	if lower_search in root.name.to_lower():
		return root
	for child in root.get_children():
		var found = _find_node_fuzzy(child, search_text)
		if found != null:
			return found
	return null
