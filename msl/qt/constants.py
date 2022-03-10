"""
Package constants.
"""
import os
from enum import Enum

HOME_DIR = os.path.join(os.path.expanduser('~'), '.msl')
""":class:`str`: The default ``$HOME`` directory where all files used by the package are located."""

SI_PREFIX_MAP = {i: prefix for i, prefix in enumerate('yzafpn\u00b5m kMGTPEZY', start=-8)}
""":class:`dict`: The SI prefixes used to form multiples of 10**(3*n), n=-8..8"""

DEGREE = '\u00B0'
""":class:`str`: The degree symbol."""

DEGREE_C = '\u2103'
""":class:`str`: The degree Centigrade symbol."""

DEGREE_F = '\u2109'
""":class:`str`: The degree Fahrenheit symbol."""


class GREEK(Enum):
    """Greek letters."""
    Alpha = '\u0391'
    Beta = '\u0392'
    Gamma = '\u0393'
    Delta = '\u0394'
    Epsilon = '\u0395'
    Zeta = '\u0396'
    Eta = '\u0397'
    Theta = '\u0398'
    Iota = '\u0399'
    Kappa = '\u039A'
    Lambda = '\u039B'
    Mu = '\u039C'
    Nu = '\u039D'
    Xi = '\u039E'
    Omicron = '\u039F'
    Pi = '\u03A0'
    Rho = '\u03A1'
    Sigma = '\u03A3'
    Tau = '\u03A4'
    Upsilon = '\u03A5'
    Phi = '\u03A6'
    Chi = '\u03A7'
    Psi = '\u03A8'
    Omega = '\u03A9'
    alpha = '\u03B1'
    beta = '\u03B2'
    gamma = '\u03B3'
    delta = '\u03B4'
    epsilon = '\u03B5'
    zeta = '\u03B6'
    eta = '\u03B7'
    theta = '\u03B8'
    iota = '\u03B9'
    kappa = '\u03BA'
    lambda_ = '\u03BB'
    mu = '\u03BC'
    nu = '\u03BD'
    xi = '\u03BE'
    omicron = '\u03BF'
    pi = '\u03C0'
    rho = '\u03C1'
    sigmaf = '\u03C2'
    sigma = '\u03C3'
    tau = '\u03C4'
    upsilon = '\u03C5'
    phi = '\u03C6'
    chi = '\u03C7'
    psi = '\u03C8'
    omega = '\u03C9'
    thetasym = '\u03D1'
    upsih = '\u03D2'
    straightphi = '\u03D5'
    piv = '\u03D6'
    Gammad = '\u03DC'
    gammad = '\u03DD'
    varkappa = '\u03F0'
    varrho = '\u03F1'
    straightepsilon = '\u03F5'
    backepsilon = '\u03F6'
