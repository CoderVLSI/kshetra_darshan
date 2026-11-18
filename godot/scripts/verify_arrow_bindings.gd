extends SceneTree

func _initialize() -> void:
	var bindings = {KEY_UP: "move_forward", KEY_DOWN: "move_backward", KEY_LEFT: "move_left", KEY_RIGHT: "move_right"}
	for key in bindings:
		var event = InputEventKey.new()
		event.keycode = key
		event.pressed = true
		if not event.is_action_pressed(bindings[key]):
			push_error("Arrow binding failed: " + str(bindings[key]))
			quit(1)
			return
	print("Four directional arrow bindings passed")
	quit()
