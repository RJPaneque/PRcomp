import numpy as np

def RMSE(a, b):
    """Root Mean Square Error"""
    return np.sqrt(np.mean((a-b)**2))

def MAE(a, b):
    """Mean Absolute Error"""
    return np.mean(np.abs(a-b))

def MAPE(a_got, a_exp):
    """Mean Absolute Percentage Error"""
    return np.mean(np.abs((a_got-a_exp)/a_exp)) * 100

def Deviation(a_got, a_exp):
    """Deviation"""
    if a_got.ndim == 0:
        a_got = np.array([a_got])
    if a_exp.ndim == 0:
        a_exp = np.array([a_exp])
    
    dev = (a_got - a_exp) * 100
    mask = (a_exp != 0)
    dev[~mask] = 0
    dev[mask] /= a_exp[mask]
    return dev

def MSE(a, b):
    """Mean Square Error"""
    return np.mean((a-b)**2)

def R2(a, b):
    """R^2 score"""
    ss_res = np.sum((a-b)**2)
    ss_tot = np.sum((a-np.mean(a))**2)
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

def Chi2(a, b):
    """Chi-squared test"""
    return np.sum((a-b)**2 / b) if np.sum(b) != 0 else 0

def Chi2_red(a, b):
    """Reduced Chi-squared test"""
    return Chi2(a, b) / (len(a) - 1) if len(a) > 1 else 0
    
def FWHM(x, y):
    """Full Width at Half Maximum"""
    half_max = y.max() / 2
    peak_idx = np.argmax(y)

    # find left crossing
    iL = np.where(y[:peak_idx] < half_max)[0][-1]
    iLp = iL + 1
    xL = x[iL] + (half_max - y[iL]) * (x[iLp] - x[iL]) / (y[iLp] - y[iL])

    # find right crossing
    iR = peak_idx + np.where(y[peak_idx:] < half_max)[0][0]
    iRp = iR - 1
    xR = x[iRp] + (half_max - y[iRp]) * (x[iR] - x[iRp]) / (y[iR] - y[iRp])

    fwhm = xR - xL
    return fwhm