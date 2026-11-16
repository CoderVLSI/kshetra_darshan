extends Node3D

## Cheap animated bird flock and a daylight sky with soft cloud layers.
## This is environmental art, not a claim about a site's local bird species.
var sky_material: ShaderMaterial
var birds: MultiMeshInstance3D
var clock: float = 0.0
var cloud_tick: float = 0.0
var orbit_center := Vector3.ZERO
var orbit_radius: float = 36.0
var bird_height: float = 22.0

func setup(model: Node3D, environment: Environment) -> void:
	var bounds = _bounds(model)
	orbit_center = bounds.get_center()
	orbit_center.y = 0
	orbit_radius = clampf(maxf(bounds.size.x, bounds.size.z) * 0.65, 30, 65)
	bird_height = maxf(bounds.end.y + 7.0, 20.0)
	sky_material = ShaderMaterial.new()
	sky_material.shader = load("res://shaders/temple_sky.gdshader")
	sky_material.set_shader_parameter("cloud_texture", load("res://assets/textures/atmosphere/cloud_noise.png"))
	var sky = Sky.new()
	sky.sky_material = sky_material
	sky.radiance_size = Sky.RADIANCE_SIZE_128
	sky.process_mode = Sky.PROCESS_MODE_INCREMENTAL
	environment.sky = sky
	_build_birds()

func _bounds(node: Node) -> AABB:
	var box := AABB()
	if node is MeshInstance3D:
		box = node.global_transform * node.get_aabb()
	for child in node.get_children():
		var child_box = _bounds(child)
		if child_box.size != Vector3.ZERO:
			box = child_box if box.size == Vector3.ZERO else box.merge(child_box)
	return box

func _build_birds() -> void:
	var mesh = ArrayMesh.new()
	var vertices = PackedVector3Array([
		Vector3(0,0,-.27), Vector3(-.05,.025,.1), Vector3(.05,.025,.1),
		Vector3(-.035,0,-.08), Vector3(-.54,.01,.12), Vector3(-.22,.015,.17),
		Vector3(.035,0,-.08), Vector3(.22,.015,.17), Vector3(.54,.01,.12),
		Vector3(0,0,.08), Vector3(-.10,0,.3), Vector3(.10,0,.3)])
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var material = ShaderMaterial.new()
	material.shader = load("res://shaders/bird_flight.gdshader")
	mesh.surface_set_material(0, material)
	var multi = MultiMesh.new()
	multi.transform_format = MultiMesh.TRANSFORM_3D
	multi.use_custom_data = true
	multi.mesh = mesh
	multi.instance_count = 22
	for index in range(multi.instance_count):
		multi.set_instance_custom_data(index, Color(float(index) / multi.instance_count, 0, 0, 1))
	birds = MultiMeshInstance3D.new()
	birds.name = "FlyingBirds"
	birds.multimesh = multi
	birds.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(birds)
	_update_birds()

func set_preset(preset: Dictionary, index: int) -> void:
	if not sky_material:
		return
	var day = 0.0 if index == 5 else (0.55 if index == 1 or index == 4 else 1.0)
	sky_material.set_shader_parameter("zenith_color", preset["sky_top"])
	sky_material.set_shader_parameter("horizon_color", preset["sky_horizon"])
	sky_material.set_shader_parameter("ground_color", preset["ground_bottom"])
	sky_material.set_shader_parameter("daylight", day)
	sky_material.set_shader_parameter("cloud_light", Color(.10,.13,.20).lerp(preset["sun_color"], day))
	sky_material.set_shader_parameter("cloud_shadow", Color(.04,.06,.10).lerp(Color(.46,.54,.65), day))
	if birds:
		birds.visible = index != 5

func _process(delta: float) -> void:
	clock += delta
	cloud_tick += delta
	# Update slowly to avoid rebuilding sky reflections on every rendered frame.
	if cloud_tick > 0.5 and sky_material:
		cloud_tick = 0.0
		sky_material.set_shader_parameter("cloud_phase", clock * .007)
	_update_birds()

func _update_birds() -> void:
	if not birds:
		return
	for index in range(birds.multimesh.instance_count):
		var angle = clock * .075 + float(index % 11) * .032 + float(index / 11) * PI
		var radius = orbit_radius + float(index % 4) * 1.6
		var point = orbit_center + Vector3(cos(angle)*radius, bird_height + float(index % 5)*.65 + sin(clock*.8+index)*.3, sin(angle)*radius)
		var forward = Vector3(-sin(angle), 0.02*cos(clock+index), cos(angle)).normalized()
		var transform = Transform3D(Basis.looking_at(forward), point)
		birds.multimesh.set_instance_transform(index, transform)
