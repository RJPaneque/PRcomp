import numpy as np
import itertools
from tqdm import tqdm

def VG(dist_aPSF3D, STEP, SIZE, rlim, voxel_griding=5, source_griding=3, disable_tqdm=False):
    """
    Performs voxel gridding (VG) to compute a 3D PSF kernel.

    Parameters:
        dist_aPSF3D (function): Function that calculates the PSF value given a distance r
        STEP (list): Voxel dimensions in cm [dx, dy, dz] in mm
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
    for (ix,iy,iz), (cx,cy,cz) in tqdm(zip(voxel_indices, voxel_centers), total=nx*ny*nz//2, disable=disable_tqdm):
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