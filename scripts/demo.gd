extends Node3D

const MIRA_SCENE: PackedScene = preload("res://assets/Mira.glb")
const MAKO_SCENE: PackedScene = preload("res://assets/Mako-Quaternius-CC0.glb")
const MELEE: AnimationLibrary = preload("res://assets/MeleeLib.res")
const SHOOTER: AnimationLibrary = preload("res://assets/ShooterLib.res")

var hero: Node3D
var animator: AnimationPlayer
var camera: Camera3D
var orbit_angle := 0.0
var orbit_distance := 8.0
var drag_active := false
var selected_animation := "Melee/LightIdle"
var title_label: Label

func _ready() -> void:
	_build_world()
	_build_characters()
	_build_ui()
	_play("Melee/LightIdle")

func _build_world() -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color("10bcd0")
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color("dce9f4")
	e.ambient_light_energy = 0.38
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	add_child(env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, -30, 0)
	sun.light_energy = 0.85
	sun.shadow_enabled = true
	add_child(sun)

	_box("Floating grass platform", Vector3(0, -.30, 0), Vector3(9.5, .45, 7.2), Color("55b65c"))
	_box("Soil rim", Vector3(0, -.57, 0), Vector3(9.3, .13, 7.0), Color("d99d61"))
	for p in [Vector3(-3.3, 0, -1.8), Vector3(3.5, 0, -2.1), Vector3(-2.5, 0, 1.6)]:
		_tree(p)
	for p in [Vector3(-3.85, .29, .2), Vector3(3.9, .29, .7), Vector3(.1, .29, -2.4)]:
		_box("Coral block", p, Vector3(.53, .58, .53), Color("e6774c"))

	camera = Camera3D.new()
	camera.current = true
	camera.fov = 46
	add_child(camera)
	_update_camera()

func _box(node_name: String, where: Vector3, size: Vector3, color: Color) -> void:
	var body := MeshInstance3D.new()
	body.name = node_name
	var mesh := BoxMesh.new()
	mesh.size = size
	body.mesh = mesh
	body.position = where
	body.material_override = _material(color)
	add_child(body)

func _tree(p: Vector3) -> void:
	_box("Tree trunk", p + Vector3(0, .52, 0), Vector3(.28, 1.05, .28), Color("9d6b45"))
	for level in range(3):
		var crown := MeshInstance3D.new()
		crown.name = "Pine foliage"
		var cone := CylinderMesh.new()
		cone.top_radius = 0.0
		cone.bottom_radius = .72 - level * .13
		cone.height = 1.12
		cone.radial_segments = 5
		crown.mesh = cone
		crown.position = p + Vector3(0, 1.05 + level * .54, 0)
		crown.material_override = _material(Color("8fcc55") if level % 2 == 0 else Color("72b64d"))
		add_child(crown)

func _material(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = .9
	return m

func _build_characters() -> void:
	hero = MIRA_SCENE.instantiate()
	hero.name = "Mira player"
	hero.position = Vector3(-1.0, 0, .15)
	hero.rotation_degrees.y = 17
	add_child(hero)
	animator = hero.get_node("AnimationPlayer") as AnimationPlayer
	animator.add_animation_library("Melee", MELEE)
	animator.add_animation_library("Shooter", SHOOTER)
	animator.animation_finished.connect(_on_animation_finished)

	var mako := MAKO_SCENE.instantiate()
	mako.name = "Mako by Quaternius CC0"
	mako.position = Vector3(1.65, 0, -.55)
	mako.rotation_degrees.y = -25
	mako.scale = Vector3.ONE * 1.05
	add_child(mako)
	var mako_animator := mako.get_node("AnimationPlayer") as AnimationPlayer
	for animation_name in mako_animator.get_animation_list():
		if "|Idle|" in String(animation_name):
			mako_animator.play(animation_name)
			break

func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var frame := Control.new()
	frame.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(frame)

	var header := PanelContainer.new()
	header.position = Vector2(24, 22)
	header.custom_minimum_size = Vector2(360, 0)
	header.add_theme_stylebox_override("panel", _panel_style(Color(1, 1, 1, .91), 14))
	frame.add_child(header)
	var heading := VBoxContainer.new()
	heading.add_theme_constant_override("separation", 4)
	heading.add_theme_constant_override("margin_left", 12)
	header.add_child(heading)
	var name_label := Label.new()
	name_label.text = "MIRA  /  CHARACTER MOTION LAB"
	name_label.add_theme_font_size_override("font_size", 19)
	name_label.add_theme_color_override("font_color", Color("173e47"))
	heading.add_child(name_label)
	title_label = Label.new()
	title_label.text = "Melee  •  Light Idle"
	title_label.add_theme_color_override("font_color", Color("527176"))
	heading.add_child(title_label)

	var bottom := PanelContainer.new()
	bottom.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_left = 24
	bottom.offset_right = -24
	bottom.offset_top = -98
	bottom.offset_bottom = -22
	bottom.add_theme_stylebox_override("panel", _panel_style(Color("173e47"), 16))
	frame.add_child(bottom)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 9)
	bottom.add_child(row)
	var actions := [
		["Idle", "Melee/LightIdle"],
		["Walk", "Melee/LightWalking"],
		["Run", "Melee/LightRunning"],
		["Slash", "Melee/Slash1"],
		["Jump", "Melee/Jump"],
		["Aim", "Shooter/aim-pistol"],
		["Punch", "Shooter/punch1"],
	]
	for action in actions:
		var button := Button.new()
		button.text = action[0]
		button.custom_minimum_size = Vector2(84, 42)
		button.add_theme_color_override("font_color", Color.WHITE)
		button.add_theme_color_override("font_hover_color", Color("173e47"))
		button.add_theme_stylebox_override("normal", _panel_style(Color("285d65"), 9))
		button.add_theme_stylebox_override("hover", _panel_style(Color("f2c978"), 9))
		button.add_theme_stylebox_override("pressed", _panel_style(Color("e6774c"), 9))
		button.pressed.connect(_play.bind(action[1]))
		row.add_child(button)

	var hint := Label.new()
	hint.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	hint.offset_left = -270
	hint.offset_right = -20
	hint.offset_top = 26
	hint.text = "Drag to orbit  •  Wheel to zoom"
	hint.add_theme_color_override("font_color", Color("173e47"))
	frame.add_child(hint)

func _panel_style(color: Color, radius: int) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = color
	box.set_corner_radius_all(radius)
	box.content_margin_left = 16
	box.content_margin_right = 16
	box.content_margin_top = 10
	box.content_margin_bottom = 10
	return box

func _play(animation_name: String) -> void:
	if not animator.has_animation(animation_name):
		push_warning("Missing animation: " + animation_name)
		return
	selected_animation = animation_name
	animator.play(animation_name, .18)
	title_label.text = animation_name.replace("/", "  •  ")

func _on_animation_finished(animation_name: StringName) -> void:
	if String(animation_name) == selected_animation:
		animator.play(selected_animation, .12)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			drag_active = event.pressed
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP:
			orbit_distance = maxf(5.0, orbit_distance - .45)
			_update_camera()
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			orbit_distance = minf(14.0, orbit_distance + .45)
			_update_camera()
	elif event is InputEventMouseMotion and drag_active:
		orbit_angle -= event.relative.x * .007
		_update_camera()

func _update_camera() -> void:
	if camera == null:
		return
	camera.position = Vector3(sin(orbit_angle) * orbit_distance, 4.4, cos(orbit_angle) * orbit_distance)
	camera.look_at(Vector3(0, 1.05, 0), Vector3.UP)
