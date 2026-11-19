extends Node

## GameManager (Autoload)
## Manages global game state, current temple selection, audio settings,
## mobile mode toggles, and seva action events.

signal temple_changed(temple_id: String)
signal sound_toggled(enabled: bool)
signal mobile_mode_toggled(enabled: bool)
signal seva_action_performed(action_name: String, title: String, message: String)

var current_temple_id: String = "kamakhya"
var sound_enabled: bool = true
var mobile_mode: bool = false
var reference_notes: Dictionary = {}

# Traditional eighteen plus three additional pilgrimage destinations.
var temples: Dictionary = {
	"draksharama_manikyamba": {
		"id": "draksharama_manikyamba", "name": "Draksharama Manikyamba and Bhimeswara",
		"short_name": "Draksharama Manikyamba", "location": "Draksharamam, Andhra Pradesh",
		"devi": "Mata Manikyamba", "anga": "Shakti Peetha tradition",
		"bhairava": "Bhimeswara", "style": "Eastern Chalukyan double enclosure and upper sanctum",
		"color": Color(0.72, 0.65, 0.42)
	},
	"jwalamukhi_vaishnavi": {
		"id": "jwalamukhi_vaishnavi", "name": "Jwalamukhi Devi Temple",
		"short_name": "Jwalamukhi", "location": "Kangra, Himachal Pradesh",
		"devi": "Mata Jwalamukhi / Vaishnavi", "anga": "Tongue (traditional association)",
		"bhairava": "Traditions vary", "style": "Gilded domes and natural flame sanctum",
		"color": Color(0.95, 0.66, 0.19)
	},
	"kashmir_sharada": {
		"id": "kashmir_sharada", "name": "Sharada Peeth — Surviving Ruins",
		"short_name": "Kashmir Sharada", "location": "Neelum Valley, Pakistan-administered Kashmir",
		"devi": "Mata Sharada / Saraswati", "anga": "Shakti Peetha tradition",
		"bhairava": "Not established here", "style": "Roofless Kashmiri stone sanctuary and enclosure",
		"color": Color(0.56, 0.65, 0.48)
	},
	"kamakhya": {
		"id": "kamakhya",
		"name": "Kamakhya Devi Temple",
		"short_name": "Kamakhya",
		"location": "Guwahati, Assam",
		"devi": "Mata Kamakhya",
		"anga": "Yoni Peetha",
		"bhairava": "Umananda",
		"style": "Nilachala (Beehive Dome)",
		"color": Color(0.92, 0.25, 0.20)
	},
	"kalighat": {
		"id": "kalighat",
		"name": "Kalighat Kali Temple",
		"short_name": "Kalighat",
		"location": "Kolkata, West Bengal",
		"devi": "Mata Kalika (Dakshina Kali)",
		"anga": "Right Toes",
		"bhairava": "Nakuleshwar",
		"style": "Bengali Aatchala Curved Roof",
		"color": Color(0.85, 0.15, 0.35)
	},
	"kashi_vishalakshi": {
		"id": "kashi_vishalakshi",
		"name": "Vishalakshi Temple",
		"short_name": "Vishalakshi",
		"location": "Varanasi, Uttar Pradesh",
		"devi": "Mata Vishalakshi",
		"anga": "Earrings / Eyes",
		"bhairava": "Kala Bhairava",
		"style": "Nagara & Ganga Ghat Mandir",
		"color": Color(0.95, 0.65, 0.15)
	},
	"kanchipuram_kamakshi": {
		"id": "kanchipuram_kamakshi",
		"name": "Kanchi Kamakshi Amman Temple",
		"short_name": "Kanchi Kamakshi",
		"location": "Kanchipuram, Tamil Nadu",
		"devi": "Mata Kamakshi",
		"anga": "Navel (Nabhi)",
		"bhairava": "Bhairava",
		"style": "Dravidian Gopuram & Gayatri Mandapam",
		"color": Color(0.98, 0.72, 0.10)
	},
	"madurai_meenakshi": {
		"id": "madurai_meenakshi",
		"name": "Meenakshi Sundareswarar Temple",
		"short_name": "Madurai Meenakshi",
		"location": "Madurai, Tamil Nadu",
		"devi": "Mata Meenakshi",
		"anga": "Eyes (Nayanam)",
		"bhairava": "Sundareswarar",
		"style": "Grand Dravidian Multi-tier Gopuram",
		"color": Color(0.20, 0.75, 0.55)
	},
	"mysore_chamundeshwari": {
		"id": "mysore_chamundeshwari",
		"name": "Chamundeshwari Temple",
		"short_name": "Chamundeshwari",
		"location": "Chamundi Hills, Mysuru, Karnataka",
		"devi": "Mata Chamundeshwari",
		"anga": "Hair (Kesha)",
		"bhairava": "Kruradrishti",
		"style": "Dravidian Hoysala / Vijayanagara",
		"color": Color(0.90, 0.40, 0.15)
	},
	"kolhapur_mahalakshmi": {
		"id": "kolhapur_mahalakshmi",
		"name": "Mahalakshmi Temple (Ambabai)",
		"short_name": "Kolhapur Mahalakshmi",
		"location": "Kolhapur, Maharashtra",
		"devi": "Mata Mahalakshmi",
		"anga": "Radiant Eyes",
		"bhairava": "Krodhashish",
		"style": "Hemadpanthi Chalukyan Basalt",
		"color": Color(0.95, 0.80, 0.20)
	},
	"tuljapur_bhavani": {
		"id": "tuljapur_bhavani",
		"name": "Tulja Bhavani Temple",
		"short_name": "Tulja Bhavani",
		"location": "Tuljapur, Maharashtra",
		"devi": "Mata Bhavani",
		"anga": "Left Cheek",
		"bhairava": "Bhairava",
		"style": "Hemadpanthi Deepastambha & Prakara",
		"color": Color(0.92, 0.35, 0.15)
	},
	"mahur_renuka": {
		"id": "mahur_renuka",
		"name": "Renuka Devi Temple",
		"short_name": "Mahur Renuka",
		"location": "Mahur, Maharashtra",
		"devi": "Mata Renuka",
		"anga": "Upper Lip",
		"bhairava": "Bhairava",
		"style": "Hilltop Hemadpanthi Fortified Mandir",
		"color": Color(0.88, 0.45, 0.25)
	},
	"alampur_jogulamba": {
		"id": "alampur_jogulamba",
		"name": "Jogulamba Temple",
		"short_name": "Jogulamba",
		"location": "Alampur, Telangana",
		"devi": "Mata Jogulamba",
		"anga": "Upper Teeth",
		"bhairava": "Bala Brahmeshwara",
		"style": "Badami Chalukya Rekhanagara",
		"color": Color(0.80, 0.55, 0.25)
	},
	"srisailam_bhramaramba": {
		"id": "srisailam_bhramaramba",
		"name": "Bhramaramba Devi Temple",
		"short_name": "Srisailam Bhramaramba",
		"location": "Srisailam, Andhra Pradesh",
		"devi": "Mata Bhramaramba",
		"anga": "Neck (Griva)",
		"bhairava": "Mallikarjuna (Jyotirlinga)",
		"style": "Vijayanagara Dravidian Mukhamandapa",
		"color": Color(0.85, 0.60, 0.15)
	},
	"pithapuram_puruhutika": {
		"id": "pithapuram_puruhutika",
		"name": "Puruhutika Devi Temple",
		"short_name": "Puruhutika",
		"location": "Pithapuram, Andhra Pradesh",
		"devi": "Mata Puruhutika",
		"anga": "Left Hand / Hip",
		"bhairava": "Kukkuteswara",
		"style": "Eastern Chalukyan & Pada Gaya Kunda",
		"color": Color(0.90, 0.70, 0.30)
	},
	"jajpur_biraja": {
		"id": "jajpur_biraja",
		"name": "Biraja Devi Temple",
		"short_name": "Jajpur Biraja",
		"location": "Jajpur, Odisha",
		"devi": "Mata Biraja",
		"anga": "Navel (Nabhi Gaya)",
		"bhairava": "Vaitaraneeshwar",
		"style": "Kalinga Deula (Rekha Deula)",
		"color": Color(0.88, 0.30, 0.25)
	},
	"ujjain_mahakali": {
		"id": "ujjain_mahakali",
		"name": "Harsiddhi / Mahakali Temple",
		"short_name": "Ujjain Mahakali",
		"location": "Ujjain, Madhya Pradesh",
		"devi": "Mata Mahakali",
		"anga": "Elbow",
		"bhairava": "Mahakaleshwar",
		"style": "Malwa Paramara & Giant Deepastambhas",
		"color": Color(0.85, 0.20, 0.20)
	},
	"prayag_madhaveswari": {
		"id": "prayag_madhaveswari",
		"name": "Alopi Devi Temple (Prayagraj tradition)",
		"short_name": "Alopi Shankari",
		"location": "Prayagraj, Uttar Pradesh",
		"devi": "Alopi Shankari",
		"anga": "Fingers (Hastanguli)",
		"bhairava": "Bhairava",
		"style": "Alopibagh Nagara sanctuary and sacred cradle",
		"color": Color(0.95, 0.75, 0.20)
	},
	"gaya_mangalagauri": {
		"id": "gaya_mangalagauri",
		"name": "Mangala Gauri Temple",
		"short_name": "Gaya Mangalagauri",
		"location": "Gaya, Bihar",
		"devi": "Mata Mangalagauri",
		"anga": "Breasts (Stana)",
		"bhairava": "Vishweshwar",
		"style": "Nagara Bhasmakuta Hilltop Sanctum",
		"color": Color(0.90, 0.50, 0.20)
	},
	"pradyumna_shrinkhala": {
		"id": "pradyumna_shrinkhala",
		"name": "Pandua — Shrinkhala Traditional Association",
		"short_name": "Shrinkhala Devi",
		"location": "Pandua (Pradyumna), West Bengal",
		"devi": "Mata Shrinkhala",
		"anga": "Traditional association; exact shrine unresolved",
		"bhairava": "Not established here",
		"style": "Pandua Minar and roofless Bari Masjid remains",
		"color": Color(0.80, 0.35, 0.30)
	},
	"lanka_shankari": {
		"id": "lanka_shankari",
		"name": "Shankari tradition at Koneswaram",
		"short_name": "Lanka Shankari",
		"location": "Trincomalee, Sri Lanka",
		"devi": "Mata Shankari",
		"anga": "Groin / Heart / Anklet",
		"bhairava": "Trikoneshwara",
		"style": "Present-day temple on Swami Rock",
		"color": Color(0.25, 0.65, 0.85)
	}
}

func _ready() -> void:
	var reference_file = FileAccess.open("res://data/reference_notes.json", FileAccess.READ)
	if reference_file:
		var parsed = JSON.parse_string(reference_file.get_as_text())
		if parsed is Dictionary:
			reference_notes = parsed
	# Site-specific corrections. Inclusion in the traditional list does not
	# certify the model as a measured replica or settle disputed site identities.
	temples["gaya_mangalagauri"]["style"] = "Small Nagara shrine on Mangala Gauri Hill"
	temples["kashi_vishalakshi"]["style"] = "Compact urban shrine with Dravidian entrance"
	temples["pradyumna_shrinkhala"]["style"] = "Present-day monument study; ancient shrine unresolved"
	temples["ujjain_mahakali"]["devi"] = "Mata Harsiddhi / Annapurna"
	# Autodetect mobile platform
	if OS.has_feature("mobile") or OS.has_feature("android") or OS.has_feature("ios") or OS.has_feature("web_android") or OS.has_feature("web_ios"):
		mobile_mode = true

func load_temple(temple_id: String) -> void:
	if temples.has(temple_id):
		current_temple_id = temple_id
		# The new world's _ready loads once. Emitting to the outgoing world
		# used to construct the same mesh/collisions twice before scene disposal.
		get_tree().change_scene_to_file("res://scenes/temple_world.tscn")
	else:
		push_error("GameManager: Unknown temple ID '%s'" % temple_id)

func go_to_menu() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")

func toggle_sound() -> void:
	sound_enabled = not sound_enabled
	AudioServer.set_bus_mute(AudioServer.get_bus_index("Master"), not sound_enabled)
	sound_toggled.emit(sound_enabled)

func set_mobile_mode(enabled: bool) -> void:
	mobile_mode = enabled
	mobile_mode_toggled.emit(mobile_mode)

func get_current_temple() -> Dictionary:
	return temples.get(current_temple_id, temples["kamakhya"])

func trigger_seva(action_key: String) -> void:
	var t = get_current_temple()
	var devi_name = t.get("devi", "Devi")
	
	match action_key:
		"prayer":
			seva_action_performed.emit("prayer", "🙏 Namaskaram", "Offering heartfelt devotional prayers at the sacred lotus feet of %s." % devi_name)
		"pranam":
			seva_action_performed.emit("pranam", "🙇 Sashtanga Pranam", "Prostrating in supreme surrender and humility before %s." % devi_name)
		"flower_offering":
			seva_action_performed.emit("flower_offering", "🌸 Pushpanjali", "Offering fragrant red hibiscus, bilva patra, and fresh jasmine to %s." % devi_name)
		"ring_bell":
			seva_action_performed.emit("ring_bell", "🔔 Ghanta Naada", "Ringing the sacred brass temple bell to awaken positive cosmic vibrations.")
		"aarti":
			seva_action_performed.emit("aarti", "🪔 Mangala Aarti", "Performing sacred Pancha-Pradipa and camphor flame aarti to %s." % devi_name)
		"prasadam":
			seva_action_performed.emit("prasadam", "🥥 Prasada Seva", "Receiving the blessed, sanctified charanamrita and sweet prasadam.")
		"conch":
			seva_action_performed.emit("conch", "🐚 Shankha Naada", "Blowing the resonant auspicious conch shell across the sanctum.")
		"mantra":
			seva_action_performed.emit("mantra", "🕉️ Mantra Japa", "Chanting the sacred Ashtadasha Maha Shakti Peetha stotram.")
		_:
			seva_action_performed.emit(action_key, "Seva", "Performing sacred seva at %s." % t.get("name", "Temple"))
