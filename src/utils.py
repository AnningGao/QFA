import numpy as np
import torch


def MatrixInverse(M, D, device):
    """
    Efficient and stable matrix inverse function for matrix with structure:
    $$
        Matrix = MM^T + D
    $$
    Here M is a Npix x Nh matrix and D is a Npix x Npix diagonal matrix, usually Npix >> Nh
    ---------------------------------------------------------------
    Args:
        M (torch.tensor (shape=(Npix, Nh), dtype=torch.float32)): a Npix x Nh matrix
        D (torch.tensor (shape=(Npix, ), dtype=torch.float32)): the diagonal elements for D

    Returns:
        inverse matrix of MM^T + D
        shape: (Npix, Npix)
        dtype: torch.float32
    """
    _, Nh = M.shape
    diagD = torch.diag(1./D)
    I = torch.eye(Nh, dtype=torch.float32).to(device)
    return diagD - diagD@M@torch.linalg.inv(I+M.T@diagD@M)@M.T@diagD


def MatrixLogDet(M, D, device):
    """
    Efficient and stable matrix log determinant function for matrix with structure:
    $$
        Matrix = MM^T + D
    $$
    Here M is a Npix x Nh matrix and D is a Npix x Npix diagonal matrix, usually Npix >> Nh
    ---------------------------------------------------------------
    Args:
        M (torch.array (shape=(Npix, Nh), dtype=torch.float32)): a Npix x Nh matrix
        D (torch.array (shape=(Npix,   ), dtype=torch.float32)): the diagonal elements for D

    Returns:
        Log determinant for MM^T + D
        type: torch.float32
    """
    _, Nh = M.shape
    diagD = torch.diag(1./D)
    I = torch.eye(Nh, dtype=torch.float32).to(device)
    return torch.sum(torch.log(D)) + torch.log(torch.linalg.det(I+M.T@diagD@M))


def tauHI(z, tau0, beta):
    """
    Simple power law for effective optical depth of absorption systems
    $$
        tau(z) = tau0*(1+z)**beta
    $$
    -------------------------------------------------
    Args:
        z (torch.array (shape=(N, ), dtype=torch.float32)): redshift array
        tau0 (torch.float32): power law amplitude
        beta (torch.float32): power law index

    Returns:
        effective optical depth (torch.array (shape=(N, ), dtype=torch.float32))
    """
    return tau0*torch.pow((1.+z), beta)


def omega_func(z, tau0, beta, c0):
    """
    Absorption noise evolution function
    $$
        omega(z) = (1-tau0*(1+z)^beta-c0)**2
    $$
    ---------------------------------------------
    Args:
        z (torch.array (shape=(N, ), dtype=torch.float32)): redshift array
        tau0 (torch.float32): effective optical depth parameter
        beta (torch.float32): effective optical depth parameter
        c0 (torch.float32): bias term

    Returns:
        omega (torch.array (shape=(N, ), dtype=torch.float32)) : absorption noise redshift evolution
    """
    root = 1. - c0 - torch.exp(-1.*tauHI(z, tau0, beta))
    return root*root


def tau(z):
    """
    mean optical depth measured by ?
    ----------------------------------------------------------------------
    Args:
        z (torch.array (shape=(N, ), dtype=torch.float32)): redshift array

    Returns:
        effective optical depth: (torch.array (shape=(N, ), dtype=torch.float32))
    """
    tau0, beta, C, z0 = (0.751, 2.90, -0.132, 3.5)
    return tau0*((1+z)/(1+z0))**beta + C


def smooth(s, window_len=32):
    """Smooth curve s with corresponding window length

    Args:
        s (numpy.ndarray (shape: (N, ), dtype=float)): a 1d curve
        window_len (int, optional): smoothing window. Defaults to 32.

    Returns:
        smoothed curve (numpy.ndarray (shape: (N, ), dtype=float))
    """
    s = np.r_[s[window_len-1:0:-1], s, s[-2:-window_len-1:-1]]
    kernel = np.ones(window_len, dtype=float)/window_len
    y = np.convolve(kernel, s, mode='valid')
    return y[int(window_len/2-1):-int(window_len/2)]
