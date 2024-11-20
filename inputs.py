import numpy as np
import subprocess
import simuls as Simulators

class InputEditor:
    def __init__(self, verbose=True):
        self.verbose = verbose

    def _run_bin(self, comms):
        result = subprocess.run(comms, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if not self.verbose: 
            return
        elif result.returncode == 0:
            print(result.stdout[:-1])
        else:
            print("ERROR")
            print(result.stderr[:-1])

    def get_newSource(self, shape:str, pos:list[float], radius:float, 
                           ACT:str, SIZE:list[int], STEP:list[float]):
        """Update source shape and activity in the phantom"""
        NXM, NYM, NZM = SIZE[0]//2+1, SIZE[1]//2+1, SIZE[2]//2+1
        yy, xx, zz = np.meshgrid(np.arange(-NXM+1, NXM)*STEP[0],
                                 np.arange(-NYM+1, NYM)*STEP[1],
                                 np.arange(-NZM+1, NZM)*STEP[2])
        bool_vol = np.zeros((SIZE[0], SIZE[1], SIZE[2]), dtype='bool')
        match shape.lower():
            case 'sphere':      # for radius 0 its a point
                bool_vol = np.sqrt((xx-pos[0])**2 + (yy-pos[1])**2 + (zz-pos[2])**2) <= radius
            case 'cylinder':    # cylinder of height=dimX*dx
                bool_vol = np.sqrt((yy-pos[1])**2 + (zz-pos[2])**2) <= radius
            case _:
                raise KeyError("shape not expected: only sphere or cylinder")
        ACTIVITY = bool_vol.astype('float32') * float(ACT)/np.sum(bool_vol)
        return ACTIVITY
    
    def get_newMaterial(self, MATS:dict, SIZE:list[int], STEP:list[float]): # material can be heterogenous: water, lung-water-bone, bone-water, ...
        """Update materials/densities {'mat name' : [mat id, mat index,density]} in the phantom"""
        NXM, NYM, NZM = SIZE[0]//2+1, SIZE[1]//2+1, SIZE[2]//2+1
        yy, xx, zz = np.meshgrid(np.arange(-NXM+1, NXM)*STEP[0],
                                 np.arange(-NYM+1, NYM)*STEP[1],
                                 np.arange(-NZM+1, NZM)*STEP[2])
        size_third = SIZE[0]*STEP[0]/3

        MATERIAL = np.ones((SIZE[0], SIZE[1], SIZE[2]), dtype='int32')
        DENSITY = np.ones((SIZE[0], SIZE[1], SIZE[2]), dtype='float32')

        mats_idx = [MATS[mat][1] for mat in MATS.keys()]
        dens = [MATS[mat][2] for mat in MATS.keys()]

        match len(MATS):
            case 1:    # homogeneous material
                MATERIAL[:,:,:] = mats_idx[0]
                DENSITY[:,:,:] = dens[0]
            case 2:    # heterogenous material of 2 halves in x axis
                #first half of x
                MATERIAL[xx<=0] = mats_idx[0]
                DENSITY[xx<=0] = dens[0]
                #second half of x
                MATERIAL[xx>0] = mats_idx[1]
                DENSITY[xx>0] = dens[1]
            case 3:    # heterogenous material of 3 thirds in x axis
                #set all voxels to first third
                MATERIAL[:,:,:] = mats_idx[0]
                DENSITY[:,:,:] = dens[0] 
                #overwrite two thirds (dont know why have to divide by 2)
                MATERIAL[xx>=-size_third/2] = mats_idx[1]
                DENSITY[xx>=-size_third/2] = dens[1]
                #overwrite last third
                MATERIAL[xx>=+size_third] = mats_idx[2]
                DENSITY[xx>=+size_third] = dens[2]
            case _:
                raise KeyError(f"There is no material distribution available for that much materials.")
        
        return MATERIAL, DENSITY
        

class PenEasy(InputEditor):
    def _make_vox(self, pid:str, SIZE:list[int], STEP:list[float]):
        # read material, density and activity files
        with open("penEasy/mat/MATERIAL.raw", 'rb') as f:
            raw_data_MAT = np.fromfile(f, dtype=np.int32)
        with open("penEasy/mat/DENSITY.raw", 'rb') as f:
            raw_data_DEN = np.fromfile(f, dtype=np.float32)
        with open("penEasy/mat/ACTIVITY.raw", 'rb') as f:
            raw_data_ACT = np.fromfile(f, dtype=np.float32)
        
        # only could called after having edited the phantom
        if pid in ['SPC', 'NUC']:
            MATERIAL = np.reshape(raw_data_MAT, SIZE)
            DENSITY = np.reshape(raw_data_DEN, SIZE)
            ACTIVITY = np.zeros(SIZE, dtype=np.float32) # not used in SPC, NUC

        # make sure the data is the same size
        elif pid == 'MOD':
            if np.prod(SIZE) == raw_data_MAT.size == raw_data_ACT.size:     # both MAT/DEN and ACT have been updated
                MATERIAL = np.reshape(raw_data_MAT, SIZE)
                DENSITY = np.reshape(raw_data_DEN, SIZE)
                ACTIVITY = np.reshape(raw_data_ACT, SIZE)

            elif np.prod(SIZE) == raw_data_MAT.size:    # only MAT/DEN has been updated -> ACT will later be updated
                MATERIAL = np.reshape(raw_data_MAT, SIZE)
                DENSITY = np.reshape(raw_data_DEN, SIZE)
                ACTIVITY = np.zeros(SIZE, dtype=np.float32)
            else:                                       # only ACT has been updated -> MAT/DEN will later be updated
                MATERIAL = np.zeros(SIZE, dtype=np.int32)
                DENSITY = np.zeros(SIZE, dtype=np.float32)
                ACTIVITY = np.reshape(raw_data_ACT, SIZE)

        # save voxel phantom
        data = np.column_stack([MATERIAL.reshape(MATERIAL.size),
                                ACTIVITY.reshape(ACTIVITY.size),
                                DENSITY.reshape(DENSITY.size)])

        # choose phantom.vox file
        # penEasy SPC, NUC (only material & density)
        if pid in ['SPC', 'NUC']:
            data[:,0] = 1   # to fit their inputs (they collapse if done as MOD)
            file = 'penEasy/phantomN.vox'
        
        # penEasy MOD (material, density, activity)
        elif pid == 'MOD':
            file = 'penEasy/phantom.vox'
        
        # save phantom.vox file
        with open(file, 'w') as fid:
            fid.write("[SECTION VOXELS HEADER v.2008-04-13] \n")
            fid.write(f" {SIZE[0]}     {SIZE[1]}      {SIZE[2]}     No. OF VOXELS IN X,Y,Z \n")
            fid.write(f" {STEP[0]:5.4f}  {STEP[1]:5.4f}  {STEP[2]:5.4f}    VOXEL SIZE (cm) ALONG X,Y,Z \n")
            fid.write(" 1                  COLUMN NUMBER WHERE MATERIAL ID IS LOCATED \n")
            fid.write(" 3                  COLUMN NUMBER WHERE THE MASS DENSITY IS LOCATED \n")
            fid.write(" 0                  BLANK LINES AT END OF X,Y-CYCLES (1=YES,0=NO) \n")
            fid.write("[END OF VXH SECTION] \n")
        with open(file, 'ab') as fid:
            np.savetxt(fid, data, fmt=" %d    %4.3f    %4.3f")

    def _get_voxData(self, pid:str):
        match pid:
            case 'MOD':
                phantom_file = 'penEasy/phantom.vox'
            case 'SPC' | 'NUC':
                phantom_file = 'penEasy/phantomN.vox'
            case _:
                raise KeyError(f"Voxel data can only be retrieved for pids {self.available_pids}")
        with open(phantom_file, 'r') as file:
            line1 = file.readline() # not used
            line2 = file.readline()
            line3 = file.readline()
        SIZE = [int(i) for i in line2.strip().split()[:3]]
        STEP = [float(i) for i in line3.strip().split()[:3]]
        return SIZE, STEP
    
    def __init__(self, verbose=True):
        super().__init__(verbose)
        # material info table (mat file name, mat id, mass density)
        self.MATS ={'water':    ['water', 1, 1.01130250E+00],    
                    'air':      ['air', 2, 1.21000000E-03],
                    'lung':     ['lung', 3, 4.80000000E-01],
                    'bone':     ['bone', 4, 1.87540000E+00]}
        
        self.available_pids = Simulators.PenEasy.available_pids

    def edit_isotope(self, pid:str, isotope:str):
        if pid not in self.available_pids:
            raise KeyError(f"Isotope can only be edited for pids {self.available_pids}")
        
        suff = 'nuc' if pid == 'NUC' else 'spc'    
        self._run_bin([f"./bin/penEasy/isotope_{suff}.sh", isotope])

    def edit_voxSize(self, pid:str, size:list[int], step:list[float]):
        if pid not in self.available_pids:
            raise KeyError(f"Voxel size can only be edited for pids {self.available_pids}")
        
        suff = 'modified' if pid == 'MOD' else 'normal' 
        self._run_bin([f"./bin/penEasy/resize_{suff}.sh", str(size[0]), str(size[2]), str(step[0]), str(step[2])])

    def edit_seed(self, pid:str, seed1:int=None, seed2:int=None):
        if pid not in self.available_pids:
            raise KeyError(f"Seed can only be edited for pids {self.available_pids}")
        
        if not seed1 or not seed2:
            seed1, seed2 = np.random.randint(0, 2**16 - 1, dtype=np.uint16, size=2)
        self._run_bin([f"./bin/penEasy/seeds.sh", str(seed1), str(seed2)])

    def edit_mat(self, pid:str, MATS:dict, SIZE:list[int], STEP:list[float]):
        """MATS = {'mat name' : [mat id, mat index, mass density]}"""
        if pid not in self.available_pids:
            raise KeyError(f"Material can only be edited for pids {self.available_pids}")
        if len(MATS) != 1 and pid in ['SPC', 'NUC']:
            raise KeyError(f"Heterogenous material edition cannot be done for pids SPC and NUC")
        
        # update material and density
        MATERIAL, DENSITY = self.get_newMaterial(MATS, SIZE, STEP) 
        DENSITY.tofile('penEasy/mat/DENSITY.raw', format="%f")
        MATERIAL.tofile('penEasy/mat/MATERIAL.raw', format="%d")
        self._make_vox(pid, SIZE, STEP)

        # update normal_spc/nuc.in files
        if pid in ['SPC', 'NUC']:
            mat_file = [_[0] for _ in MATS.items()][0]
            self._run_bin([f"./bin/penEasy/material_normal.sh", mat_file])

        if self.verbose:
            phantom_file = 'penEasy/phantom.vox' if pid == 'MOD' else 'penEasy/phantomN.vox'
            print(f"\"{phantom_file}\" updated to {'-'.join(list(MATS.keys()))} (case {len(MATS)})")
            
    def edit_source_shape(self, pid:str, shape:str, pos:list[float], radius:float, ACT:str, SIZE:list[int], STEP:list[float]):
        ##!!-ONLY VALID FOR PENEASY MOD-!!##
        if pid != 'MOD':
            raise KeyError("Source shape can only be edited for pid MOD")
        
        ACTIVITY = self.get_newSource(shape, pos, radius, ACT, SIZE, STEP)
        ACTIVITY.tofile('penEasy/mat/ACTIVITY.raw', format="%f")
        self._make_vox('MOD', SIZE, STEP)
        if self.verbose: 
            print(f"\"penEasy/phantom.vox\" updated to {shape} source with activity {ACT}")

    def edit_source_nhist(self, pid:str, nhist:str):
        current_size, current_step = self._get_voxData(pid)
        with open("penEasy/mat/ACTIVITY.raw", 'rb') as f:
            ACTIVITY = np.fromfile(f, dtype=np.float32)
        is_pointSource = np.sum(ACTIVITY>0) == 1

        match pid:
            case 'NUC' | 'SPC':
                if not is_pointSource:
                    raise KeyError("\"penEasy/mat/ACTIVITY.raw\" is not a point source so pids SPC and NUC are not valid. Please edit source shape first.")
                else:
                    self._run_bin([f"./bin/penEasy/nhist_normal.sh", nhist])
            case 'MOD':
                # update activity
                ACTIVITY[ACTIVITY>0] = float(nhist)/np.sum(ACTIVITY>0)
                ACTIVITY.tofile('penEasy/mat/ACTIVITY.raw', format="%f")
                # save phantom.vox file
                self._make_vox(pid, current_size, current_step)
            case _:
                raise KeyError(f"Source nhist can only be edited for pids {self.available_pids}")
            
        if self.verbose:
            if pid == 'MOD':
                print(f"\"penEasy/phantom.vox\" updated to a total activity of {nhist}")
            elif pid in ['SPC', 'NUC']:
                print(f"\"penEasy/phantomN.vox\" updated to point source of activity {nhist}")


class PeneloPET(InputEditor):
    def __init__(self, verbose=True):
        super().__init__(verbose)
        # material info table (mat name, mat id, mass density)
        self.MATS ={'water':    ['water', None, 1.01130250E+00],    
                    'air':      ['air', None,  1.21000000E-03],
                    'lung':     ['lung', None, 4.80000000E-01],
                    'bone':     ['bone_cor', None, 1.87540000E+00]}
        
        self.available_pids = Simulators.PeneloPET.available_pids

    def edit_isotope(self, pid:str, isotope:str):
        if pid not in self.available_pids:
            raise KeyError(f"Isotope can only be edited for pids {self.available_pids}")
        self._run_bin([f"./bin/penelopet/isotope.sh", isotope])

    def edit_seed(self, pid:str, seed1:int=None, seed2:int=None):
        if pid not in self.available_pids:
            raise KeyError(f"Seed can only be edited for pids {self.available_pids}")
        
        if not seed1 or not seed2:
            seed1, seed2 = np.random.randint(0, 2**16 - 1, dtype=np.uint16, size=2)
        self._run_bin([f"./bin/penelopet/seeds.sh", str(seed1), str(seed2)])
    
    def edit_mat(self, pid:str, MATS:dict):
        if pid not in self.available_pids:
            raise KeyError(f"Material can only be edited for pids {self.available_pids}")
        if len(MATS) != 1:
            raise KeyError(f"Heterogenous material edition is not implemented for PeneloPET")
        
        mat = [_[0] for _ in MATS.items()][0]
        self._run_bin([f"./bin/materialpenelopet.sh", mat])

    def edit_source_nhist(self, pid:str, nhist:str):
        if pid not in self.available_pids:
            raise KeyError(f"Source nhist can only be edited for pids {self.available_pids}")
        # Point source
        self._run_bin([f"./bin/penelopet/activity.sh", nhist])

        # Voxelized source (not used)
        with open("penelopet/work/main/source.raw", 'rb') as f:
            ACTIVITY = np.fromfile(f, dtype='float32')
        ACTIVITY[ACTIVITY>0] = float(nhist)/np.sum(ACTIVITY>0) * 1e3  #dont know why its reduced a factor of 1000
        ACTIVITY.tofile('penelopet/work/main/source.raw', format="%f")
        
        if self.verbose: 
            print(f"\"penelopet/work/main/source.raw\" updated to point source of activity {nhist}")


class Hybrid(InputEditor):
    def __init__(self, verbose=True):
        super().__init__(verbose)
        self.MATS ={'water':    [None, 6,   1.01130250E+00],    
                    'air':      [None, 1,   1.21000000E-03],
                    'lung':     [None, 2,   4.80000000E-01],
                    'bone':     [None, 23,  1.87540000E+00]}
        self.available_pids = Simulators.Hybrid.available_pids
        
    def edit_isotope(self, pid:str, isotope:str):
        if pid not in self.available_pids:
            raise KeyError(f"Isotope can only be edited for pids {self.available_pids}")
        
        self._run_bin([f"./bin/hybrid/isotope.sh", isotope])    

    def edit_voxSize(self, pid:str, size:list[int], step:list[float]):
        if pid not in self.available_pids:
            raise KeyError(f"Voxel size can only be edited for pids {self.available_pids}")
         
        self._run_bin([f"./bin/hybrid/resize.sh", str(size[0]), str(size[2]), str(step[0]), str(step[2])])

    def edit_seed(self, pid:str, seed1:int=None, seed2:int=None):
        if pid not in self.available_pids:
            raise KeyError(f"Seed can only be edited for pids {self.available_pids}")
        
        if not seed1 or not seed2:
            seed1, seed2 = np.random.randint(0, 2**16 - 1, dtype=np.uint16, size=2)
        self._run_bin([f"./bin/hybrid/seeds.sh", str(seed1), str(seed2)])

    def edit_mat(self, pid:str, MATS:dict, SIZE:list[int], STEP:list[float]):
        """MATS = {'mat name' : [mat index,density]}"""
        if pid not in self.available_pids:
            raise KeyError(f"Material can only be edited for pids {self.available_pids}")
        
        MATERIAL, DENSITY = self.get_newMaterial(MATS, SIZE, STEP)
        MATERIAL.tofile('hybrid/GEO/MATERIAL.raw', format="%d")
        DENSITY.tofile('hybrid/GEO/DENSITY.raw', format="%f")
        if self.verbose: 
            print(f"\"hybrid/GEO/MATERIAL.raw\" and \"hybrid/GEO/DENSITY.raw\" updated to {'-'.join(list(MATS.keys()))} (case {len(MATS)})")

    def edit_source_shape(self, pid:str, shape:str, pos:list[float], radius:float, ACT:str, SIZE:list[int], STEP:list[float]):
        if pid not in self.available_pids:
            raise KeyError(f"Source shape can only be edited for pids {self.available_pids}")
        
        ACTIVITY = self.get_newSource(shape, pos, radius, ACT, SIZE, STEP)
        ACTIVITY.tofile('hybrid/GEO/ACTIVITY.raw', format="%f")
        if self.verbose: 
            print(f"\"hybrid/GEO/ACTIVITY.raw\" updated to {shape} source with activity {ACT}")

    def edit_source_nhist(self, pid:str, nhist:str):
        if pid not in self.available_pids:
            raise KeyError(f"Source nhist can only be edited for pids {self.available_pids}")

        with open("hybrid/GEO/ACTIVITY.raw", 'rb') as f:
            ACTIVITY = np.fromfile(f, dtype='float32')
        ACTIVITY[ACTIVITY>0] = float(nhist)/np.sum(ACTIVITY>0)
        ACTIVITY.tofile("hybrid/GEO/ACTIVITY.raw", format="%f")
        if self.verbose: 
            print(f"\"hybrid/GEO/ACTIVITY.raw\" updated to source with total number of histories {nhist}")

    
class Gate(InputEditor):
    def __init__(self, verbose=True):
        super().__init__(verbose)
        # densities doesnt matter, but are needed
        self.MATS ={'water':    ['WaterTFM', 6, 1.01130250E+00],    
                    'air':      ['Air', 1,   1.21000000E-03],
                    'lung':     ['LungTFM', 2,   4.80000000E-01],
                    'bone':     ['BoneTFM', 23,  1.87540000E+00]}
        
        self.available_pids = Simulators.Gate.available_pids
        self.available_NUC_emission = self.available_pids.copy()
        self.available_NUC_emission.remove('G70')

    def switch_emission(self, pid:str, emis:str):
        if emis.upper() == 'NUC' and pid not in self.available_NUC_emission:
            raise KeyError(f"Mode NUC can only be edited for pids {self.available_NUC_emission}")
        
        self._run_bin([f"./bin/gate/switch_emission.sh", emis])

    def edit_isotope(self, pid:str, isotope:str):
        if pid not in self.available_pids:
            raise KeyError(f"Isotope can only be edited for pids {self.available_pids}")
        
        self._run_bin([f"./bin/gate/isotope.sh", isotope])

    def edit_voxSize(self, pid:str, size:list[int], step:list[float]):
        if pid not in self.available_pids:
            raise KeyError(f"Voxel size can only be edited for pids {self.available_pids}")
        
        self._run_bin([f"./bin/gate/resize.sh", str(size[0]), str(size[2]), str(step[0]), str(step[2])])

    def edit_seed(self, pid:str, seed1:int=None, seed2:int=None):
        if pid not in self.available_pids:
            raise KeyError(f"Seed can only be edited for pids {self.available_pids}")
        
        if not seed1 or not seed2:
            seed1, seed2 = np.random.randint(0, 2**16 - 1, dtype=np.uint16, size=2)
        self._run_bin([f"./bin/gate/seeds.sh", str(seed1), str(seed2)])
    
    def edit_mat(self, pid:str, MATS:dict, SIZE:list[int], STEP:list[float]):
        """MATS = {'mat name' : [mat id, mat index, mass density]}"""
        if pid not in self.available_pids:
            raise KeyError(f"Material can only be edited for pids {self.available_pids}")
        
        # update material and density
        MATERIAL, DENSITY = self.get_newMaterial(MATS, SIZE, STEP) 
        MATERIAL.astype('uint16').tofile('gate/phantom/MATERIAL.i33', format="%d")

        mats = [_[0] for _ in MATS.items()]
        self._run_bin([f"./bin/gate/materials.sh"] + mats)

    def edit_source_shape(self, pid:str, shape:str, pos:list[float], radius:float, ACT:str, SIZE:list[int], STEP:list[float]):
        if pid not in self.available_pids:
            raise KeyError(f"Source shape can only be edited for pids {self.available_pids}")
        
        if shape.lower() == 'sphere' and radius == 0:
            radius = 0.001  # cm
        ACTIVITY = self.get_newSource(shape, pos, radius, ACT, SIZE, STEP)
        ACTIVITY.tofile('gate/phantom/ACTIVITY.i33', format="%f")
        self._run_bin([f"./bin/gate/source.sh", shape])
    
    def edit_source_nhist(self, pid:str, nhist:str):
        if pid not in self.available_pids:
            raise KeyError(f"Simulation nhist can only be edited for pids {self.available_pids}")
        
        self._run_bin([f"./bin/gate/nhist.sh", nhist])
