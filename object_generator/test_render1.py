import os
import numpy as np
import trimesh
import pyrender
import random
import imageio
from PIL import Image
from trimesh import primitives

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
    obj.apply_translation([x, y, height_offset])
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
            if other.intersection(obj).is_empty:
                count +=1
            else:
                print("Intersecting")
    pass
def create_cube(size):
    cube = trimesh.creation.box(extents=[size * 0.6, size * 0.59, size * 0.29])
    cube.visual.vertex_colors = random_color()
    random_position(cube, size * 0.29 )
    return cube

def create_box(size):
    box = trimesh.creation.box(extents=np.array([0.34, 0.6, 0.34]) * size)
    box.visual.vertex_colors = random_color()
    return box

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
    box = trimesh.creation.box(extents=np.array([0.34, 0.6, 0.34]) * size)
    cylinder = trimesh.creation.cylinder(radius=0.1 * size, height=0.34 * size, sections=32)
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
        return create_cube(size)
    if obj_type == 'prism':
        return create_triangular_prism(size)
    elif obj_type == 'hole_box':
        return create_hole_box(size)

# Create a brown table (large plane)
table_size = 2  # half-size of the table
table = trimesh.creation.box(extents=[table_size, table_size, 0.1])
table.visual.vertex_colors = [115, 74, 41, 255]  # Brown color
table.apply_translation([0, 0, -0.05])  # Lower the table so the square stands on it

# Create scene
scene = pyrender.Scene()


# Add a random number of objects to the scene
num_objects = random.randint(20, 20)  # Random number of objects
objects = []
for _ in range(num_objects):
    obj = create_random_object()
    objects.append(obj)
    obj_mesh = pyrender.Mesh.from_trimesh(obj)
    scene.add(obj_mesh)


# pyramid_mesh = pyrender.Mesh.from_trimesh(pyramid)
table_mesh = pyrender.Mesh.from_trimesh(table)
# scene.add(pyramid_mesh)
scene.add(table_mesh)

# Set up the camera (simple perspective camera)
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
camera_position = [0, 0, 2]
rotation_angle = np.radians(15)  # Convert 5 degrees to radians
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
r = pyrender.OffscreenRenderer(viewport_width = 600, viewport_height = 600)

color, depth = r.render(scene)
img = Image.fromarray(color)
img.save('rendered_scene.png')
r.delete()

# Save the rendered images
imageio.imwrite('scene_color.png', color)
# imageio.imwrite('/usr/src/app/data/scene_depth.png', depth)

