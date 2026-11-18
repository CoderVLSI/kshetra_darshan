class_name ShrineRegistry
extends Node3D

## Documented, campus-scoped shrine destinations. New artwork and unsurveyed
## placement are explicitly interpretive. A destination is enabled only after
## a floor and full player-capsule clearance check succeeds.
signal registry_ready
signal destination_selected(destination: Dictionary)

var temple_id: String
var scope_note: String = ""
var excluded: Array = []
var sources: Array = []
var _model: Node3D
var _player: CharacterBody3D
var _destinations: Array[Dictionary] = []
var _reserved: Array[Vector3] = []
var _catalog: Dictionary = {}
var _bounds := AABB()
var _materials: Dictionary = {}
var is_ready: bool = false
var _space: PhysicsDirectSpaceState3D
var _identity_labels: Array[Dictionary] = []
var _label_tick: float = 0.0

func _process(delta: float) -> void:
	_label_tick -= delta
	if _label_tick > 0 or not is_instance_valid(_player):
		return
	_label_tick = .20
	var camera := get_viewport().get_camera_3d()
	var nearby: Array[Dictionary] = []
	for identity in _identity_labels:
		var distance: float = _player.global_position.distance_to(identity["target"])
		identity["distance"] = distance
		identity["group"].visible = false
		if camera and not camera.is_position_in_frustum(identity["group"].global_position):
			continue
		if distance < 12.0:
			nearby.append(identity)
	nearby.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["distance"] < b["distance"])
	# At darshan distance, a second shrine name on the same sightline can
	# appear to identify the wrong sculpture. Show only the approached shrine.
	var limit := 1 if not nearby.is_empty() and float(nearby[0]["distance"]) < 3.5 else 3
	for index in range(mini(limit, nearby.size())):
		nearby[index]["group"].visible = true
		# Tradition belongs in the nearby inspection panel, not another floating
		# paragraph over the murti. Keep it as metadata for that panel and map.
		nearby[index]["context"].visible = false

func setup(id: String, model_root: Node3D, player: CharacterBody3D) -> void:
	temple_id = id
	_model = model_root
	_player = player
	name = "ShrineRegistry"
	var file = FileAccess.open("res://data/shrine_catalog.json", FileAccess.READ)
	if file:
		var parsed = JSON.parse_string(file.get_as_text())
		if parsed is Dictionary:
			_catalog = parsed.get("temples", {}).get(id, {})
	scope_note = str(_catalog.get("scope_note", "Main temple complex only; shrine inventory remains under review."))
	excluded = _catalog.get("excluded", [])
	sources = _catalog.get("sources", [])
	call_deferred("_populate")

func get_destinations() -> Array[Dictionary]:
	return _destinations.duplicate(true)

func teleport_to(id: String) -> bool:
	if not is_instance_valid(_player):
		return false
	for destination in _destinations:
		if destination["id"] != id or not destination.get("available", false):
			continue
		var position: Vector3 = destination["position"]
		if not _landing_clear(position):
			# Recompute if another object has moved into the original landing.
			position = _find_landing(destination["target"], position.y)
			if not position.is_finite():
				return false
		_player.global_position = position + Vector3.UP * 0.025
		_player.velocity = Vector3.ZERO
		_player.set("virtual_move_vector", Vector2.ZERO)
		_player.set("virtual_look_vector", Vector2.ZERO)
		var target: Vector3 = destination["target"]
		target.y = _player.global_position.y
		if target.distance_squared_to(_player.global_position) > .01:
			_player.look_at(target, Vector3.UP)
		_player.rotation.x = 0.0
		_player.rotation.z = 0.0
		destination_selected.emit(destination)
		return true
	return false

func _populate() -> void:
	await get_tree().physics_frame
	if not is_instance_valid(_model) or not is_instance_valid(_player):
		return
	_space = get_world_3d().direct_space_state
	_suppress_unlisted_generic_shrines()
	_bounds = _architectural_bounds(_model)
	# A second physics tick removes disabled generic shrine collision bodies.
	await get_tree().physics_frame
	var entries: Array = _catalog.get("shrines", [])
	for entry_value in entries:
		if not entry_value is Dictionary:
			continue
		var entry: Dictionary = entry_value
		var study = preload("res://scripts/shrine_sculpture.gd").new()
		var anchor = _resolve_anchor(entry)
		var target := Vector3.ZERO
		var status := "existing_model_anchor"
		var artwork := "Existing model; detailed iconography remains subject to reference review."
		if entry.has("hall_slot"):
			var hall = _model.find_child(str(entry.placement_mesh), true, false) as MeshInstance3D
			status = "schematic_position"
			if hall:
				var bounds: AABB = hall.global_transform * hall.get_aabb()
				var slot: Array = entry.hall_slot
				var base := bounds.position + Vector3(bounds.size.x * slot[0], .1, bounds.size.z * slot[1])
				var inner := Node3D.new()
				add_child(inner)
				inner.name = "Shrine_" + str(entry.id)
				inner.global_position = base
				inner.rotation.y = PI / 2 if slot[0] < .5 else -PI / 2
				if study.supports(entry):
					inner.add_child(study.build(entry))
					artwork = "Iconographic study within %s. Exact position and installed image remain unverified." % entry.placement_context
				elif entry.has("figure_from_mesh") and _place_imported_figure(inner, entry.figure_from_mesh):
					artwork = "Existing deity study in the documented mandapa. Individual bay and iconography remain approximate."
				else:
					artwork = "Reference location at %s. Installed image remains unverified." % entry.placement_context
				target = base + Vector3.UP
				_reserved.append(base)
			else:
				status = "unavailable"
		elif anchor:
			target = _anchor_center(anchor)
			if entry.get("render_iconographic_study", false) and study.supports(entry):
				anchor.add_child(study.build(entry))
				artwork = "Iconographic study in the documented sanctum. Installed image details remain unverified."
			elif "Reference" in str(anchor.name) or entry.get("installed_image_unverified", false):
				artwork = "Reference location — installed image not reconstructed."
			elif entry.get("kind", "") == "heritage":
				artwork = "Present-day monument study; dimensions and surviving details remain approximate."
			artwork = str(entry.get("artwork_description", artwork))
		else:
			status = "schematic_position"
			artwork = "Stylised shrine and sacred-form study; exact sculpture and placement are not surveyed."
			# Matangi and Kamala share Kamakhya's cave. They must never be
			# packed into separate courtyard temples by the general staging grid.
			if temple_id == "kamakhya" and entry.get("id", "") in ["matangi", "kamala"]:
				var main_anchor = _first_main_deity(_model)
				var center = _anchor_center(main_anchor)
				var side = -1.0 if entry["id"] == "matangi" else 1.0
				var base = _floor_at(center + Vector3(side * 2.0, 0, -1.4), center.y)
				if base.is_finite():
					var peetha = Node3D.new()
					peetha.name = "Shrine_" + entry["id"]
					add_child(peetha)
					peetha.global_position = base
					var stone = _material("basalt", Color(.065, .06, .055))
					_sphere(peetha, "NaturalStoneReference", Vector3(0,.18,0), Vector3(.70,.36,.60), stone)
					_box(peetha, "RedOfferingCloth", Vector3(0,.28,.02), Vector3(.52,.025,.44), _material("cloth", Color(.57,.065,.045)))
					target = base + Vector3(0,.25,0)
					_reserved.append(base)
					entry = entry.duplicate()
					entry["placement"] = [base.x, base.y, base.z]
					entry["shared_sanctum_built"] = true
			var specified = entry.get("placement")
			var base: Vector3 = Vector3(INF, INF, INF)
			if specified is Array and specified.size() == 3:
				base = Vector3(float(specified[0]), float(specified[1]), float(specified[2]))
				if not _shrine_space_clear(base):
					base = Vector3(INF, INF, INF)
			if entry.get("shared_sanctum_built", false):
				base = Vector3(specified[0], specified[1], specified[2])
			elif not base.is_finite():
				base = _find_shrine_position()
			if entry.get("shared_sanctum_built", false):
				pass
			elif base.is_finite():
				var shrine = _build_shrine(entry)
				artwork = str(shrine.get_meta("artwork_status", artwork))
				add_child(shrine)
				shrine.global_position = base
				_reserved.append(base)
				target = base + Vector3(0, 1.0, 0)
			else:
				status = "unavailable"
				target = _bounds.get_center()
		var landing: Vector3 = Vector3(INF, INF, INF)
		if status != "unavailable":
			var landing_name := str(entry.get("landing_anchor", ""))
			if not landing_name.is_empty():
				var authored := _model.find_child(landing_name, true, false) as Node3D
				if authored:
					var floor := _floor_at(authored.global_position, authored.global_position.y)
					if _landing_clear(floor):
						landing = floor
			if not landing.is_finite():
				landing = _find_landing(target, target.y - 1.0)
		var available: bool = landing.is_finite()
		var destination: Dictionary = {
			"id": str(entry.get("id", "shrine_%d" % _destinations.size())),
			"label": str(entry.get("label", entry.get("deity", "Shrine"))),
			"deity": str(entry.get("deity", "")),
			"form": str(entry.get("form", "unknown")),
			"position": landing if available else target,
			"target": target,
			"kind": str(entry.get("kind", "subsidiary")),
			"notes": str(entry.get("notes", "")),
			"evidence": entry.get("evidence", ""),
			"source_ids": entry.get("source_ids", []),
			"tradition": _tradition_context(entry),
			"placement_status": status,
			"artwork_status": artwork,
			"available": available,
		}
		_destinations.append(destination)
		_add_destination_label(entry, destination)
		if available:
			var marker = Marker3D.new()
			marker.name = "Landing_" + destination["id"].validate_node_name()
			add_child(marker)
			marker.global_position = landing
	is_ready = true
	registry_ready.emit()

func _place_imported_figure(parent: Node3D, source_name: String) -> bool:
	var source = _model.find_child(source_name, true, false) as MeshInstance3D
	if not source or not source.mesh is ArrayMesh:
		return false
	# The old builder joined a sandstone pavilion and a basalt-and-gold idol.
	# Carry the idol surfaces into the documented hall without the pavilion.
	var result := ArrayMesh.new()
	for index in source.mesh.get_surface_count():
		var mat = source.mesh.surface_get_material(index)
		if not mat or not ("basalt" in mat.resource_name.to_lower() or "gold" in mat.resource_name.to_lower()):
			continue
		result.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, source.mesh.surface_get_arrays(index))
		result.surface_set_material(result.get_surface_count() - 1, mat)
	if result.get_surface_count() == 0:
		return false
	var figure := MeshInstance3D.new()
	figure.mesh = result
	var bounds = result.get_aabb()
	figure.position = Vector3(-bounds.get_center().x, -bounds.position.y, -bounds.get_center().z)
	parent.add_child(figure)
	return true

func _resolve_anchor(entry: Dictionary) -> Node3D:
	var anchor_name = str(entry.get("model_anchor", ""))
	if not anchor_name.is_empty():
		var exact = _model.find_child(anchor_name, true, false)
		if exact is Node3D:
			return exact
	if str(entry.get("kind", "")) == "main":
		return _first_main_deity(_model)
	var form = str(entry.get("form", "unknown"))
	var label = str(entry.get("label", "")).to_lower()
	if form == "ganesha":
		return _model.find_child("Ganesha_Shrine", true, false) as Node3D
	if "bhairava" in label:
		return _model.find_child("Bhairava_Shrine", true, false) as Node3D
	return null

func _first_main_deity(node: Node) -> Node3D:
	if str(node.name).begins_with("Deity_") and node is Node3D:
		return node
	for child in node.get_children():
		var found = _first_main_deity(child)
		if found:
			return found
	return null

func _suppress_unlisted_generic_shrines() -> void:
	# Older blockouts placed entire neighbouring temple groups inside a
	# courtyard. Remove those from the complex-only playable presentation.
	var outside_prefixes: Dictionary = {
		"kanchipuram_kamakshi": ["Ganesha_Shrine"],
		"mahur_renuka": ["Parashurama_Shrine", "Matru_Tirtha"],
		"alampur_jogulamba": ["Navabrahma_", "Tungabhadra_Ghat"],
		"kashi_vishalakshi": ["Annapurna_Shrine", "Bhairava_Shrine"],
		"kamakhya": ["Preceding_Shiva_Kameshwara"]
	}
	for prefix in outside_prefixes.get(temple_id, []):
		for node in _model.find_children("*", "Node3D", true, false):
			if String(node.name).begins_with(prefix):
				node.visible = false
				_disable_collision(node)
	var ganesha_listed := false
	var bhairava_listed := false
	for entry in _catalog.get("shrines", []):
		var label = str(entry.get("label", "")).to_lower()
		ganesha_listed = ganesha_listed or entry.get("form", "") == "ganesha" or "ganesh" in label or "ganapati" in label or "vinayaka" in label
		bhairava_listed = bhairava_listed or "bhairav" in label
	for key in ["Ganesha_Shrine", "Bhairava_Shrine"]:
		if (key == "Ganesha_Shrine" and ganesha_listed) or (key == "Bhairava_Shrine" and bhairava_listed):
			continue
		var node = _model.find_child(key, true, false)
		if node is Node3D:
			node.visible = false
			_disable_collision(node)

func _disable_collision(node: Node) -> void:
	if node is CollisionObject3D:
		node.collision_layer = 0
		node.collision_mask = 0
	for child in node.get_children():
		_disable_collision(child)

func _anchor_center(node: Node3D) -> Vector3:
	if node is MeshInstance3D:
		return (node.global_transform * node.get_aabb()).get_center()
	var box = _architectural_bounds(node)
	return box.get_center() if box.size != Vector3.ZERO else node.global_position

func _architectural_bounds(node: Node) -> AABB:
	var bounds := AABB()
	if node is Node3D and not node.visible:
		return bounds
	var key = str(node.name).to_lower()
	if node is MeshInstance3D and not ("ground" in key or "terrain" in key or "sea" in key or "ocean" in key or "river" in key or "hill_base" in key):
		bounds = node.global_transform * node.get_aabb()
	for child in node.get_children():
		var box = _architectural_bounds(child)
		if box.size != Vector3.ZERO:
			bounds = box if bounds.size == Vector3.ZERO else bounds.merge(box)
	return bounds

func _floor_at(point: Vector3, height_limit: float) -> Vector3:
	var ray = PhysicsRayQueryParameters3D.create(Vector3(point.x, height_limit + 1.5, point.z), Vector3(point.x, height_limit - 12.0, point.z), 1, [_player.get_rid()])
	var result = _space.intersect_ray(ray)
	if result.is_empty() or result["normal"].dot(Vector3.UP) < .85:
		return Vector3(INF, INF, INF)
	var collider = result["collider"] as Node
	var key = str(collider.get_parent().name if collider and collider.get_parent() else "").to_lower()
	if "roof" in key or "shikhara" in key or "vimana" in key or "cornice" in key or "uppercap" in key:
		return Vector3(INF, INF, INF)
	return result["position"]

func _landing_clear(feet: Vector3) -> bool:
	if not feet.is_finite():
		return false
	var support = _floor_at(feet, feet.y + .05)
	if not support.is_finite() or absf(support.y - feet.y) > .14:
		return false
	# A centre ray can hit a thin ledge or ornament that cannot support the
	# capsule. Require a small flat footprint around every visitor landing.
	for offset in [Vector3(.26,0,0), Vector3(-.26,0,0), Vector3(0,0,.26), Vector3(0,0,-.26)]:
		var edge = _floor_at(feet + offset, feet.y + .05)
		if not edge.is_finite() or absf(edge.y - feet.y) > .06:
			return false
	var capsule = CapsuleShape3D.new()
	var collision = _player.get_node_or_null("CollisionShape3D") as CollisionShape3D
	if collision and collision.shape is CapsuleShape3D:
		capsule.radius = collision.shape.radius + .025
		capsule.height = collision.shape.height
	else:
		capsule.radius = .375
		capsule.height = 1.75
	var query = PhysicsShapeQueryParameters3D.new()
	query.shape = capsule
	query.transform = Transform3D(Basis.IDENTITY, feet + Vector3.UP * (capsule.height * .5 + .04))
	query.collision_mask = 1
	query.exclude = [_player.get_rid()]
	return _space.intersect_shape(query, 1).is_empty()

func _find_landing(target: Vector3, floor_hint: float) -> Vector3:
	var best := Vector3(INF, INF, INF)
	var best_score := INF
	for ring in [1.9, 2.5, 3.2, 4.2, 5.5, 8.0, 11.0]:
		for index in range(16):
			var angle = TAU * float(index) / 16.0
			var point = target + Vector3(sin(angle) * ring, 0, cos(angle) * ring)
			var floor = _floor_at(point, floor_hint)
			if not floor.is_finite() or not _landing_clear(floor):
				continue
			# Prefer a front-facing view, nearby landing and matching floor level.
			var score = ring + absf(floor.y - floor_hint) * 2.0 + (1.0 - cos(angle)) * .6
			if score < best_score:
				best = floor
				best_score = score
		if best.is_finite():
			return best
	return best

func _shrine_space_clear(base: Vector3) -> bool:
	for occupied in _reserved:
		if Vector2(occupied.x - base.x, occupied.z - base.z).length() < 3.4:
			return false
	var query = PhysicsShapeQueryParameters3D.new()
	var box = BoxShape3D.new()
	box.size = Vector3(2.7, 2.8, 2.8)
	query.shape = box
	query.transform = Transform3D(Basis.IDENTITY, base + Vector3.UP * 1.5)
	query.collision_mask = 1
	query.exclude = [_player.get_rid()]
	return _space.intersect_shape(query, 1).is_empty()

func _find_shrine_position() -> Vector3:
	var border = Rect2(Vector2(_bounds.position.x, _bounds.position.z), Vector2(_bounds.size.x, _bounds.size.z)).grow(-2.0)
	if border.size.x < 4 or border.size.y < 4:
		return Vector3(INF, INF, INF)
	var best := Vector3(INF, INF, INF)
	var best_score := INF
	var floor_hint = _player.global_position.y
	# Deterministic grid packing stays inside the model's authored footprint.
	for ix in range(int(ceil(border.size.x / 2.0))):
		for iz in range(int(ceil(border.size.y / 2.0))):
			var point = Vector3(border.position.x + float(ix) * 2.0, floor_hint, border.position.y + float(iz) * 2.0)
			var base = _floor_at(point, floor_hint)
			if not base.is_finite() or not _shrine_space_clear(base):
				continue
			# Preserve the main central approach; put small shrines at the sides.
			var center = _bounds.get_center()
			var approach_penalty = 12.0 if absf(point.x - center.x) < 3.5 else 0.0
			var edge_distance = minf(minf(point.x - border.position.x, border.end.x - point.x), minf(point.z - border.position.y, border.end.y - point.z))
			var score = edge_distance + approach_penalty + absf(base.y - floor_hint) * 2.0
			if score < best_score:
				best = base
				best_score = score
	return best

func _material(key: String, color: Color, metallic: float = 0.0) -> StandardMaterial3D:
	if _materials.has(key):
		return _materials[key]
	var material = StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = .72 if metallic == 0 else .34
	material.metallic = metallic
	_materials[key] = material
	return material

func _mesh(parent: Node3D, name: String, mesh: Mesh, position: Vector3, material: Material, scale: Vector3 = Vector3.ONE) -> MeshInstance3D:
	var instance = MeshInstance3D.new()
	instance.name = name
	instance.mesh = mesh
	instance.material_override = material
	instance.position = position
	instance.scale = scale
	parent.add_child(instance)
	return instance

func _box(parent: Node3D, name: String, position: Vector3, size: Vector3, material: Material) -> MeshInstance3D:
	var shape = BoxMesh.new()
	shape.size = size
	var instance = _mesh(parent, name, shape, position, material)
	if name in ["StonePlinth", "BackRecess", "CarvedPier", "Cornice", "Frieze", "UpperCap", "Altar"]:
		var body = StaticBody3D.new()
		body.name = "ShrineCollision"
		var collision = CollisionShape3D.new()
		var box = BoxShape3D.new()
		box.size = size
		collision.shape = box
		body.add_child(collision)
		instance.add_child(body)
	return instance

func _sphere(parent: Node3D, name: String, position: Vector3, size: Vector3, material: Material) -> MeshInstance3D:
	var shape = SphereMesh.new()
	shape.radius = .5
	shape.height = 1.0
	shape.radial_segments = 12
	shape.rings = 8
	return _mesh(parent, name, shape, position, material, size)

func _cylinder(parent: Node3D, name: String, position: Vector3, radius: float, height: float, material: Material, top_radius: float = -1) -> MeshInstance3D:
	var shape = CylinderMesh.new()
	shape.bottom_radius = radius
	shape.top_radius = radius if top_radius < 0 else top_radius
	shape.height = height
	shape.radial_segments = 16
	return _mesh(parent, name, shape, position, material)

func _build_shrine(entry: Dictionary) -> Node3D:
	var shrine = Node3D.new()
	shrine.name = "Shrine_" + str(entry.get("id", "site")).validate_node_name()
	shrine.set_meta("catalog_id", entry.get("id", ""))
	shrine.set_meta("placement_status", "schematic_position")
	shrine.set_meta("artwork_status", "Reference altar — installed image not reconstructed.")
	var stone = _material("stone", Color(.30, .28, .24))
	var dark = _material("basalt", Color(.065, .06, .055))
	var gold = _material("brass", Color(.78, .57, .20), .72)
	var red = _material("cloth", Color(.57, .065, .045))
	var light = _material("pale_stone", Color(.68, .64, .52))
	_box(shrine, "StonePlinth", Vector3(0, .09, 0), Vector3(2.0, .18, 1.9), stone)
	_box(shrine, "BackRecess", Vector3(0, 1.12, -.76), Vector3(2.0, 2.0, .18), stone)
	for side in [-1.0, 1.0]:
		_box(shrine, "CarvedPier", Vector3(side * .86, 1.1, 0), Vector3(.18, 1.9, 1.5), stone)
	_box(shrine, "Cornice", Vector3(0, 2.14, -.02), Vector3(2.22, .20, 2.0), light)
	_box(shrine, "Frieze", Vector3(0, 2.31, -.03), Vector3(1.9, .14, 1.7), stone)
	_box(shrine, "UpperCap", Vector3(0, 2.44, -.03), Vector3(1.6, .12, 1.45), light)
	_cylinder(shrine, "Finial", Vector3(0, 2.60, 0), .085, .22, gold, .03)
	_box(shrine, "Altar", Vector3(0, .33, -.12), Vector3(1.15, .30, 1.0), dark)
	_box(shrine, "AltarCloth", Vector3(0, .49, -.12), Vector3(1.18, .02, 1.03), red)
	var study = preload("res://scripts/shrine_sculpture.gd").new()
	if study.supports(entry):
		shrine.add_child(study.build(entry))
		shrine.set_meta("artwork_status", "Original sacred-form study; installed image not photo-matched.")
		return shrine
	var form = str(entry.get("form", "unknown"))
	if form in ["linga", "linga_nandi", "linga_group", "ganesha", "vishnu", "nandi", "navagraha", "acharya", "cradle", "flame"]:
		shrine.set_meta("artwork_status", "Stylised sacred-form study; installed sculpture and placement not surveyed.")
	match form:
		"linga", "linga_nandi":
			_cylinder(shrine, "YoniPitha", Vector3(0, .58, -.12), .40, .14, dark)
			_box(shrine, "Spout", Vector3(.42, .58, -.12), Vector3(.48, .1, .17), dark)
			_cylinder(shrine, "Linga", Vector3(0, .85, -.12), .19, .48, dark)
			_sphere(shrine, "LingaCrown", Vector3(0, 1.08, -.12), Vector3(.38, .25, .38), dark)
			if form == "linga_nandi":
				_sphere(shrine, "NandiBody", Vector3(0,.63,.52), Vector3(.34,.24,.45), light)
				_sphere(shrine, "NandiHead", Vector3(0,.76,.35), Vector3(.23,.25,.24), light)
		"linga_group":
			for index in range(11):
				var x = float(index % 4 - 1.5) * .24
				var z = float(index / 4 - 1) * .24 - .12
				_cylinder(shrine, "LingaPitha_%d" % index, Vector3(x,.57,z), .10, .10, dark)
				_cylinder(shrine, "Linga_%d" % index, Vector3(x,.70,z), .055, .20, dark)
		"ganesha":
			_sphere(shrine, "SeatedBody", Vector3(0, .83, -.13), Vector3(.62, .63, .45), dark)
			_sphere(shrine, "ElephantHead", Vector3(0, 1.26, -.08), Vector3(.44, .46, .36), dark)
			for side in [-1.0, 1.0]:
				_sphere(shrine, "Ear", Vector3(side * .28, 1.26, -.10), Vector3(.25, .37, .12), dark)
				_sphere(shrine, "Leg", Vector3(side * .28, .63, .06), Vector3(.35, .22, .30), dark)
				_sphere(shrine, "Arm", Vector3(side * .35, .92, .02), Vector3(.16, .43, .18), dark)
			_cylinder(shrine, "Trunk", Vector3(.035, 1.03, .15), .075, .43, dark, .10)
			_sphere(shrine, "TrunkTip", Vector3(.10, .83, .15), Vector3(.21, .14, .14), dark)
			_cylinder(shrine, "Crown", Vector3(0, 1.57, -.08), .18, .23, gold, .06)
		"acharya":
			var robe = _material("saffron", Color(.73, .25, .045))
			_cylinder(shrine, "SeatedRobe", Vector3(0, .77, -.10), .37, .5, robe, .18)
			_sphere(shrine, "Head", Vector3(0, 1.15, -.10), Vector3(.26, .30, .25), dark)
			_box(shrine, "Scripture", Vector3(.2, .68, .20), Vector3(.30, .06, .24), light)
			_cylinder(shrine, "Staff", Vector3(-.43, 1.03, -.10), .025, 1.15, gold)
		"nandi":
			_sphere(shrine, "RecliningBull", Vector3(0, .74, -.10), Vector3(.65, .40, .95), dark)
			_sphere(shrine, "BullHead", Vector3(0, .98, .32), Vector3(.32, .35, .35), dark)
			for side in [-1.0, 1.0]:
				_cylinder(shrine, "Horn", Vector3(side * .14, 1.21, .32), .045, .19, gold, .006)
		"navagraha":
			for index in range(9):
				var pos = Vector3(float(index % 3 - 1) * .3, .74, float(index / 3 - 1) * .3 - .1)
				_cylinder(shrine, "GrahaFigure", pos, .065, .30, dark)
				_sphere(shrine, "GrahaHead", pos + Vector3.UP * .21, Vector3.ONE * .13, dark)
		"cradle":
			for side in [-1.0, 1.0]:
				_cylinder(shrine, "CradlePost", Vector3(side * .46, 1.0, -.1), .045, 1.0, gold)
			_box(shrine, "CradleBeam", Vector3(0, 1.52, -.1), Vector3(1.1, .06, .06), gold)
			_box(shrine, "Cradle", Vector3(0, .83, -.1), Vector3(.66, .15, .40), red)
		"flame":
			var flame = _material("flame", Color(1.0, .44, .055))
			flame.emission_enabled = true
			flame.emission = Color(1.0, .25, .02)
			flame.emission_energy_multiplier = 2.0
			for index in range(3):
				_sphere(shrine, "RockFlame", Vector3((index - 1) * .24, .83, -.1), Vector3(.10, .36, .10), flame)
		"vishnu":
			# Attribute emblem, not an invented exact main-murti sculpture.
			var wheel = TorusMesh.new()
			wheel.inner_radius = .23
			wheel.outer_radius = .30
			wheel.rings = 16
			wheel.ring_segments = 8
			var chakra = _mesh(shrine, "ChakraEmblem", wheel, Vector3(-.24, 1.09, -.1), gold)
			chakra.rotation.x = PI * .5
			_sphere(shrine, "ConchEmblem", Vector3(.25, .96, -.1), Vector3(.25, .47, .26), light)
			_cylinder(shrine, "ConchTip", Vector3(.25, 1.25, -.1), .11, .22, light, .015)
		_:
			# Sacred forms whose exact anatomy is undocumented remain a named
			# reference altar. Never invent a four/eight/ten-armed goddess here.
			_box(shrine, "SacredFormReference", Vector3(0, .90, -.2), Vector3(.62, .78, .12), dark)
			var emblem = _label_3d("REFERENCE ALTAR\nImage not reconstructed", 30, Color(.90, .81, .61))
			emblem.position = Vector3(0, 1.0, -.10)
			emblem.pixel_size = .002
			shrine.add_child(emblem)
	return shrine

func _label_3d(text: String, font_size: int, color: Color) -> Label3D:
	var label = Label3D.new()
	label.text = text
	label.font_size = font_size
	label.modulate = color
	label.outline_size = 7
	label.outline_modulate = Color(.025, .035, .03, .95)
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = false
	label.pixel_size = .003
	return label

func _tradition_context(entry: Dictionary) -> String:
	if entry.has("tradition"):
		return str(entry["tradition"])
	var form := str(entry.get("form", "unknown"))
	var role := "Main sanctuary" if entry.get("kind", "") == "main" else "In-complex shrine"
	if entry.get("kind", "") == "heritage":
		return "Historic site / tradition reference\nSee the documented monument identity and source notes."
	var context: Dictionary = {
		"devi": "Shakta tradition • Goddess worship",
		"linga": "Shaiva tradition • Shiva linga",
		"linga_nandi": "Shaiva tradition • Shiva linga and Nandi",
		"linga_group": "Shaiva tradition • Group of Shiva lingas",
		"shiva": "Shaiva tradition • Shiva image",
		"vishnu": "Vaishnava tradition • Vishnu worship",
		"radha_krishna": "Vaishnava tradition • Radha and Krishna worship",
		"ganesha": "Ganesha / Ganapati worship",
		"nandi": "Nandi • Shiva's sacred bull",
		"navagraha": "Navagraha • Nine planetary deities",
		"acharya": "Acharya tradition • Teacher shrine",
		"cradle": "Sacred cradle • Non-figurative worship",
		"flame": "Sacred flame • Non-figurative worship",
		"sacred_symbol": "Sacred form • See the sourced tradition notes",
		"unknown": "Reference site • Original image unverified"
	}
	return role + "\n" + str(context.get(form, "See the sourced shrine tradition notes"))

func _add_destination_label(entry: Dictionary, destination: Dictionary) -> void:
	# One consistent label for imported sculptures, added shrines and reference
	# sites. Stage it toward the safe approach so walls do not hide the name.
	var group := Node3D.new()
	group.name = "ShrineIdentity_" + str(destination["id"]).validate_node_name()
	group.set_meta("catalog_id", destination["id"])
	group.set_meta("tradition", _tradition_context(entry))
	add_child(group)
	var target: Vector3 = destination["target"]
	var landing: Vector3 = destination["position"]
	var approach := target.lerp(landing, .15) if destination["available"] else target
	approach.y = maxf(target.y + .80, landing.y + 1.70)
	group.global_position = approach
	var title := _label_3d(str(destination["label"]), 28, Color(1.0, .9, .64))
	title.name = "ShrineLabel"
	title.fixed_size = true
	title.pixel_size = .002
	title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title.width = 560
	title.outline_size = 10
	title.visibility_range_end = 18.0
	group.add_child(title)
	var context := _label_3d(_tradition_context(entry), 24, Color(.96, .94, .86))
	context.name = "ShrineTradition"
	context.fixed_size = true
	context.position.y = -.30
	context.visibility_range_end = 9.0
	context.outline_size = 8
	group.add_child(context)
	_identity_labels.append({"group": group, "context": context, "target": target})

func _add_nameplate(parent: Node3D, text: String, position: Vector3) -> void:
	var label = _label_3d(text, 36, Color(.91, .79, .55))
	label.name = "ShrineLabel"
	label.position = position
	parent.add_child(label)
