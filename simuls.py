import numpy as np
import time
import subprocess

class MasterSimulator:
    active_simulators = dict()

    @staticmethod
    def _runSim_chrono(comm, cwd):
        #import psutil
        t_cpu = 0
        t_real = time.perf_counter()
        out, err = subprocess.Popen(comm, shell=True, cwd=cwd, stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE).communicate()
        t_real -= time.perf_counter()
        return out, err, abs(t_real), abs(t_cpu)

    def __init__(self, verbose=False):
        self.verbose = verbose

    @classmethod
    def simulate(cls, pid:str, get_times:bool, time_samples=5, output_dir="RESULTS", final_file=None):
        # get simulator object
        if pid not in cls.active_simulators.keys():
            raise ValueError(f"Simulator with pid {pid} is not active")
        else:
            self = cls.active_simulators[pid]

        # setup
        runs = time_samples if get_times else 1
        sim_times = np.zeros((runs,2))                      # 2 columns: real-time and CPU-time
        
        # create output directory if it doesn't exist
        if not subprocess.os.path.exists(output_dir):    
            subprocess.os.mkdir(output_dir)

        # get output file's name and format
        if not final_file:
            final_file = f"{output_dir}/{self.pid}.{self.output_format}"
        else:
            final_file = f"{output_dir}/{final_file}.{self.output_format}"                         

        # run simulations and get timings
        for run in range(runs):
            _, _, t, _ = cls._runSim_chrono(self.simul_command, self.simul_dir)
            sim_times[run,0] = t
            sim_times[run,1] = None # psutil.Process().cpu_times().user doesnt work
        
        # export results
        subprocess.run(f"mv {self.output_file} {final_file}", shell=True)

        # show timing statistics and save them if wanted
        print(f"{self.name} real time: {np.mean(sim_times[:,0]):.3f} +- {np.std(sim_times[:,0]):.3f} s")
        #print(f"{program_name} CPU time: {np.mean(sim_times[:,1]):.3f} +- {np.std(sim_times[:,1]):.3f} s")
        if get_times:
            file_times = f"{output_dir}/{self.pid}_times.txt"
            with open(file_times, 'a') as f:        # append mode
                np.savetxt(f, sim_times, fmt='%.3f')
        
        # return output file's location and sim_times
        return final_file, sim_times 
    
    @classmethod
    def simulate_all(cls, suffix:str=""):
        log = open("log.txt", 'w')
        for self in cls.active_simulators.values():
            log.write("//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////\n")
            log.write(f"//////////////////                                     {self.name} simulation - init                              ///////////////////////////////\n")
            log.write("//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////\n")               
            
            out, err, t, _ = cls._runSim_chrono(self.simul_command, self.simul_dir)
            log.write(out.decode('utf-8'))
            log.write(err.decode('utf-8'))
            
            output_file = f"RESULTS/{self.pid + suffix}.{self.output_format}"
            subprocess.run(f"cp {self.output_file} {output_file}", shell=True)
            
            print(f"{self.name} simulation finished in {t:.2f} sec")
        log.close()
    

class SlaveSimulator:
    def __init__(self, pid:str, name:str, bash_dir:str, simul_dir:str, simul_command:str, output_file:str, output_format:str):
        self.pid = pid                       # program ID
        self.name = name                     # name of the program or configuration
        self.bash_dir = bash_dir             # directory where bash scripts are located
        self.simul_dir = simul_dir           # directory where the executable is located
        self.simul_command = simul_command   # command to run simulation within its folder
        self.output_file = output_file       # relative path to the output file
        self.output_format = output_format   # raw (binary) or dat (ascii)


class PenEasy(MasterSimulator):
    available_pids = ['MOD', # modified, accelerated version of penEasy
                      'SPC', # original penEasy with external emission spectrum
                      'NUC'  # original penEasy with internal emission spectrum (nuclear decay simulation)
                      ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
    
    def activate_pid(self, pid:str):
        pid = pid.upper()
        if pid not in PenEasy.available_pids:
            raise ValueError(f"Invalid pid {pid}. Available pids are {PenEasy.available_pids}")

        bash_dir = "penEasy"
        simul_dir = "penEasy" 
        name = f"penEasy {pid}"
        match pid:
            case 'MOD': # modified, accelerated version of penEasy
                simul_command = "./modified.x<modified.in"
                output_file = "penEasy/image_out.raw"
                output_format = "raw"
            
            case 'SPC' | 'NUC': # original penEasy with external/internal emission spectrum (external file with spectrum/nuclear decay simulation)
                simul_command = f"./run_normal.sh {pid.lower()}"
                output_file = "penEasy/PosRange.dat"
                output_format = "dat"

        slave = SlaveSimulator(pid, name, bash_dir, simul_dir, simul_command, output_file, output_format)
        MasterSimulator.active_simulators[pid] = slave
        if self.verbose:
            print(f"{name} activated")

class PeneloPET(MasterSimulator):
    available_pids = ['PET20', # bug in the emission spectrum is present
                      'PET24', # bug in the emission spectrum is fixed
                     ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
    
class HybridMC(MasterSimulator):
    available_pids = ['HYB',   # HybridMC simulation
                     ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
    
class GATE(MasterSimulator):
    available_pids = ['G70',   # GATE 7.0beta
                      'vG92',  # vGATE 9.2
                      'vG93',  # vGATE 9.3
                    #   'G94',   # GATE 9.4
                    #   'G100',  # GATE 10.0
                     ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)

    def activate_pid(self, pid:str):
        pid = pid.upper()
        if pid not in GATE.available_pids:
            raise ValueError(f"Invalid pid {pid}. Available pids are {GATE.available_pids}")

        bash_dir = "gate"
        simul_dir = "gate" 
        name = pid
        match pid:
            case 'GATE70':
                pass