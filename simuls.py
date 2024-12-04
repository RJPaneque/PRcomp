import numpy as np
import time
import subprocess
from dataclasses import dataclass

class HostSimulator:
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
        elif "." not in final_file:
            final_file = f"{output_dir}/{final_file}.{self.output_format}"  
        else:
            final_file = f"{output_dir}/{final_file}"                       

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
    

@dataclass
class GuestSimulator:
    pid : str           # program ID
    name : str          # name of the program or configuration
    bash_dir : str      # directory where bash scripts are located
    simul_dir : str     # directory where the executable is located
    simul_command : str # command to run simulation within its folder
    output_file : str   # relative path to the output file
    output_format : str # raw (binary) or dat (ascii)


class PenEasy(HostSimulator):
    available_pids = ['MOD', # modified, accelerated version of penEasy
                      'SPC', # original penEasy with external emission spectrum
                      'NUC'  # original penEasy with internal emission spectrum (nuclear decay simulation)
                      ]
    
    available_vers = ['20',  # penEasy 2020
                      '24',  # penEasy 2024
                      ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
    
    def activate_pid(self, pid:str, ver:str):
        pid = pid.upper()
        if pid not in PenEasy.available_pids:
            raise ValueError(f"Invalid pid {pid}. Available pids are {PenEasy.available_pids}")
        if ver not in PenEasy.available_vers:
            raise ValueError(f"Invalid version {ver}. Available versions are {PenEasy.available_vers}")
        
        if pid == 'MOD' and ver != '20':
            raise ValueError(f"Modified code of PenEasy is only available for version 2020")

        match pid:
            case 'MOD': # modified, accelerated version of penEasy
                simul_command = f"./pen{ver}mod.x<pen{ver}mod.in"
                output_file = "penEasy/image_out.raw"
                output_format = "raw"
            
            case 'SPC' | 'NUC': # original penEasy with external/internal emission spectrum (external file with spectrum/nuclear decay simulation)
                simul_command = f"./run_normal.sh {pid.lower()} {ver}"
                output_file = "penEasy/annihilation.dat"
                output_format = "dat"

        guest = GuestSimulator(
            pid=pid, 
            name=f"penEasy 20{ver} {pid}", 
            bash_dir="penEasy",
            simul_dir="penEasy", 
            simul_command=simul_command, 
            output_file=output_file, 
            output_format=output_format
            )
        
        HostSimulator.active_simulators[pid] = guest
        if self.verbose:
            print(f"{guest.name} activated")

class PeneloPET(HostSimulator):
    available_pids = ['2020', # bug in the emission spectrum is present
                      '2024', # bug in the emission spectrum is fixed
                     ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)

    def activate_pid(self, pid:str):
        pid = pid.upper()
        if pid not in PeneloPET.available_pids:
            raise ValueError(f"Invalid pid {pid}. Available pids are {PeneloPET.available_pids}")

        match pid:
            case '2020': # PeneloPET 2020 with bug in the emission spectrum
                simul_command = "./penelopet_2020.x main"
            case '2024': # PeneloPET 2024 with fixed bug in the emission spectrum
                simul_command = "./penelopet_2024_R.x main"

        guest = GuestSimulator(
            pid=pid, 
            name=f"PeneloPET {pid}", 
            bash_dir="penelopet",
            simul_dir="penelopet/work", 
            simul_command=simul_command, 
            output_file="penelopet/work/main/annihilation.dat", 
            output_format="dat"
            )
        
        HostSimulator.active_simulators[pid] = guest
        if self.verbose:
            print(f"{guest.name} activated")
    
class HybridMC(HostSimulator):
    available_pids = ['HYB',   # HybridMC simulation
                     ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
    
class GATE(HostSimulator):
    available_pids = ['7',   # GATE 7.0beta
                      '9',   # vGATE 9.x
                    #   '10',  # GATE 10.0
                     ]
    
    def __init__(self, verbose=False):
        super().__init__(verbose)

    def activate_pid(self, pid:str, output_format:str):
        pid = pid.upper()
        if pid not in GATE.available_pids:
            raise ValueError(f"Invalid pid {pid}. Available pids are {GATE.available_pids}")
        
        match output_format:
            case 'dat':
                output_file = "gate/output/annihilation.dat"
            case 'raw':
                output_file = "gate/output/Image-Stop.raw"
            case _:
                raise ValueError(f"Invalid format {pid}. Available pids are {GATE.available_pids}")

        match pid:
            case '7': # GATE 7.0beta on fistensor
                simul_file = "PR_GATEv7.mac"
            case '9': # virtual GATE 9.2 on my Windows
                simul_file = "PR_GATEv9.mac"


        guest = GuestSimulator(
            pid=pid, 
            name=f"GATE {pid}", 
            bash_dir="gate",
            simul_dir="gate", 
            simul_command=f"./run_gate.sh {simul_file}", 
            output_file=output_file, 
            output_format=output_format
            )
        
        HostSimulator.active_simulators[pid] = guest
        if self.verbose:
            print(f"{guest.name} activated")