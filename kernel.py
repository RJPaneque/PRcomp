import numpy as np
import itertools
from tqdm import tqdm

def VG(dist_aPSF3D, STEP, SIZE, rlim, voxel_griding=5, source_griding=3, disable_tqdm=False):
    """
    Performs voxel gridding (VG) to compute a 3D PSF kernel.

    Parameters:
        dist_aPSF3D (function): Function that calculates the PSF value given a distance r
        STEP (list): Voxel dimensions in cm [dx, dy, dz] in cm
        SIZE (list): Kernel size in voxels [nx, ny, nz]
        rlim (tuple): (rmin, rmax) Range of distances to consider in mm
        voxel_griding (int): Number of samples within each voxel
        source_griding (int): Number of samples within the source voxel

    Returns:
        numpy.ndarray: Normalized 3D PSF kernel
    """
    if voxel_griding % 2 == 0:
        voxel_griding += 1  # Ensure voxel_griding is odd
        print("voxel_griding is changed to", voxel_griding)
    if source_griding % 2 == 0:
        source_griding += 1
        print("source_griding is changed to", source_griding)
    if len(STEP) != 3 or len(SIZE) != 3:
        raise ValueError("STEP and SIZE must be lists of length 3.")
    if len(rlim) != 2:
        raise ValueError("rlim must be a tuple of length 2.")
    
    STEP = [s*10 for s in STEP]  # Convert to mm

    rmin, rmax = rlim
    rmin = max(rmin, 1e-8)  # Ensure rmin is not zero
    RMAX = 3**0.5 * max(STEP)*max(SIZE)/2
    rmax = RMAX if rmax is None or rmax > RMAX else rmax    # Ensure rmax is within reasonable bounds

    dx, dy, dz = STEP
    nx, ny, nz = SIZE
    aPSF_kernel = np.zeros((nx, ny, nz), dtype=np.float32)

    # Check size is odd
    if nx % 2 == 0 or ny % 2 == 0 or nz % 2 == 0:
        raise ValueError("Kernel sizes must be odd to properly place the source voxel.")

    # Load iterators to save memory
    voxel_indices = ((ix, iy, iz) for ix in range(nx) for iy in range(ny) for iz in range(nz))
    auxiliary_indices = ((ix, iy, iz) for ix in range(nx) for iy in range(ny) for iz in range(nz))
    voxel_centers = (((ix-nx//2)*dx, (iy-ny//2)*dy, (iz-nz//2)*dz) for ix, iy, iz in auxiliary_indices)

    # Grid points in source voxel
    grid_source = [np.linspace(0, step/2, 1+source_griding//2) for step in STEP]  # Only positive to always start at 0
    grid_source = [np.sort(np.concat((-g[1:], +g), dtype=np.float32)) for g in grid_source]         # Include negative values

    # Loop over all voxels in kernel and grid them
    for (ix,iy,iz), (cx,cy,cz) in tqdm(zip(voxel_indices, voxel_centers), total=nx*ny*nz, disable=disable_tqdm):
      grid_xyz = np.linspace((cx-dx/2, cy-dy/2, cz-dz/2), (cx+dx/2, cy+dy/2, cz+dz/2), voxel_griding)
      x,y,z = np.meshgrid(grid_xyz[:, 0], grid_xyz[:, 1], grid_xyz[:, 2], indexing='ij')

      # Loop over all sampled source points and eval aPSF3D(r)
      for (sx, sy, sz) in itertools.product(*grid_source):
        r = np.sqrt((x-sx)**2 + (y-sy)**2 + (z-sz)**2)
        mask = (r >= rmin) & (r <= rmax)
        psf = dist_aPSF3D(r) * mask
        aPSF_kernel[ix, iy, iz] += psf.sum()

    aPSF_kernel /= aPSF_kernel.sum()    
    return aPSF_kernel

def VG2(dist_aPSF3D, STEP, SIZE, EDENS_IMG, rlim, voxel_griding=5, source_griding=3, disable_tqdm=False):
    """
    Performs voxel gridding (VG) to compute a 3D PSF kernel in heterogeneous media.

    Parameters:
        dist_aPSF3D (function): Function that calculates the PSF value given a distance r
        STEP (list): Voxel dimensions in cm [dx, dy, dz] in cm
        SIZE (list): Kernel size in voxels [nx, ny, nz]
        EDENS_IMG (numpy.ndarray): 3D array of electronic density values in cm^-3
        rlim (tuple): (rmin, rmax) Range of distances to consider in cm
        voxel_griding (int): Number of samples within each voxel
        source_griding (int): Number of samples within the source voxel

    Returns:
        numpy.ndarray: Normalized 3D PSF kernel
    """
    if EDENS_IMG.ndim != 3 or EDENS_IMG.shape != tuple(SIZE):
        raise ValueError("DENS_IMG must be a 3D array with the same shape as SIZE.")
    if voxel_griding % 2 == 0:
        voxel_griding += 1  # Ensure voxel_griding is odd
        print("voxel_griding is changed to", voxel_griding)
    if source_griding % 2 == 0:
        source_griding += 1
        print("source_griding is changed to", source_griding)
    if len(STEP) != 3 or len(SIZE) != 3:
        raise ValueError("STEP and SIZE must be lists of length 3.")
    if len(rlim) != 2:
        raise ValueError("rlim must be a tuple of length 2.")

    rmin, rmax = rlim
    rmin = max(rmin, 1e-9)  # Ensure rmin is not zero
    RMAX = max(STEP)*max(SIZE)/2 #* 3**0.5
    rmax = RMAX if rmax is None or rmax > RMAX else rmax    # Ensure rmax is within reasonable bounds

    dx, dy, dz = STEP
    nx, ny, nz = SIZE
    aPSF_kernel = np.zeros((nx, ny, nz), dtype=np.float32)

    # Check size is odd
    if nx % 2 == 0 or ny % 2 == 0 or nz % 2 == 0:
        raise ValueError("Kernel sizes must be odd to properly place the source voxel.")

    # Load iterators to save memory
    voxel_indices = ((ix, iy, iz) for ix in range(nx) for iy in range(ny) for iz in range(nz))
    voxel_centers = (((ix-nx//2)*dx, (iy-ny//2)*dy, (iz-nz//2)*dz) for ix in range(nx) for iy in range(ny) for iz in range(nz))

    # Grid points in source voxel
    grid_source = [np.linspace(0, step/2, 1+source_griding//2) for step in STEP]  # Only positive to always start at 0
    grid_source = [np.sort(np.concat((-g[1:], +g), dtype=np.float32)) for g in grid_source]         # Include negative values

    # Loop over all voxels in kernel and grid them
    for (ix,iy,iz), (cx,cy,cz) in tqdm(zip(voxel_indices, voxel_centers), total=nx*ny*nz, disable=disable_tqdm):
      grid_xyz = np.linspace((cx-dx/2, cy-dy/2, cz-dz/2), (cx+dx/2, cy+dy/2, cz+dz/2), voxel_griding)
      x,y,z = np.meshgrid(grid_xyz[:, 0], grid_xyz[:, 1], grid_xyz[:, 2], indexing='ij')
      eden = EDENS_IMG[ix, iy, iz]

      # Loop over all sampled source points and eval aPSF3D(r)
      for (sx, sy, sz) in itertools.product(*grid_source):
        r = np.sqrt((x-sx)**2 + (y-sy)**2 + (z-sz)**2) 
        mask = (r >= rmin) & (r <= rmax)
        psf = dist_aPSF3D(r/eden*10) * mask  # Scale distance by electronic density and convert to mm
        aPSF_kernel[ix, iy, iz] += psf.sum()

    aPSF_kernel /= aPSF_kernel.sum()    
    return aPSF_kernel


def voxel_traversal(start, end, voxel_size, grid_origin=(0, 0, 0)):
    """
    Calculates the distance a line segment travels through each voxel.

    Parameters:
        start: tuple of floats (x0, y0, z0) - start point in world coords
        end:   tuple of floats (x1, y1, z1) - end point in world coords
        voxel_size: tuple (dx, dy, dz)
        grid_origin: tuple (ox, oy, oz) - world coord of voxel (0,0,0)

    Returns:
        List of ((i, j, k), distance_inside_voxel)
    """
    start = np.array(start, dtype=np.float64)
    end = np.array(end, dtype=np.float64)
    direction = end - start
    length = np.linalg.norm(direction)
    if length == 0:
        return []

    direction /= length  # Normalize the direction vector

    # Voxel size and origin
    voxel_size = np.array(voxel_size, dtype=np.float64)
    origin = np.array(grid_origin, dtype=np.float64)

    # Convert to voxel coordinates
    voxel_start = np.floor((start - origin) / voxel_size).astype(int)
    voxel_end = np.floor((end - origin) / voxel_size).astype(int)

    current = voxel_start.copy()

    step = np.sign(direction).astype(int)

    # Compute tMax and tDelta
    voxel_boundary = origin + (current + (step > 0)) * voxel_size
    t_max = (voxel_boundary - start) / direction
    t_delta = voxel_size / np.abs(direction)
    t_max[np.isinf(t_max)] = np.inf
    t_delta[np.isinf(t_delta)] = np.inf

    result = []
    t = 0.0
    max_t = length

    while all((step > 0) * (current <= voxel_end) + (step < 0) * (current >= voxel_end)):
        # Find next axis to cross
        axis = np.argmin(t_max)
        next_t = t_max[axis]

        travel_distance = min(next_t, max_t) - t
        if travel_distance > 0:
            result.append((tuple(current), travel_distance))

        if next_t > max_t:
            break

        current[axis] += step[axis]
        t = next_t
        t_max[axis] += t_delta[axis]

    return result