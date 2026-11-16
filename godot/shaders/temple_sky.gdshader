shader_type sky;

uniform vec3 zenith_color : source_color = vec3(0.12, 0.32, 0.65);
uniform vec3 horizon_color : source_color = vec3(0.71, 0.80, 0.88);
uniform vec3 ground_color : source_color = vec3(0.22, 0.25, 0.24);
uniform vec3 cloud_light : source_color = vec3(0.97, 0.96, 0.91);
uniform vec3 cloud_shadow : source_color = vec3(0.48, 0.57, 0.65);
uniform float cloud_phase = 0.0;
uniform float daylight = 1.0;
uniform sampler2D cloud_texture : filter_linear_mipmap, repeat_enable;

float hash21(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}
float noise2(vec2 p) {
	return texture(cloud_texture, p * 0.07).r;
}
float cloud_noise(vec2 p) {
	return noise2(p) * 0.55 + noise2(p * 2.03 + 7.2) * 0.27 + noise2(p * 4.07 + 19.1) * 0.13 + noise2(p * 8.13) * 0.05;
}
void sky() {
	float altitude = max(EYEDIR.y, 0.0);
	vec3 colour = mix(horizon_color, zenith_color, pow(altitude, 0.43));
	float horizon_haze = exp(-altitude * 9.0);
	if (LIGHT0_ENABLED) {
		float alignment = clamp(dot(EYEDIR, LIGHT0_DIRECTION), 0.0, 1.0);
		float halo = pow(alignment, 28.0) * 0.23 + pow(alignment, 280.0) * 0.35;
		float disk = smoothstep(0.99991, 0.99996, alignment);
		colour += LIGHT0_COLOR * (halo * daylight + disk * 5.0);
		colour += LIGHT0_COLOR * pow(alignment, 5.0) * horizon_haze * daylight * 0.08;
	}
	if (EYEDIR.y > 0.025) {
		vec2 p = EYEDIR.xz / (EYEDIR.y + 0.19) * 2.0 + vec2(cloud_phase, cloud_phase * 0.23);
		float density = cloud_noise(p);
		float clouds = smoothstep(0.52, 0.73, density) * smoothstep(0.025, 0.18, EYEDIR.y);
		float rim = cloud_noise(p + vec2(-0.08, 0.09));
		vec3 cloud_colour = mix(cloud_shadow, cloud_light, smoothstep(0.47, 0.72, rim));
		colour = mix(colour, cloud_colour, clouds * 0.84);
		// Sparse distant stars disappear naturally as daylight increases.
		vec2 star_grid = SKY_COORDS * vec2(1200.0, 600.0);
		float star = step(0.9985, hash21(floor(star_grid))) * pow(max(0.0, 1.0 - length(fract(star_grid) - 0.5) * 2.0), 5.0);
		colour += vec3(star * (1.0 - daylight) * 1.5);
	}
	if (EYEDIR.y < 0.0) {
		colour = mix(horizon_color, ground_color, smoothstep(0.0, 0.18, -EYEDIR.y));
	}
	COLOR = max(colour, vec3(0.0));
}
