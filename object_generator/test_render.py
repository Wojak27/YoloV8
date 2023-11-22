import numpy as np
import trimesh
import pyrender

# Create a red square (thin box)
square_size = .5  # half-size of the square
square = trimesh.creation.box(extents=[square_size, square_size, 0.5])
square.visual.vertex_colors = [255, 0, 0, 255]  # Red color

# Create a brown table (large plane)
table_size = 2  # half-size of the table
table = trimesh.creation.box(extents=[table_size, table_size, 0.1])
table.visual.vertex_colors = [115, 74, 41, 255]  # Brown color
table.apply_translation([0, 0, -0.05])  # Lower the table so the square stands on it

# Create scene
scene = pyrender.Scene()

# Add objects to the scene
square_mesh = pyrender.Mesh.from_trimesh(square)
table_mesh = pyrender.Mesh.from_trimesh(table)
scene.add(square_mesh)
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

# Set up the light
light = pyrender.SpotLight(color=np.ones(3), intensity=3.0,
                           innerConeAngle=np.pi/8.0,
                           outerConeAngle=np.pi/6.0)
scene.add(light, pose=camera_pose)

# Render the scene
r = pyrender.OffscreenRenderer(600, 600)
color, depth = r.render(scene)
r.delete()

# Save the rendered images
import imageio
imageio.imwrite('/usr/src/app/data/scene_color.png', color)
# imageio.imwrite('/usr/src/app/data/scene_depth.png', depth)
