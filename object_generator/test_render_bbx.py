import sys
import datetime
import copy 
import os
import numpy as np
import trimesh
import pyrender
import random
import imageio
from PIL import Image
from trimesh import primitives
from PIL import ImageDraw

os.environ['PYOPENGL_PLATFORM'] = 'egl' 


def random_color():
    return random.choice([[255, 0, 0, 255], [0, 255, 0, 255], [0, 0, 255, 255]])   #[random.randint(0, 255) for _ in range(3)] + [255]

def create_pyramid(base_length, height):
    # Vertices of the pyramid
    vertices = np.array([
        [0, 0, 0],  # Base corner 1
        [base_length, 0, 0],  # Base corner 2
        [base_length, base_length, 0],  # Base corner 3
        [0, base_length, 0],  # Base corner 4
        [base_length / 2, base_length / 2, height]  # Apex
    ])

    # Faces of the pyramid (triangles for sides and a quadrilateral for the base)
    faces = [
        [0, 1, 4],  # Side 1
        [1, 2, 4],  # Side 2
        [2, 3, 4],  # Side 3
        [3, 0, 4],  # Side 4
        [0, 1, 2, 3]  # Base
    ]

    return trimesh.Trimesh(vertices=vertices, faces=faces)

def random_position(obj, height_offset):
    x = random.uniform(-0.4 * table_size, 0.4 * table_size)
    y = random.uniform(-0.4 * table_size, 0.4 * table_size)
    angle = np.radians(np.random.randint(0, 45))  # 45 degree rotation
    axis = [0, 0, 1]  # Around z-axis
    transformation_matrix = trimesh.transformations.rotation_matrix(angle, axis)
    obj.apply_transform(transformation_matrix)

    obj.apply_translation([x, y, height_offset - 0.1])
    count = 0
    num_tries = 0
    while num_tries < 1000 and count != len(objects):
        if num_tries == 999:
            print("Failed to place object")
            
        count = 0
        num_tries += 1
        obj.apply_translation([-x, -y, -height_offset])
        x = random.uniform(-0.4 * table_size, 0.4 * table_size)
        y = random.uniform(-0.4 * table_size, 0.4 * table_size)
        obj.apply_translation([x, y, height_offset])
        print("try: {} P object:{}".format(num_tries, len(objects)))
        for other in objects:
            # if other.intersection(obj).is_empty:
            if obj.vertices.min(0)[0] > other.vertices.max(0)[0] or obj.vertices.max(0)[0] < other.vertices.min(0)[0] \
                or obj.vertices.min(0)[1] > other.vertices.max(0)[1] or obj.vertices.max(0)[1] < other.vertices.min(0)[1] \
                or obj.vertices.min(0)[2] > other.vertices.max(0)[2] or obj.vertices.max(0)[2] < other.vertices.min(0)[2]:
                count +=1
            else:
                print("Intersecting")
    pass
def create_cube(size):
    cube = trimesh.creation.box(extents=[size * 0.6, size * 0.59, size * 0.29])
    cube.visual.vertex_colors = random_color()
    random_position(cube, size * 0.29 )
    return cube


def create_triangular_prism(size):
    length, width, height = 0.34 * size, 0.58 * size, 0.29 * size
    # Vertices of the shape
    vertices = np.array([
        [0, 0, 0],          # Base - bottom left
        [length, 0, 0],     # Base - bottom right
        [length, width, 0], # Base - top right
        [0, width, 0],      # Base - top left
        [0, width/2, height],  # Top - left
        [length, width/2, height] # Top - right
    ])

    # Faces of the shape
    faces = [
        [0, 1, 5, 4], # Side face - rectangle
        [2, 3, 4, 5], # Side face - rectangle
        [0, 1, 2, 3],  # Base - rectangle
        [1, 2, 5, 1],
        [0, 3, 4, 0]
    ]

    # Create the mesh
    prism = trimesh.Trimesh(vertices=vertices, faces=faces)
    prism.visual.vertex_colors = random_color()
    random_position(prism, height)
    return prism

def create_hole_box(size):
    box = trimesh.creation.box(extents=np.array([ 0.6, 0.68, 0.34 ]) * size)
    cylinder = trimesh.creation.cylinder(radius=0.2 * size, height=0.34 * size, sections=32)
    box_with_hole = box.difference(cylinder, engine='scad')
    plane_normal = [0, 1, 0]  # Normal vector to the plane (x-axis in this case)
    plane_origin = box_with_hole.centroid  # The plane will pass through the mesh centroid

    box_with_hole = box_with_hole.slice_plane(plane_origin, plane_normal, cap=True)
    box_with_hole.visual.vertex_colors = random_color()
    random_position(box_with_hole, 0.34 * size)
    
    return box_with_hole

def create_random_object():
    obj_type = random.choice(['hole_box', 'cube', 'prism'])
    size = 0.3 # random.uniform(0.1, 0.3)
    if obj_type == 'cube':
        obj = create_cube(size)
    if obj_type == 'prism':
        obj = create_triangular_prism(size)
    elif obj_type == 'hole_box':
        obj = create_hole_box(size)
    return obj, obj.vertices

# Create a brown table (large plane)
table_size = 2  # half-size of the table
table = trimesh.creation.box(extents=[table_size, table_size, 0.1])
table.visual.vertex_colors = [115, 74, 41, 255]  # Brown color
table.apply_translation([0, 0, -0.05])  # Lower the table so the square stands on it

# Create scene
scene = pyrender.Scene()


# Add a random number of objects to the scene




# pyramid_mesh = pyrender.Mesh.from_trimesh(pyramid)
table_mesh = pyrender.Mesh.from_trimesh(table)
# scene.add(pyramid_mesh)
scene.add(table_mesh)

# Set up the camera (simple perspective camera)
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
camera_position = [0, 0, 2]
rotation_angle = np.radians(0)  # Convert 5 degrees to radians
rotation_matrix = np.array([
    [1, 0, 0, 0],
    [0, np.cos(rotation_angle), -np.sin(rotation_angle), 0],
    [0, np.sin(rotation_angle), np.cos(rotation_angle), 0],
    [0, 0, 0, 1]
])

# Combine rotation with translation for the camera pose
camera_pose = rotation_matrix @ np.array([
    [1, 0, 0, camera_position[0]],
    [0, 1, 0, camera_position[1]],
    [0, 0, 1, camera_position[2]],
    [0, 0, 0, 1]
])
s = np.sqrt(2)/2
# camera_pose = np.array([
#    [0.0, -s,   s,   1.5],
#    [1.0,  0.0, 0.0, 0.0],
#    [0.0,  s,   s,   1.5],
#    [0.0,  0.0, 0.0, 1.0],
# ])
# camera_pose = np.array([
#     [1, 0, 0, 0],
#     [0, 1, 0, 0],
#     [0, 0, 1, 2],  # Change 10 to the desired height above the object
#     [0, 0, 0, 1],
# ])
scene.add(camera, pose=camera_pose)

num_objects = random.randint(1,1)  # Random number of objects
objects = []
vertices_list = []
for _ in range(num_objects):
    obj, vertices = create_random_object()
    objects.append(obj)
    vertices_list.append(vertices)
    print("verticies list: ", vertices_list)
    obj_mesh = pyrender.Mesh.from_trimesh(obj)
    scene.add(obj_mesh)

def add_random_light(scene):
    # Randomly choose a type of light
    light_type = random.choice(['directional'])#, ['point','directional', 'spot'])

    # Common parameters for all lights
    color = np.random.rand(3)  # Random color
    intensity = random.uniform(1.0, 10.0)  # Random intensity between 1 and 10

    # Random position for point and spot lights
    position = np.array([random.uniform(-1, 1) for _ in range(3)])

    # Create and add the light to the scene
    if light_type == 'point':
        light = pyrender.PointLight(color=color, intensity=intensity)
    elif light_type == 'directional':
        light = pyrender.DirectionalLight(color=color, intensity=intensity)
        position = np.zeros(3)  # Directional light doesn't need a position
    else:  # 'spot'
        innerConeAngle = random.uniform(0, np.pi/2)
        outerConeAngle = random.uniform(innerConeAngle, np.pi/2)
        light = pyrender.SpotLight(color=color, intensity=intensity, 
                                   innerConeAngle=innerConeAngle, 
                                   outerConeAngle=outerConeAngle)

    # Light pose
    light_pose = np.eye(4)
    light_pose[:3, 3] = position

    # Add light to the scene
    scene.add(light, pose=light_pose)

add_random_light(scene)

# Render the scene
viewport_width = 600
viewport_height = 600
r = pyrender.OffscreenRenderer(viewport_width = viewport_width, viewport_height = viewport_height)



# Camera matrices
view_matrix = camera_pose
projection_matrix = camera.get_projection_matrix(width=viewport_width, height=viewport_height)

# Function to project 3D vertices to 2D
def project_3d_to_2d(vertices, view_matrix, projection_matrix):
    # Transform vertices to camera space
    vertices_4d = np.hstack((vertices, np.ones((vertices.shape[0], 1))))
    vertices_cam_space = np.dot(view_matrix, vertices_4d.T).T

    # Transform vertices to clip space
    vertices_clip_space = np.dot(projection_matrix, vertices_cam_space.T).T

    # Perform perspective divide to get normalized device coordinates
    vertices_ndc = vertices_clip_space[:, :3] / vertices_clip_space[:, 3][:, np.newaxis]

    # Transform to viewport coordinates
    viewport_x = 0
    viewport_y = 0
    viewport_width = 600  # Match with your viewport size
    viewport_height = 600
    vertices_viewport = np.zeros_like(vertices_ndc)
    vertices_viewport[:, 0] = (-vertices_ndc[:, 0] + 1) * viewport_width / 2
    vertices_viewport[:, 1] = (vertices_ndc[:, 1]+1) * viewport_height / 2  # Flip Y-axis
    print("Camera Space Coordinates:\n", vertices_cam_space)
    print("Clip Space Coordinates:\n", vertices_clip_space)
    print("Normalized Device Coordinates:\n", vertices_ndc)
    print("Viewport Coordinates:\n", vertices_viewport)

    return vertices_viewport[:, :2]

color, depth = r.render(scene)
# Example: Project the vertices of the sphere
# Now, vertices_2d contains the 2D projections of the sphere's vertices
# You can use this to draw the bounding box on the image
# Convert the rendered image to a PIL image for drawing

img = Image.fromarray(color)
# Project vertices of each object to 2D and draw bounding boxes
image = Image.fromarray(color)
draw = ImageDraw.Draw(image)
for vertices in vertices_list:
    vertices_2d = project_3d_to_2d(vertices, view_matrix, projection_matrix)
    min_x, min_y = np.min(vertices_2d, axis=0)
    max_x, max_y = np.max(vertices_2d, axis=0)
    draw.rectangle([min_x, min_y, max_x, max_y], outline="red")
    for vertex in vertices_2d:
        draw.ellipse((vertex[0] - 2, vertex[1] - 2, vertex[0] + 2, vertex[1] + 2), fill="red")
        # Draw lines or points instead of rectangles to debug

# Save or display the image
image.save("rendered_with_bbox.png")
# image.show()


file_name = f"output/rendered_scene{1}.png"
os.makedirs("output", exist_ok=True)

img.save(file_name)
r.delete()

# Save the rendered images
imageio.imwrite('scene_color.png', color)
# imageio.imwrite('/usr/src/app/data/scene_depth.png', depth)


