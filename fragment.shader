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

uniform vec3 sky_color;

uniform float max_render_dist;

layout(std430, binding = 0) buffer SphereBuffer {
    float sphere_data[];
};
uniform uint num_spheres;

layout(std430, binding = 1) buffer BoxBuffer {
    float box_data[];
};
layout(std430, binding = 2) buffer BoxMaterialIndexes {
    int box_material_indexes[];
};
uniform uint num_boxes;

struct Material {
    vec3 color;
    float ambientStrength;
    float diffuseStrength;
    float specularStrength;
    float shininess;
};

Material defaultMaterial = Material(
    vec3(0.8, 0.8, 0.8), 0.1, 0.8, 0.5, 32.0
);

layout(std430, binding = 3) buffer MaterialDataBuffer {
    float material_data[];
};

struct Light {
    vec3 pos;
    float intensity;
    vec3 color;
};

layout(std430, binding = 4) buffer LightDataBuffer {
    float light_data[];
};
uniform uint num_lights;

Material getMaterial(uint index) { // the float index ist assumed not the obj index
    return Material(
        vec3(material_data[index], material_data[index + 1], material_data[index + 2]),
        material_data[index + 3],
        material_data[index + 4],
        material_data[index + 5],
        material_data[index + 6]
    );
}

Light getLight(uint index) {
    uint realIndex = index * 7;
    return Light(
        vec3(light_data[realIndex], light_data[realIndex + 1], light_data[realIndex + 2]),
        light_data[realIndex + 3],
        vec3(light_data[realIndex + 4], light_data[realIndex + 5], light_data[realIndex + 6])
    );
}

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

vec3 boxPos(uint index) {
    uint realIndex = index * 7;
    return vec3(box_data[realIndex], box_data[realIndex + 1], box_data[realIndex + 2]);
}

vec3 boxDim(uint index) {
    uint realIndex = index * 7;
    return vec3(box_data[realIndex + 3], box_data[realIndex + 4], box_data[realIndex + 5]);
}

Material boxMaterial(uint index) {
    return getMaterial(box_material_indexes[index]);
}

float boxDist(vec3 curr_pos, uint index) {
    vec3 box_corner = boxPos(index);
    vec3 box_size = boxDim(index);
    vec3 box_center = box_corner + box_size * 0.5;

    vec3 q = abs(curr_pos - box_center) - box_size * 0.5;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

float infSpheresDist(vec3 curr_pos) {
    vec3 mod_pos = vec3(mod(curr_pos.x, 50), mod(curr_pos.y, 50), mod(curr_pos.z, 50));
    return distance(vec3(25, 25, 25), mod_pos) - 5;
}

float dist(vec3 curr_pos) {
    float min_dist = max_render_dist;
    for (int i = 0; i < num_spheres; i++) {
        float curr_dist = distance(curr_pos, spherePos(i)) - sphereRadius(i);
        min_dist = min(curr_dist, min_dist);//, smooth_factor);
    }
    for (int i = 0; i < num_boxes; i++) {
        min_dist = min(boxDist(curr_pos, i), min_dist);//, smooth_factor);
    }
    min_dist = min(abs(curr_pos.y), min_dist);//, smooth_factor); // floor at y = 0
    min_dist = min(infSpheresDist(curr_pos), min_dist);//, smooth_factor);
    return max(min_dist, 0.0);
}

Material getNearestMaterial(vec3 curr_pos) {
    Material curr_material = defaultMaterial;
    float min_dist = max_render_dist;
    for (int i = 0; i < num_spheres; i++) {
        float curr_dist = distance(curr_pos, spherePos(i)) - sphereRadius(i);
        min_dist = min(curr_dist, min_dist); // spheres don't currently have a material
    }
    min_dist = min(abs(curr_pos.y), min_dist); // floor doesn't have a material
    min_dist = min(infSpheresDist(curr_pos), min_dist); // the inf spheres don't have a material
    for (int i = 0; i < num_boxes; i++) {
        float curr_dist = boxDist(curr_pos, i);
        if (curr_dist < min_dist) {
            min_dist = curr_dist;
            curr_material = boxMaterial(i);
        }
    }
    return curr_material;
}

vec3 getNormal(vec3 p) {
    float eps = 0.0005 * max(1.0, length(p)); // Scales epsilon with distance
    vec2 e = vec2(eps, 0.0);
    return normalize(vec3(
        dist(p + e.xyy) - dist(p - e.xyy),
        dist(p + e.yxy) - dist(p - e.yxy),
        dist(p + e.yyx) - dist(p - e.yyx)
    ));
}

// old shade fuction
//vec3 shade(vec3 p, Material mat, vec3 lightPos) {
//    vec3 N = getNormal(p); // Surface normal
//    vec3 L = normalize(lightPos - p); // Light direction
//    vec3 V = normalize(-p); // View direction (camera at origin)
//    vec3 R = reflect(-L, N); // Reflection direction
//
//    // Lambertian diffuse reflection
//    float diff = max(dot(N, L), 0.0) * mat.diffuseStrength;
//    // Phong specular reflection
//    float spec = pow(max(dot(R, V), 0.0), mat.shininess) * mat.specularStrength * smoothstep(0.0, 0.2, dot(N, L));
//    // Ambient light
//    float ambient = mat.ambientStrength;
//
//    return mat.color * (ambient + diff) + vec3(1.0) * spec;
//}

vec3 shade(vec3 p, Material mat) {
    vec3 finalColor = vec3(0.0); // Start with no light contribution

    // Loop over all the lights
    for (int i = 0; i < num_lights; ++i) {
        Light light = getLight(i);
        vec3 L = normalize(light.pos - p); // Light direction
        vec3 N = getNormal(p); // Surface normal
        vec3 V = normalize(-p); // View direction (camera at origin)
        vec3 R = reflect(-L, N); // Reflection direction

        // Diffuse component (Lambertian reflection)
        float diff = max(dot(N, L), 0.0) * mat.diffuseStrength;

        // Specular component (Phong reflection)
        float spec = pow(max(dot(R, V), 0.0), mat.shininess) * mat.specularStrength * smoothstep(0.0, 0.2, dot(N, L));

        // Ambient component
        float ambient = mat.ambientStrength;

        // Accumulate the light contributions (color * intensity)
        finalColor += light.color * light.intensity * (ambient + diff + spec);
    }

    // Apply the material color
    return mat.color * finalColor;
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
    
    if (total_dist < max_render_dist) {
        Material material = getNearestMaterial(curr_pos);
        pixel_color = vec4(shade(curr_pos, material), 1.0 + smooth_factor);
    }
    else {
        pixel_color = vec4(sky_color, 1.0 + smooth_factor);
    }
}