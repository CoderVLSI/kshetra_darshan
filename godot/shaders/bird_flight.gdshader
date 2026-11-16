shader_type spatial;
render_mode unshaded, cull_disabled;
void vertex() {
	float wing = smoothstep(0.07, 0.38, abs(VERTEX.x));
	VERTEX.y += sin(TIME * 7.0 + INSTANCE_CUSTOM.x * 6.28318) * wing * 0.17;
}
void fragment() {
	ALBEDO = vec3(0.10, 0.12, 0.14);
}
