import numpy as np
import trimesh
import pyrender
import random
import imageio

def random_color():
    return [random.randint(0, 255) for _ in range(3)] + [255]

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
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    obj.apply_translation([x, y, height_offset])
    
    
def create_cube(size):
    cube = trimesh.creation.box(extents=[size, size, size])
    cube.visual.vertex_colors = random_color()
    random_position(cube, size / 2)
    return cube

def create_cylinder(height, radius):
    cylinder = trimesh.creation.cylinder(radius=radius, height=height)
    cylinder.visual.vertex_colors = random_color()
    random_position(cylinder, height / 2)
    return cylinder

def create_random_object():
    obj_type = random.choice(['cube', 'cylinder'])
    if obj_type == 'cube':
        size = random.uniform(0.1, 0.3)
        return create_cube(size)
    elif obj_type == 'cylinder':
        height = random.uniform(0.1, 0.3)
        radius = random.uniform(0.05, 0.15)
        return create_cylinder(height, radius)

# Create a brown table (large plane)
table_size = 2  # half-size of the table
table = trimesh.creation.box(extents=[table_size, table_size, 0.1])
table.visual.vertex_colors = [115, 74, 41, 255]  # Brown color
table.apply_translation([0, 0, -0.05])  # Lower the table so the square stands on it

# Create scene
scene = pyrender.Scene()


# Add a random number of objects to the scene
num_objects = random.randint(1, 5)  # Random number of objects
for _ in range(num_objects):
    obj = create_random_object()
    obj_mesh = pyrender.Mesh.from_trimesh(obj)
    scene.add(obj_mesh)


# pyramid_mesh = pyrender.Mesh.from_trimesh(pyramid)
table_mesh = pyrender.Mesh.from_trimesh(table)
# scene.add(pyramid_mesh)
scene.add(table_mesh)

# Set up the camera (simple perspective camera)
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
s = np.sqrt(2)/2
camera_pose = np.array([
   [0.0, -s,   s,   1.5],
   [1.0,  0.0, 0.0, 0.0],
   [0.0,  s,   s,   1.5],
   [0.0,  0.0, 0.0, 1.0],
])
scene.add(camera, pose=camera_pose)

def add_random_light(scene):
    # Randomly choose a type of light
    light_type = random.choice(['point', 'directional', 'spot'])

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
r = pyrender.OffscreenRenderer(600, 600)
color, depth = r.render(scene)
r.delete()

# Save the rendered images
imageio.imwrite('/usr/src/app/data/scene_color.png', color)
# imageio.imwrite('/usr/src/app/data/scene_depth.png', depth)

