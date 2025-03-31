from pymol import cmd
from pymol.cgo import *
import numpy as np

# Membrane normal vector (already correct)
normal = np.array([
    0,
    0,
    13.46204853
])
# Define membrane planes
center = np.array([0, 0, 0])  # Center is now at the origin
upper_plane_center = center + (normal)
lower_plane_center = center - (normal)

# Plane size (adjust if necessary)
plane_size = 40  # Reduce size if it appears too wide

# Generate a square plane in 3D space
corners = np.array([
    [-plane_size, -plane_size, 0],
    [plane_size, -plane_size, 0],
    [-plane_size, plane_size, 0],
    [plane_size, plane_size, 0]
])

# Function to create and load a plane in PyMOL
def create_plane(plane_center, name):
    obj = [
        BEGIN, TRIANGLE_STRIP,
        COLOR, 0.0, 0.5, 1.0,  # Blue color
        ALPHA, 0.5,  # 50% transparency
    ]

    for vertex in corners:
        vertex = vertex + plane_center  # Shift plane to the correct position
        obj.extend([VERTEX, *vertex])

    obj.append(END)

    cmd.load_cgo(obj, name)

# Create upper and lower membrane planes
create_plane(upper_plane_center, "upper_membrane_plane")
create_plane(lower_plane_center, "lower_membrane_plane")