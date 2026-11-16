class_name ShrineSculpture
extends RefCounted

## Original iconographic studies, not scans of the installed temple murtis.
## Museum references and limitations: data/sculpture_evidence.json.
var stone: StandardMaterial3D
var gold: StandardMaterial3D
var cloth: StandardMaterial3D
var white: StandardMaterial3D

func supports(entry: Dictionary) -> bool:
	return study_type(entry) != ""

func study_type(entry: Dictionary) -> String:
	var id = str(entry.get("id", ""))
	if id == "main": return ""
	if id == "nabhigaya": return "sacred_well"
	if id == "devi_footprints": return "footprints"
	if id == "sosthi_tala": return "three_stones"
	if id in ["annapurna", "annapoorani"] and entry.get("form", "") != "flame": return "annapurna"
	if id == "surya": return "surya"
	if str(entry.get("form", "")) == "ganesha": return "ganesha"
	if str(entry.get("form", "")) == "vishnu": return "vishnu"
	if id in ["saraswati", "mahasaraswati"]: return "saraswati"
	if id == "varahi": return "varahi"
	if id == "murugan": return "murugan"
	return ""

func build(entry: Dictionary) -> Node3D:
	stone = material(Color(.12,.125,.13),.08,.48)
	gold = material(Color(.72,.47,.13),.8,.3)
	cloth = material(Color(.54,.10,.065),.0,.75)
	white = material(Color(.75,.72,.60),.1,.45)
	var root = Node3D.new()
	root.name = "IconographicStudy"
	root.set_meta("artwork_status", "Original iconographic study; installed temple image not photo-matched")
	root.set_meta("evidence_manifest", "res://data/sculpture_evidence.json")
	var kind = study_type(entry)
	if kind in ["sacred_well", "footprints", "three_stones"]:
		_build_nonfigurative(root, kind)
		return root
	var seated = kind in ["ganesha", "saraswati", "varahi", "annapurna"]
	var body_y = .92 if seated else 1.10
	var head_y = 1.34 if seated else 1.58
	# Lotus pedestal and layered petals create a readable silhouette.
	cylinder(root,"LotusSeat",Vector3(0,.54,-.1),.38,.10,gold)
	for i in range(16):
		var angle = TAU * float(i)/16
		var petal = sphere(root,"LotusPetal",Vector3(sin(angle)*.32,.57,cos(angle)*.22-.1),Vector3(.12,.07,.18),gold)
		petal.rotation.y = angle
	sphere(root,"Torso",Vector3(0,body_y,-.13),Vector3(.36,.50,.24),stone)
	cylinder(root,"WaistCloth",Vector3(0,body_y-.17,-.13),.22,.27,cloth,.14)
	if seated:
		for side in [-1.0,1.0]:
			sphere(root,"FoldedLeg",Vector3(side*.20,.68,.02),Vector3(.43,.18,.29),stone)
	else:
		for side in [-1.0,1.0]:
			limb(root,"Leg",Vector3(side*.105,.93,-.13),Vector3(side*.10,.65,-.12),.075,stone)
			sphere(root,"Foot",Vector3(side*.10,.61,-.015),Vector3(.14,.09,.25),stone)
	if kind == "ganesha":
		sphere(root,"ElephantHead",Vector3(0,head_y,-.09),Vector3(.38,.36,.30),stone)
		for side in [-1.0,1.0]:
			sphere(root,"ElephantEar",Vector3(side*.25,head_y,-.10),Vector3(.27,.37,.10),stone)
			sphere(root,"Tusk",Vector3(side*.12,head_y-.12,.10),Vector3(.035,.13,.06),white)
		var trunk = [Vector3(0,1.32,.08),Vector3(0,1.18,.16),Vector3(.02,1.05,.20),Vector3(.13,1.01,.20),Vector3(.17,1.06,.19)]
		for i in range(trunk.size()-1): limb(root,"CurvedTrunk",trunk[i],trunk[i+1],.065-float(i)*.009,stone)
	else:
		sphere(root,"Head",Vector3(0,head_y,-.1),Vector3(.24,.30,.24),stone)
		if kind == "varahi":
			sphere(root,"BoarMuzzle",Vector3(0,head_y-.035,.07),Vector3(.19,.14,.25),stone)
			for side in [-1.0,1.0]:
				sphere(root,"BoarEar",Vector3(side*.12,head_y+.10,-.1),Vector3(.10,.14,.07),stone)
				sphere(root,"BoarTusk",Vector3(side*.10,head_y-.06,.14),Vector3(.028,.10,.045),white)
		else:
			sphere(root,"Nose",Vector3(0,head_y-.01,.025),Vector3(.045,.075,.055),stone)
			for side in [-1.0,1.0]:
				sphere(root,"Ear",Vector3(side*.13,head_y-.01,-.09),Vector3(.065,.12,.055),stone)
				sphere(root,"Eye",Vector3(side*.055,head_y+.025,.017),Vector3(.048,.015,.012),gold)
			sphere(root,"Lips",Vector3(0,head_y-.075,.02),Vector3(.07,.016,.025),stone)
	# Crown rings, earrings, necklaces and armlets remain original authored detail.
	cylinder(root,"Crown",Vector3(0,head_y+.20,-.1),.14,.20,gold,.06)
	for ring in range(3): torus(root,"CrownBand",Vector3(0,head_y+.13+ring*.055,-.1),.12-ring*.022,.012,gold,false)
	for side in [-1.0,1.0]:
		torus(root,"Earring",Vector3(side*.15,head_y-.08,-.08),.035,.009,gold,true)
	for i in range(13):
		var angle = PI*float(i)/12
		sphere(root,"NecklaceBead",Vector3(cos(angle)*.15,body_y+.14-sin(angle)*.12,.015),Vector3.ONE*.023,gold)
	var arm_y = body_y+.13
	for side in [-1.0,1.0]:
		var shoulder = Vector3(side*.18,arm_y,-.12)
		var elbow = Vector3(side*.31,arm_y-.18,-.05)
		var hand = Vector3(side*.25,arm_y-.25,.10)
		if kind == "saraswati": hand = Vector3(side*.26,arm_y-.09,.19)
		if kind == "surya":
			elbow = Vector3(side*.31,arm_y-.10,-.04)
			hand = Vector3(side*.35,arm_y+.08,.08)
		arm(root,shoulder,elbow,hand)
	if kind in ["vishnu", "ganesha", "saraswati"]:
		for side in [-1.0,1.0]: arm(root,Vector3(side*.16,arm_y,-.17),Vector3(side*.34,arm_y+.10,-.18),Vector3(side*.40,arm_y+.27,-.08))
	if kind == "vishnu":
		# Deity's right is viewer's left for a sculpture facing +Z.
		torus(root,"Chakra",Vector3(-.40,arm_y+.40,-.07),.115,.017,gold,true)
		for i in range(8):
			var a = TAU*i/8.0
			limb(root,"ChakraSpoke",Vector3(-.40,arm_y+.40,-.07),Vector3(-.40+sin(a)*.10,arm_y+.40+cos(a)*.10,-.07),.008,gold)
		sphere(root,"Conch",Vector3(.40,arm_y+.39,-.06),Vector3(.14,.21,.12),white)
		cylinder(root,"ConchTip",Vector3(.40,arm_y+.52,-.06),.035,.11,white,.005)
	if kind == "saraswati":
		limb(root,"VinaNeck",Vector3(-.39,.93,.19),Vector3(.40,1.16,.19),.035,gold)
		sphere(root,"VinaResonator",Vector3(-.28,.95,.19),Vector3(.23,.21,.18),gold)
		for i in range(4): limb(root,"VinaString",Vector3(-.35,.96+i*.009,.224),Vector3(.39,1.18+i*.009,.224),.002,white)
		var book = BoxMesh.new()
		book.size = Vector3(.17,.045,.10)
		mesh(root,"PalmLeafManuscript",book,Vector3(.40,arm_y+.28,-.08),white)
		for i in range(12):
			var a = TAU*float(i)/12
			sphere(root,"RosaryBead",Vector3(-.40+cos(a)*.045,arm_y+.21+sin(a)*.065,-.06),Vector3.ONE*.016,gold)
	if kind == "murugan":
		limb(root,"VelShaft",Vector3(-.37,.60,.02),Vector3(-.37,1.85,.02),.014,gold)
		sphere(root,"VelLeaf",Vector3(-.37,1.83,.02),Vector3(.11,.23,.035),gold)
	if kind == "annapurna":
		# General bowl-and-ladle iconography; not a claimed installed-image scan.
		torus(root,"RiceBowlRim",Vector3(.25,arm_y-.23,.12),.10,.015,gold,false)
		sphere(root,"RiceVessel",Vector3(.25,arm_y-.27,.12),Vector3(.21,.11,.18),gold)
		for grain in range(9):
			var angle = TAU*grain/9.0
			sphere(root,"RiceOffering",Vector3(.25+cos(angle)*.055,arm_y-.22,.12+sin(angle)*.045),Vector3(.025,.014,.017),white)
		limb(root,"LadleHandle",Vector3(-.25,arm_y-.25,.10),Vector3(.02,arm_y-.12,.18),.009,gold)
		sphere(root,"LadleBowl",Vector3(.035,arm_y-.12,.18),Vector3(.09,.025,.07),gold)
	if kind == "surya":
		torus(root,"SolarHalo",Vector3(0,head_y-.06,-.28),.30,.018,gold,true)
		for side in [-1.0,1.0]:
			var flower = Vector3(side*.35,arm_y+.34,.08)
			limb(root,"LotusStem",Vector3(side*.35,arm_y+.08,.08),flower,.009,gold)
			for petal in range(8):
				var angle = TAU*petal/8.0
				sphere(root,"FullBloomLotus",flower+Vector3(cos(angle)*.055,sin(angle)*.055,0),Vector3(.065,.065,.025),gold)
	# Fine skirt pleats, clearly sculpted rather than text on an empty slab.
	for i in range(9):
		var x = (float(i)-4)*.037
		limb(root,"GarmentPleat",Vector3(x,body_y-.08,.105),Vector3(x*1.35,.66,.10),.006,gold)
	return root

func _build_nonfigurative(root: Node3D, kind: String) -> void:
	# Sources establish these sacred forms, not exact surveyed dimensions.
	# A well, footprints and three worshipped stones are not missing idols.
	if kind == "sacred_well":
		for ring in range(3):
			for block in range(16):
				var angle = TAU * (block + .5 * (ring % 2)) / 16.0
				var shape = BoxMesh.new()
				shape.size = Vector3(.17, .13, .12)
				var node = mesh(root, "WellMasonry", shape, Vector3(sin(angle)*.42,.58+ring*.13,cos(angle)*.42-.1), stone)
				node.rotation.y = angle
		var darkness = material(Color(.015,.022,.025), 0, .95)
		cylinder(root, "RecessedWellOpening", Vector3(0,.56,-.1), .35,.015,darkness)
	elif kind == "footprints":
		var base = BoxMesh.new()
		base.size = Vector3(.62,.05,.65)
		mesh(root, "FootprintStone",base,Vector3(0,.56,-.1),stone)
		for side in [-1.0,1.0]:
			sphere(root,"SacredSoleStudy",Vector3(side*.13,.595,-.1),Vector3(.12,.025,.27),gold)
			for toe in range(5):
				sphere(root,"ToeStudy",Vector3(side*.13+(toe-2)*.025,.595,.045-absf(toe-1)*.012),Vector3(.027,.023,.036),gold)
	else:
		for index in range(3):
			sphere(root,"WorshippedStone",Vector3((index-1)*.28,.68,-.1),Vector3(.22,.25,.20),stone)
			for flower in range(5):
				var angle = TAU*flower/5.0
				sphere(root,"OfferingFlower",Vector3((index-1)*.28+cos(angle)*.04,.57,.11+sin(angle)*.04),Vector3.ONE*.045,gold)

func material(color: Color, metallic: float, roughness: float) -> StandardMaterial3D:
	var mat = StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = metallic
	mat.roughness = roughness
	return mat

func mesh(parent: Node3D, title: String, shape: Mesh, pos: Vector3, mat: Material) -> MeshInstance3D:
	var node = MeshInstance3D.new()
	node.name = title
	node.mesh = shape
	node.position = pos
	node.material_override = mat
	parent.add_child(node)
	return node

func sphere(parent: Node3D, title: String, pos: Vector3, size: Vector3, mat: Material) -> MeshInstance3D:
	var shape = SphereMesh.new()
	shape.radius = .5
	shape.height = 1
	shape.radial_segments = 20
	shape.rings = 12
	var node = mesh(parent,title,shape,pos,mat)
	node.scale = size
	return node

func cylinder(parent: Node3D, title: String, pos: Vector3, radius: float, height: float, mat: Material, top: float = -1) -> MeshInstance3D:
	var shape = CylinderMesh.new()
	shape.bottom_radius = radius
	shape.top_radius = radius if top < 0 else top
	shape.height = height
	shape.radial_segments = 24
	return mesh(parent,title,shape,pos,mat)

func limb(parent: Node3D, title: String, a: Vector3, b: Vector3, radius: float, mat: Material) -> void:
	var node = cylinder(parent,title,(a+b)*.5,radius,a.distance_to(b),mat)
	node.quaternion = Quaternion(Vector3.UP,(b-a).normalized())
	sphere(parent,title+"Joint",b,Vector3.ONE*radius*2,mat)

func arm(parent: Node3D, a: Vector3, b: Vector3, c: Vector3) -> void:
	limb(parent,"UpperArm",a,b,.043,stone)
	limb(parent,"Forearm",b,c,.032,stone)
	sphere(parent,"Palm",c,Vector3(.065,.09,.045),stone)
	for finger in range(4): limb(parent,"Finger",c+Vector3((finger-1.5)*.013,-.025,.01),c+Vector3((finger-1.5)*.013,-.066,.015),.005,stone)

func torus(parent: Node3D, title: String, pos: Vector3, radius: float, thickness: float, mat: Material, vertical: bool) -> void:
	var shape = TorusMesh.new()
	shape.inner_radius = radius-thickness
	shape.outer_radius = radius+thickness
	shape.rings = 24
	shape.ring_segments = 8
	var node = mesh(parent,title,shape,pos,mat)
	if vertical: node.rotation.x = PI*.5
