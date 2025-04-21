import numpy as np
from scipy.special import gamma

alpha = 1 / 137.035999084   # Fine structure constant
hc = 197.3269804            # MeV·fm
mc2 = 0.51099895            # Electron mass at rest (MeV)

def Fermi_factor(_Z, _E):
    """
    Calculate the Fermi function for beta spectrum correction
    
    Parameters:
    Z (int): Atomic number of daughter nucleus
    E (float): Kinetic energy of beta particle in MeV
    
    Returns:
    float: Fermi function value F(Z,E)
    """
    # Determine particle momentum and beta
    W = _E + mc2
    p = np.sqrt(W**2 - mc2**2)
    beta = p / W

    # Sommerfeld parameter
    eta = -_Z * alpha / beta

    # Relativistic correction (S)
    S = np.sqrt(1 - (alpha * _Z)**2)

    # Nuclear radius (fm)
    abplus = -1.9 + 1.96*_Z + 0.0079*_Z**2 - 0.00002*_Z**3
    R = (1.123*abplus**(1/3)-0.941/abplus**(1/3))/hc

    # Gove-Martin approximation
    gamma_term = abs(gamma(S + 1j * eta))**2
    exponential_term = np.exp(np.pi * eta)
    prefactor = (2 * (1 + S)) / (gamma(1 + 2 * S)**2)
    radial_term = (2 * p * R / hc)**(2 * S - 2)

    # Final Fermi function
    F = prefactor * radial_term * exponential_term * gamma_term
    return F

def shape_factor(_nature, _Z, _A, _Q, _E):
    """
    Calculate the shape factor for beta decay.
    
    Parameters:
    nature (str): Nature of the decay -> 'allowed, 'first-forbidden', 'first-forbidden unique'
    Z (int): Atomic number of the daughter nucleus
    A (int): Mass number of the daughter nucleus
    Q (float): Q value of the beta decay (in MeV)
    E (float): Kinetic energy of the beta particle (in MeV)
    
    Returns:
    S (float): Shape factor value
    """
    # Calculate shape factor
    p = np.sqrt(_E**2 + 2*_E*mc2)
    q = _Q - _E
    Lambda = 1.0
    phi = 5   # factor to define (a >> b) as (a > phi*b)
    SchopperCriterion = lambda __Z, __A, __Emax: __Z/137 >  phi * (1.26 * __A**(1/3) * __Emax / hc)
    match _nature:
        case 'allowed':
            S = 1.0
        case 'first-forbidden unique':
            S = q**2 + Lambda * p**2 
        case 'first-forbidden':
            if SchopperCriterion(_Z, _A, _Q):   # Can be considered as allowed
                S = 1.0     
            else:
                raise ValueError("Cannot find a valid shape factor for this transition.")
        case _:
            raise ValueError("Invalid nature of decay. Choose among 'allowed', 'first-forbidden' or 'first-forbidden unique'.")
    return S

def beta_spectrum(_Q, _Z, _A, _nature='allowed'):
    """
    Calculate the beta spectrum for a given Q value and Z value.
    
    Parameters:
    _Q (float): The Q value of the beta decay (in keV).
    _Z (int): The atomic number of the decaying nucleus.
    _A (int): The mass number of the decaying nucleus.
    _nature (str): The nature of the decay ('allowed', 'first-forbidden', 'first-forbidden unique').
    
    Returns:
    tuple:
        - E (numpy.ndarray): The kinetic energy of the beta particle (in MeV).
        - N (numpy.ndarray): The normalized beta spectrum.
        - N0 (numpy.ndarray): The normalized beta spectrum without Fermi and shape factors.
    """
    # Init
    E = np.arange(1e-10, _Q, 1) # keV
    mc2keV = mc2 * 1e3 # MeV to keV

    # Calculate the beta spectrum without Coulomb correction
    N0 = np.sqrt(E**2 + 2*E*mc2keV) * (_Q - E)**2 * (E + mc2keV)
    
    # Coulomb correction using Fermi factor
    F = Fermi_factor(_Z-1, E*1e-3)
    S = shape_factor(_nature, _Z-1, _A, _Q*1e-3, E*1e-3) 
    N = N0*F*S
    return E, N/N.sum(), N0/N0.sum()


### Isotopes ###
Ga68branches = [   
    # Nature     Q(keV)  E(keV)  Weight 
     ('allowed',  821,    352,    1.4e-2),
     ('allowed', 1899,    836,   98.6e-2),
]

Rb82branches = [
    # Nature     Q(keV)  E(keV)  Weight
     ('allowed', 2605,   1169,   13.6e-2 + 0.7e-2),   # Add remianing branches 
     ('allowed', 3382,   1536,   85.7e-2),
]

I124branches = [
    # Nature                    Q(keV)  E(keV)  Weight
     ('first-forbidden',         812,    367,    1.3e-2 + 0.1e-2),   # Add remaining branches
     ('first-forbidden',        1535,    687,   51.5e-2),
     ('first-forbidden unique', 2138,    974,   47.1e-2),
]

MB = {
    'Ga68': {
        'Z': 31,
        'A': 68,
        'branches': Ga68branches,
    },
    'Rb82': {
        'Z': 37,
        'A': 82,
        'branches': Rb82branches,
    },
    'I124': {
        'Z': 53,
        'A': 124,
        'branches': I124branches,
    },
}

SB = {
    'C11': {
        'Z': 6,
        'A': 11,
        'branches': [('allowed',  960,    385,     1.0)],
    },
    'N13': {
        'Z': 7,
        'A': 13,
        'branches': [('allowed',  1198,   492,     1.0)],
    },
    'O15': {
        'Z': 8,
        'A': 15,
        'branches': [('allowed',  1732,   735,     1.0)],
    },
    'F18': {
        'Z': 9,
        'A': 18,
        'branches': [('allowed',  633,    250,     1.0)],
    },
    'Cu64': {
        'Z': 29,
        'A': 64,
        'branches': [('allowed',  653,    278,     1.0)],
    },
}