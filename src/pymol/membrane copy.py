from pymol import cmd
from pymol.cgo import *

# Plane size (adjust if needed)
PLANE_SIZE = 100

# Define Z-coordinates for both planes
z_values = [120.62298965454102 + 20, 120.62298965454102 - 20]

# Function to create a plane at a given Z-coordinate
def create_plane(z, plane_name):
    obj = [
        BEGIN, TRIANGLE_STRIP,
        COLOR, 0.5, 0.5, 0.5,  # Gray color
        ALPHA, 0.5,  # 50% transparency
    ]
    
    # Define four corners of the plane
    corners = [
        [-PLANE_SIZE, -PLANE_SIZE, z],
        [PLANE_SIZE, -PLANE_SIZE, z],
        [-PLANE_SIZE, PLANE_SIZE, z],
        [PLANE_SIZE, PLANE_SIZE, z]
    ]

    for corner in corners:
        obj.extend([VERTEX, *corner])

    obj.append(END)

    # Load the object into PyMOL
    cmd.load_cgo(obj, plane_name)

# Create both planes
create_plane(z_values[0], "upper_plane")
create_plane(z_values[1], "lower_plane")