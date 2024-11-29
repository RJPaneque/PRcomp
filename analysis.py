# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

class PRAnalysis:
    def __init__(self, label:str, file:str, SIZE:list[int], STEP:list[float],  raw_format='float32'): 	# vox_size in cm
        """vox_size and data from file in cm"""
        self.label = label

        self.NX, self.NY, self.NZ = SIZE
        self.dx, self.dy, self.dz = STEP #cm

        self.dr = np.sqrt(self.dx**2 + self.dy**2 + self.dz**2)

        self.Xmax = self.NX*self.dx/2
        self.Ymax = self.NY*self.dy/2
        self.Zmax = self.NZ*self.dz/2
        self.Rmax = np.sqrt(self.Xmax**2 + self.Ymax**2 + self.Zmax**2)

        self.aPSFx_range = (np.arange(0, self.NX) - self.NX // 2) * self.dx
        self.aPSFy_range = (np.arange(0, self.NY) - self.NY // 2) * self.dy
        self.aPSFz_range = (np.arange(0, self.NZ) - self.NZ // 2) * self.dz

        """---------------------------------------------------
        ------LOAD  AND PROCESS DATA------
        ---------------------------------------------------"""
        match file.split('.')[-1]:  # file extension
            case 'dat':
                ##LOAD ANNIHILATION COORDS (in cm)
                data = np.loadtxt(file)     # !!!!! MUST BE CENTERED AT 0,0,0 !!!!!
                self.xp = data[:, 0]
                self.yp = data[:, 1]
                self.zp = data[:, 2]
                
                ##PROCESS
                self.dpoints = data.shape[0]        # number of 3D points
                self.dsize= self.dpoints            # size of the sample
                
                #get img from coords  
                self.img = np.zeros((self.NX, self.NY, self.NZ))
                Xp = np.floor(self.xp/self.dx + self.NX/2).astype(int)         # x -> i = floor(x/self.dx + NX/2)
                Yp = np.floor(self.yp/self.dy + self.NY/2).astype(int)
                Zp = np.floor(self.zp/self.dz + self.NZ/2).astype(int)
                for t in range(self.dpoints):
                    if Xp[t] >= self.NX or Yp[t] >= self.NY or Zp[t] >= self.NZ or \
                       Xp[t] < 0 or Yp[t] < 0 or Zp[t] < 0:
                        continue    # dont consider points beyond the image

                    self.img[Xp[t], Yp[t], Zp[t]] += 1
                
                #get normalised aPSF
                self.aPSFx = np.histogram(self.xp, bins=self.NX, range=[-self.Xmax, self.Xmax])[0].astype('float64')
                self.aPSFy = np.histogram(self.yp, bins=self.NY, range=[-self.Ymax, self.Ymax])[0].astype('float64')
                self.aPSFz = np.histogram(self.zp, bins=self.NZ, range=[-self.Zmax, self.Zmax])[0].astype('float64')

            case 'raw':
                ##LOAD
                with open(file, 'rb') as f:
                    raw_data = np.fromfile(f, dtype=raw_format)
                self.img = np.reshape(raw_data, (self.NX, self.NY, self.NZ))
                
                ##PROCESS
                self.dpoints = len(self.img[self.img > 0])
                self.dsize= np.sum(self.img, dtype=np.intc)
                
                #get coords from img  
                coor = np.zeros((self.dsize, 3))
                n = 0
                for ijk in np.argwhere(self.img>0)[:]:
                    r = int(self.img[ ijk[0], ijk[1], ijk[2] ])  # number of counts in voxel ijk
                    coor[n:n+r,:] = np.repeat([ijk], r, axis=0)  # repeat ijk row number-of-counts times
                    n += r                                       # update index for coords
                self.xp = (coor[:,0]-self.NX//2)*self.dx         # i -> x = (i - NX//2)*self.dx
                self.yp = (coor[:,1]-self.NY//2)*self.dy
                self.zp = (coor[:,2]-self.NZ//2)*self.dz
                
                #get normalised aPSF
                self.aPSFx = np.sum(np.sum(self.img, 2), 1).astype('float64')
                self.aPSFy = np.sum(np.sum(self.img, 2), 0).astype('float64')
                self.aPSFz = np.sum(np.sum(self.img, 1), 0).astype('float64')
            case _:
                raise FileNotFoundError("Used a not considered file format. Please use raw or dat.")

        # normalise aPSF   
        self.aPSFx /= np.sum(self.aPSFx)
        self.aPSFy /= np.sum(self.aPSFy)
        self.aPSFz /= np.sum(self.aPSFz)

        # aPSF_sin
        self.aPSFx_sin = self.aPSFx / np.max(self.aPSFx)
        self.aPSFy_sin = self.aPSFy / np.max(self.aPSFy)
        self.aPSFz_sin = self.aPSFz / np.max(self.aPSFz)

        ##MORE PROCESSING
        #radial distance traveled
        self.rp = np.sqrt(self.xp**2 + self.yp**2 + self.zp**2) # cm

        #maxima reached
        self.rmax = np.max(self.rp)     # cm
        self.xmax = np.max(self.xp)
        self.ymax = np.max(self.yp)
        self.zmax = np.max(self.zp)

        #radial stuff (normalised)
        rrange = np.arange(0, self.rmax, self.dr)
        self.rplot = rrange[:-1] + self.dr/2
        #---radial annihilation distribution: g3D(r) = 4pi r^2 * aPSF3D(r)
        self.g3D = np.histogram(self.rp, bins=rrange)[0]
        self.g3D = self.g3D / np.sum(self.g3D)
        #---cumulative radial annihilation distribution: G3D(r) = int_0^r g3D(r') dr'
        self.G3D = np.cumsum(self.g3D) 
        #---radial annihilation Point Spread Function: aPSF3D(r)
        self.aPSF3D	= self.g3D / self.rplot**2
        self.aPSF3D = self.aPSF3D / np.sum(self.aPSF3D)
        self.aPSF3D_sin = self.aPSF3D / np.max(self.aPSF3D)

        #---cummulative radial distribution without histograms: G3D(r) = (i+1)/N for i=0..N-1
        self.rsort = np.sort(self.rp)
        self.G3D_nohist = np.arange(1, self.dsize+1)/self.dsize

    def interpol_G3D(self, val):
        """Interpolates the value of G3D(r) for a given results object"""
        x1 = self.rplot[self.G3D<val][-1]
        y1 = self.G3D[self.G3D<val][-1]
        x2 = self.rplot[self.G3D>val][0]
        y2 = self.G3D[self.G3D>val][0]

        return x1 + (x2-x1)*(val-y1)/(y2-y1)
    

class GetResults:
    def _filterResults(self, labels):
        if not labels:
            results = self.active_results
        else:
            try:
                results = {label: self.active_results[label] for label in labels}
            except KeyError:
                raise KeyError(f"Please use programs that are available: {self.active_results.keys()}")
        return results

    def _singleFigurePlot(self, QoI, 
                          lim:float,    # lim in mm
                          log_scale:bool, 
                          title:str, 
                          xlabel:str, ylabel:str,
                          labels:list[str]=None, 
                          sin:bool=False, 
                          legend_size:int=9, 
                          sublabels:dict[str]=None):    
        results = self._filterResults(labels)

        match QoI:
            case 'aPSFx':
                xQoI = 'result.aPSFx_range'
                yQoI = 'result.aPSFx_sin' if sin else 'result.aPSFx'
                if not lim: 
                    mlim, Mlim = None, None
                else:
                    mlim, Mlim = -lim, lim
            case 'aPSF3D':
                xQoI = 'result.rplot'
                yQoI = 'result.aPSF3D_sin' if sin else 'result.aPSF3D'
                mlim, Mlim = 0, lim
            case 'g3D':
                xQoI = 'result.rplot'
                yQoI = 'result.g3D'
                mlim, Mlim = 0, lim
            case 'G3D':
                xQoI = 'result.rplot'
                yQoI = 'result.G3D'
                mlim, Mlim = 0, lim
            case 'G3D_nohist':
                xQoI = 'result.rsort'
                yQoI = 'result.G3D_nohist'
                mlim, Mlim = 0, lim
            case _:
                raise ValueError("Please use a valid QoI: aPSFx, aPSF3D, g3D, G3D")


        #plt.figure()
        for label, result in results.items():
            if sublabels:
                label = sublabels[label]
            plt.plot(eval(xQoI+'*10'), eval(yQoI), label=label) # *10 to convert to mm
        
        if log_scale: plt.yscale('log')
        if lim: plt.xlim([mlim, Mlim])
        plt.legend(prop={'size': legend_size})
        plt.title(title)
        plt.xlabel(xlabel); plt.ylabel(ylabel)
        #plt.show()

    def __init__(self, verbose=False): 	
        self.verbose = verbose
        self.active_results = dict()
    
    def load(self, label:str, file:str, vox_num:list[int], vox_size:list[float],  raw_format='float32'):    # vox_size in cm
        result = PRAnalysis(label, file, vox_num, vox_size, raw_format)
        self.active_results.update({label:result})
        if self.verbose:
            print(f"{label} loaded")

    def remove(self, label:str):
        if label in self.active_results.keys():
            self.active_results.pop(label)
            if self.verbose:
                print(f"{label} removed")
        elif self.verbose:
            print(f"{label} has not been loaded")
    
    def data_analysis(self, labels=None):
        """Prints relevant information on all active results"""
        results = self._filterResults(labels)

        print("Size of annihilations sample:")
        for label, result in results.items():
            print(f"     {label:<15} {result.dsize:>10}")

        print("Number of annihilation point coords:")
        for label, result in results.items():
            print(f"     {label:<15} {result.dpoints:>10}")

        print("Maximum radial distance traveled simulated:")
        for label, result in results.items():
            print(f"     {label:<15} {result.rmax*10:>10.2f} mm")

        print("Average radial distance traveled simulated:")
        for label, result in results.items():
            print(f"     {label:<15} {np.mean(result.rp)*10:>10.2f} mm")

        print("Cummulative distances:")
        for label, result in results.items():
            print(f"     {label:<15} 50% @ {result.interpol_G3D(0.5)*10:>3.2f}mm\t90% @ {result.interpol_G3D(0.9)*10:.2f}mm")

    def plot_meanZ(self, 
                   reduce=False, 
                   labels=None, 
                   sublabels=None):
        # reduce every count >=1 to 1 for better images
        # else recover them for not reloading previous sections
        results = self._filterResults(labels)

        plt.figure(figsize=(32,6))
        cols = 3 
        rows = len(results)//rows + len(results)%2
        k = 0
        for label, result in results.items():
            if sublabels:
                label = sublabels[label]
            img = result.img.copy()
            if reduce:      
                img[img>0]=1

            plt.subplot(rows, cols, k:=k+1)     # subplot number previous-k-plus-1   
            plt.imshow(np.mean(result.img, axis=2))
            plt.title("{}: {}mean z".format(label, "reduced " if reduce else ""))
            plt.xlabel("x (voxel)")
            plt.ylabel("y (voxel)")
            plt.colorbar()

        plt.show()

    def plot_aPSFx(self, 
                   sin:bool, 
                   lim:float=None, 
                   log_scale=True,
                   legend_size:int=9, 
                   title=None, 
                   labels=None, 
                   sublabels=None):    
        title = "annihilation Point Spread Function along x axis"  if not title else title
        xlabel = "x (mm)"
        ylabel = r"$aPSF_{sin}(x)$" if sin else r"$aPSF(x)$"
        self._singleFigurePlot('aPSFx', lim, log_scale, title, xlabel, ylabel, labels=labels, sin=sin, legend_size=legend_size, sublabels=sublabels)

    def plot_aPSF3D(self, 
                    sin:bool, 
                    lim:float=None, 
                    log_scale=True,
                    labels=None, 
                    title=None, 
                    legend_size:int=9, 
                    sublabels=None):    
        title = "annihilation Point Spread Function along radial distance"  if not title else title
        xlabel = "r (mm)"
        ylabel = r"$aPSF_{3Dsin}(r)$" if sin else r"$aPSF_{3D}(r)$"
        self._singleFigurePlot('aPSF3D', lim, log_scale, title, xlabel, ylabel, labels=labels, sin=sin, legend_size=legend_size, sublabels=sublabels)

    def plot_g3D(self, lim:float=None, 
                 log_scale=True,          
                 labels=None, 
                 title=None, 
                 legend_size:int=9, 
                 sublabels=None):   
        title = "radial annihilation distribution"  if not title else title
        xlabel = "r (mm)"
        ylabel = r"$g_{3D}(r)$"
        self._singleFigurePlot('g3D', lim, log_scale, title, xlabel, ylabel, labels=labels, legend_size=legend_size, sublabels=sublabels)

    def plot_G3D(self, 
                 lim:float=None, 
                 labels=None, 
                 title=None, 
                 legend_size:int=9, 
                 sublabels=None):   
        title = "Cummulative radial annihilation distribution" if not title else title
        xlabel = "r (mm)"
        ylabel = r"$G_{3D}(r)$"
        self._singleFigurePlot('G3D', lim, False, title, xlabel, ylabel, labels=labels, legend_size=legend_size, sublabels=sublabels)

    def plot_G3D_nohist(self, 
                        lim:float=None,
                        labels=None, 
                        title=None, 
                        legend_size:int=9, 
                        sublabels=None):    
        title = "Cummulative radial annihilation distribution" if not title else title
        xlabel = "r (mm)"
        ylabel = r"$G_{3D}(r)$"
        self._singleFigurePlot('G3D_nohist', lim, False, title, xlabel, ylabel, labels=labels, legend_size=legend_size, sublabels=sublabels)


def filter_rmax(file_in, file_out, threshold=100, trim:int=None, fmt='%.6e'):   # threshold in mm
    if file_in == file_out:
        raise ValueError("Input and output files must be different for security reasons")
    
    a = np.loadtxt(file_in)*10  #mm
    if a.shape[1] != 3:
        raise ValueError("Input file should have 3 columns")
    r = np.sqrt(np.sum(a**2, axis=1))
    a = a[r < threshold, :]
    if trim < len(a):
        a = a[:trim]
    np.savetxt(file_out, a/10, fmt=fmt)
    print(f"Filtered '{file_in}' to '{file_out}': {np.sum(r>threshold)} points removed")
    return