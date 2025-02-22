import pygame
import moderngl
import time
import numpy as np
from vectors import *
from objects import *

pygame.init()

start_time = time.time()

FPS = 60
clock = pygame.time.Clock()

WIDTH = 800
HEIGHT = 600
pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("Raymarching")

ctx = moderngl.create_context()

tris = ctx.buffer(np.array([
    -1.0,  1.0,  1.0,  1.0, -1.0, -1.0,
     1.0,  1.0,  1.0, -1.0, -1.0, -1.0
], dtype='f4').tobytes())

fragment_shader = ""
vertex_shader = ""
with open("fragment.shader", "r") as file:
    fragment_shader = file.read()
with open("vertex.shader", "r") as file:
    vertex_shader = file.read()

program = ctx.program(
    vertex_shader=vertex_shader,
    fragment_shader=fragment_shader
)
vao = ctx.simple_vertex_array(program, tris, 'in_vert')

# get uniforms
screen_width_uniform = program["screen_width"]
screen_height_uniform = program["screen_height"]

cam_pos_uniform = program["cam_pos"]
cam_direc_uniform = program["cam_direc"]
cam_right_uniform = program["cam_right"]
cam_up_uniform = program["cam_up"]
focal_lenght_uniform = program["focal_lenght"]

smooth_factor_uniform = program["smooth_factor"]
max_render_dist_uniform = program["max_render_dist"]

num_spheres_uniform = program["num_spheres"]

sphere_array = SphereArr()
#emptySphere = sphere_array.addSphere()
#emptySphere.setPos(vec3(100, 100, 100), sphere_array)
#emptySphere.setRadius(0, sphere_array)

sphere1 = sphere_array.addSphere()
sphere2 = sphere_array.addSphere()
sphere3 = sphere_array.addSphere()

sphere1.setRadius(5.0, sphere_array)
sphere2.setRadius(5.0, sphere_array)
sphere3.setRadius(5.0, sphere_array)

sphere_data_buffer = ctx.buffer(sphere_array.toBytes())
sphere_data_buffer.bind_to_storage_buffer(0)

cam_pos: vec3 = vec3(0.0, 15.0, -20.0)
cam_direc: vec3 = vec3(0.0, 0.0, 1.0)
focal_lenght = 2

smooth_factor = 1

cam_speed = 5
delta_time = 0

real_screen_width = 4

max_render_dist = 40

w, a, s, d = False, False, False, False
up, down = False, False

# Mouse sensitivity
mouse_sensitivity = 0.002  

# Center the mouse
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
mouse_move = True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            state = event.type == pygame.KEYDOWN
            if event.key == pygame.K_w:
                w = state
            elif event.key == pygame.K_a:
                a = state
            elif event.key == pygame.K_s:
                s = state
            elif event.key == pygame.K_d:
                d = state
            elif event.key == pygame.K_UP:
                up = state
            elif event.key == pygame.K_DOWN:
                down = state
        elif event.type == pygame.MOUSEMOTION and mouse_move:
            dx, dy = event.rel
            dx *= -mouse_sensitivity
            dy *= mouse_sensitivity

            # Rotate camera direction based on mouse movement
            yaw = dx  # Left/right movement affects yaw
            pitch = dy  # Up/down movement affects pitch

            # Apply rotation
            cam_direc = rotate_vector(cam_direc, yaw, pitch)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
                mouse_move = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            mouse_move = True

    # Normalize cam_direc
    cam_direc = cam_direc.unitVec()
        
    delta_time = clock.tick(FPS) / 1000
    elapsed_time = time.time() - start_time

    cam_right = vec3(1, 0, 0)
    if not (cam_direc == vec3(0, 1, 0)):
        cam_right = crossProd(vec3(0, 1, 0), cam_direc).unitVec()
    cam_up = crossProd(cam_direc, cam_right).unitVec()

    cam_pos += (cam_right * (d - a) + cam_up * (up - down) + cam_direc * (w - s)) * cam_speed * delta_time

    sphere1.setPos(vec3(0, cos(elapsed_time) * 10 + 15, 0), sphere_array)
    sphere2.setPos(vec3(sin(elapsed_time) * 10, 15, 0), sphere_array)
    sphere3.setPos(vec3(sin(elapsed_time + pi) * 10, cos(elapsed_time + pi) * 10 + 15, 0), sphere_array)
    smooth_factor = ((sin(elapsed_time) + 1) / 2) * 4

    # set uniforms
    screen_width_uniform.value = real_screen_width
    screen_height_uniform.value = (HEIGHT / WIDTH) * real_screen_width

    cam_pos_uniform.value = cam_pos.tuple()
    cam_direc_uniform.value = cam_direc.tuple()
    cam_right_uniform.value = cam_right.tuple()
    cam_up_uniform.value = cam_up.tuple()
    focal_lenght_uniform.value = focal_lenght

    smooth_factor_uniform.value = smooth_factor
    max_render_dist_uniform.value = max_render_dist
    
    sphere_data_buffer.write(sphere_array.toBytes())
    num_spheres_uniform.value = sphere_array.numSpheres

    ctx.clear(0.1, 0.1, 0.1)
    vao.render(moderngl.TRIANGLE_STRIP)
    pygame.display.flip()

pygame.quit()