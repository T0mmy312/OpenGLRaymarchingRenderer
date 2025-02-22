#version 430

in vec2 pixel_pos;
out vec4 pixel_color;

uniform float screen_width;
uniform float screen_height;

uniform vec3 cam_pos;
uniform vec3 cam_direc; // unit vector of camera forward direction
uniform vec3 cam_right; // unit vector of camera right direction
uniform vec3 cam_up; // unit vector of camera up direction
uniform float focal_lenght;

uniform float smooth_factor;

uniform float max_render_dist;

layout(std430, binding = 0) buffer SphereBuffer {
    float sphere_data[];
};
uniform uint num_spheres;

float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5*(a-b)/k, 0.0, 1.0);
    return mix(a, b, h) - k*h*(1.0-h);
}

vec3 spherePos(uint index) {
    uint realIndex = index * 4;
    return vec3(sphere_data[realIndex], sphere_data[realIndex + 1], sphere_data[realIndex + 2]);
}

float sphereRadius(uint index) {
    return sphere_data[index * 4 + 3];
}

float dist(vec3 curr_pos) {
    float min_dist = max_render_dist;
    for (int i = 0; i < num_spheres; i++) {
        float curr_dist = distance(curr_pos, spherePos(i)) - sphereRadius(i);
        min_dist = smin(curr_dist, min_dist, smooth_factor);
    }
    min_dist = smin(abs(curr_pos.y), min_dist, smooth_factor); // floor at y = 0
    return max(min_dist, 0.0);
}

void main() {
    vec2 screen_pos = pixel_pos * vec2(screen_width / 2, screen_height / 2);
    vec3 direc = normalize(cam_direc * focal_lenght + cam_right * screen_pos.x + cam_up * screen_pos.y);

    float total_dist = 0;

    vec3 curr_pos = cam_pos;
    float curr_dist = dist(curr_pos);
    while (curr_dist > 0.0001 && total_dist < max_render_dist) { // 0.0001 for floating point tolerances
        curr_pos += direc * curr_dist;
        total_dist += curr_dist;
        curr_dist = dist(curr_pos);
    }

    float color = 1 - total_dist / max_render_dist;
    pixel_color = vec4(vec3(color), 1.0);
}