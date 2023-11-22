import torch
from torch.utils.data import Dataset
import numpy as np
import trimesh
import pyrender
import random
import imageio
from PIL import Image
from io import BytesIO

from test_render1 import create_random_object

# Your existing functions go here (random_color, create_pyramid, random_position, etc.)

class RandomSceneDataset(Dataset):
    def __init__(self, num_samples, transform=None):
        self.num_samples = num_samples
        self.transform = transform

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        # Create scene
        scene = pyrender.Scene()

        # Add a random number of objects to the scene
        num_objects = random.randint(1, 5)  # Random number of objects
        object_poses = []  # Store object poses

        for _ in range(num_objects):
            obj = create_random_object()
            obj_pose = obj.centroid  # Get the centroid as the pose
            object_poses.append(obj_pose)

            obj_mesh = pyrender.Mesh.from_trimesh(obj)
            scene.add(obj_mesh)

        # Add table and other scene setup (camera, lights, etc.) here

        # Render the scene
        r = pyrender.OffscreenRenderer(600, 600)
        
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
        color, depth = r.render(scene)
        r.delete()

        # Convert to PIL Image
        image = Image.fromarray(color)

        # Apply transformations if any
        if self.transform:
            image = self.transform(image)

        # Convert object poses to tensor
        object_poses = torch.tensor(object_poses, dtype=torch.float32)

        return image, object_poses

# Usage example
dataset = RandomSceneDataset(num_samples=100)
image, poses = dataset[0]  # Get the first sample
print(np.array(image).shape, poses.shape)
