import lmfit
import numpy as np
import sympy as sp
from scipy.special import gamma

from IPython.display import display
import warnings
warnings.filterwarnings('ignore')
sp.init_printing()

x = sp.symbols('x')
class FitG3D:
    def __init__(self, sympy_function, constants:dict, params:dict, name:str):
        self.name = name

        self.params = list(params.keys())  # variable parameters to fit
        self.init_params = [_[0] for _ in params.values()]  # initial values for the parameters
        self.bounds = [_[1] for _ in params.values()]  # bounds for the parameters
        self.consts = constants         # constant parameters
        
        self.spG3D = sympy_function # G3D
        self.spg3D = sp.diff(sympy_function, x)  # g3D
        self.spaPSF3D = self.spg3D / x**2 # aPSF3D
        
        self.fitted_params = None
        self.fitted_params_err = None
        self.residual = None
        self.chi2 = None
        self.rmse = None
        self.stderr = None

    def fit(self, xdata, ydata, rmin=0.0):
        ydata = ydata[xdata > rmin]
        xdata = xdata[xdata > rmin]
        G3D = self.spG3D.subs(self.consts)
        npG3D = sp.lambdify([x,*self.params], G3D, 'numpy')

        model = lmfit.Model(npG3D)
        params = lmfit.Parameters()
        for i, p in enumerate(self.params):
            params.add(str(p), value=self.init_params[i], min=self.bounds[i][0], max=self.bounds[i][1])
        
        results = model.fit(ydata, params, x=xdata)
        popt = [results.best_values[str(p)] for p in self.params]
        perr = [results.params[str(p)].stderr for p in self.params]
        self.fitted_params = popt
        self.fitted_params_err = list(map(lambda _: 0 if _ is None else _, perr))

        # residual computation
        self.residual = np.sqrt(np.sum((npG3D(xdata, *popt) - ydata)**2))
        self.rmse = self.residual / np.sqrt(len(ydata))

        # chi2 computation
        eps = 1e-10
        denom = ydata
        denom = np.where(denom < eps, eps, denom)
        self.chi2 = (npG3D(xdata, *popt) - ydata)**2 / denom
        self.chi2 = np.sum(self.chi2)
        self.stderr = np.sqrt(self.chi2 / (len(xdata) - len(self.params)))

        return self.residual, self.chi2
    
    def get_params(self, redon=2, with_err=True):
        params_rounded = [round(p, redon) for p in self.fitted_params]
        if with_err:
            err_rounded = [round(e, redon) for e in self.fitted_params_err]
            pzip = zip(map(float, params_rounded), 
                       map(float, err_rounded))
        else:
            pzip = map(float, params_rounded)
        dict_params = dict(zip(self.params, pzip))
                        
        return dict_params
    
    def show_info(self, redon=2):
        print(f'Fit {self.name}:')
        G3D = self.spG3D.subs(self.consts)
        dict_params = self.get_params(redon, with_err=False)
        expr_rounded = G3D.subs(dict_params)
        display(G3D)
        display(expr_rounded)
        print(f"{dict_params=}")
        print(f"{self.residual=:.4f}\t{self.chi2=:.4f}")
        print() 
    
    def get_G3D(self):
        all_params = {**self.consts, **self.get_params(redon=6, with_err=False)}
        G3D = self.spG3D.subs(all_params)
        G3D = sp.lambdify(x, G3D, 'numpy')
        return G3D

    def get_g3D(self):
        all_params = {**self.consts, **self.get_params(redon=6, with_err=False)}
        g3D = self.spg3D.subs(all_params)
        g3D = sp.lambdify(x, g3D, 'numpy')
        return g3D
    
    def get_aPSF3D(self):
        all_params = {**self.consts, **self.get_params(redon=6, with_err=False)}
        aPSF3D = self.spaPSF3D.subs(all_params)
        aPSF3D = sp.lambdify(x, aPSF3D, 'numpy')
        return aPSF3D
    
def MBfit_function(*weights, n_is_const=False):
    """
    Define the multi-branch fitting function.
    Parameters:
        weights (list): List of weights for each branch (in %).
    Returns:
        fit_func (FitG3D): Fitting function object.
    """
    if sum(weights) != 100:
        raise ValueError("Weights must sum to 100")
    argsP = []
    argsC = []
    spf = 1
    for i, w in enumerate(weights, 1):
        a, b, c, n = sp.symbols(f'a{i} b{i} c{i} n{i}')
        argsP += [a, b, c]
        if n_is_const:
            argsC += [n]
        else:
            argsP += [n]
        
        f = (a*x)**n + (b*x)**2.5 + (c*x)**3.5
        spf = spf - w*1e-2*sp.exp(-f)
    
    params = dict.fromkeys(argsP, (0.4, [0, None]))
    for i in range(1, len(weights)+1):
        n = sp.symbols(f'n{i}')
        if n in argsP: params[n] = (1, [1.001, 2])
    const = dict.fromkeys(argsC, 1)

    fit_func = FitG3D(spf, const, params, str(spf))
    return fit_func, argsP, argsC

############################################################################################################
def load_sample(input_file):
    sample = np.loadtxt(input_file)
    if sample.ndim == 1:
        pass
    elif sample.ndim == 2:
        sample = np.sqrt(np.sum(sample**2, axis=1))
    else:
        print("Invalid input file")
    return sample
    
############################################################################################################
def load_nonhisto_G3D(input_file):
    sample = load_sample(input_file)

    s = len(sample)
    sample_sorted = np.sort(sample)
    G3D_sort = np.arange(1,s+1)/s
    return sample_sorted, G3D_sort

def load_nonhisto_g3D(input_file, tol=1e-6):    # default tol in cm
    sample_sorted, G3D_sort = load_nonhisto_G3D(input_file)

    thin_sample = np.arange(0, sample_sorted[-1], tol)
    thin_G3D = np.interp(thin_sample, sample_sorted, G3D_sort)
    rp = thin_sample[:-1] + np.diff(thin_sample)/2  # mid points

    rdiff = np.diff(thin_sample)
    Gdiff = np.diff(thin_G3D)
    
    g3D_sort = Gdiff / rdiff
    g3D_sort = g3D_sort / g3D_sort.max()
    return rp, g3D_sort

def load_nonhisto_aPSF3D(input_file, tol=1e-6):
    rp, g3D_sort = load_nonhisto_g3D(input_file, tol)
    aPSF3D_sort = g3D_sort / rp**2
    aPSF3D_sort = aPSF3D_sort / aPSF3D_sort.max()
    return rp, aPSF3D_sort

############################################################################################################
def load_histo_g3D(input_file, bin_size=0.5):   # default bin_size in mm
    sample = load_sample(input_file)
        
    bins = np.arange(0, sample.max() + bin_size, bin_size)
    sample_histo, step = np.histogram(sample, bins=bins, density=True)  #g3D
    rp = step[:-1] + np.diff(step)/2
    g3D = sample_histo / sample_histo.max()
    return rp, g3D

def load_histo_aPSF3D(input_file, bin_size=0.5):
    rp, g3D = load_histo_g3D(input_file, bin_size)
    aPSF3D = g3D / rp**2
    aPSF3D = aPSF3D / aPSF3D.max() #/ np.diff(rp)[0]
    return rp, aPSF3D

def load_histo_G3D(input_file, bin_size=0.5):
    rp, g3D = load_histo_g3D(input_file, bin_size)
    g3D = g3D / g3D.sum()
    G3D = np.cumsum(g3D)
    return rp, G3D

############################################################################################################
from betaplus import MB, SB, Fermi_factor, shape_factor
def halflife_values(iso):
    match iso:
        case "C11":   hl = 20.3 * 60  # Convert minutes to seconds
        case "N13":   hl = 9.97 * 60   # Convert minutes to seconds
        case "O15":   hl = 2.03 * 60   # Convert minutes to seconds
        case "F18":   hl = 109.8 * 60  # Convert minutes to seconds
        case "Cu64":  hl = 12.7 * 3600 # Convert hours to seconds
        case _: hl = None
    return hl

def coulomb_effect(iso, branch=0):
    if iso in SB.keys():
        Z = SB[iso]['Z']
        A = SB[iso]['A']
        N = A - Z
        nat, Q, Em, _ = SB[iso]['branches'][branch]
    elif iso in MB.keys():
        Z = MB[iso]['Z']
        A = MB[iso]['A']
        N = A - Z
        nat, Q, Em, _ = MB[iso]['branches'][branch]
    else:
        raise ValueError(f"Undefined isotope: {iso}")
    
    ee = np.linspace(1e-10, Em, 100)
    ff = Fermi_factor(Z, ee)
    nc = (N-Z)**2/A * np.mean(ff)
    return [1+nc]
    # return [max(N/Z, N/Z + (N-Z)/(N+Z))]
    # Qa = 23.7*(N-Z+1)/A
    # Qp = 11.2/A**0.5 if (Z%2 == N%2) else 0
    # Qc = 0.691 / A**(1/3) * (Z*(Z-1) - (Z-1)*(Z-2))
    # Qp = Q + Qa - Qc
    # print(f"{iso}: {Q=}, {Qa=}, {Qp=}, {Qc=}")

    # R = 1.26*(A)**(1/3)
    # RZ = 1.26*(Z)**(1/3)
    # hc = 197.327
    # return [1 + Z/N * Em*R/hc]