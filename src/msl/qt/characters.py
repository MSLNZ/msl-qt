"""Unicode characters."""

from __future__ import annotations

from enum import Enum

__all__: list[str] = [
    "DEGREE",
    "DEGREE_C",
    "DEGREE_F",
    "GREEK",
    "INFINITY",
    "MICRO",
    "PLUS_MINUS",
]

DEGREE = "\u00b0"
"""Degree character."""

DEGREE_C = "\u2103"
"""Degree Centigrade character."""

DEGREE_F = "\u2109"
"""Degree Fahrenheit character."""


class GREEK(Enum):
    """Greek characters."""

    Alpha = "\u0391"
    Beta = "\u0392"
    Gamma = "\u0393"
    Delta = "\u0394"
    Epsilon = "\u0395"
    Zeta = "\u0396"
    Eta = "\u0397"
    Theta = "\u0398"
    Iota = "\u0399"
    Kappa = "\u039a"
    Lambda = "\u039b"
    Mu = "\u039c"
    Nu = "\u039d"
    Xi = "\u039e"
    Omicron = "\u039f"
    Pi = "\u03a0"
    Rho = "\u03a1"
    Sigma = "\u03a3"
    Tau = "\u03a4"
    Upsilon = "\u03a5"
    Phi = "\u03a6"
    Chi = "\u03a7"
    Psi = "\u03a8"
    Omega = "\u03a9"
    alpha = "\u03b1"
    beta = "\u03b2"
    gamma = "\u03b3"
    delta = "\u03b4"
    epsilon = "\u03b5"
    zeta = "\u03b6"
    eta = "\u03b7"
    theta = "\u03b8"
    iota = "\u03b9"
    kappa = "\u03ba"
    lambda_ = "\u03bb"
    mu = "\u03bc"
    nu = "\u03bd"
    xi = "\u03be"
    omicron = "\u03bf"
    pi = "\u03c0"
    rho = "\u03c1"
    sigmaf = "\u03c2"
    sigma = "\u03c3"
    tau = "\u03c4"
    upsilon = "\u03c5"
    phi = "\u03c6"
    chi = "\u03c7"
    psi = "\u03c8"
    omega = "\u03c9"
    thetasym = "\u03d1"
    upsih = "\u03d2"
    straightphi = "\u03d5"
    piv = "\u03d6"
    Gammad = "\u03dc"
    gammad = "\u03dd"
    varkappa = "\u03f0"
    varrho = "\u03f1"
    straightepsilon = "\u03f5"
    backepsilon = "\u03f6"


INFINITY = "\u221e"
"""Infinity character."""

MICRO = "\u00b5"
"""Micro character."""

PLUS_MINUS = "\u00b1"
"""Plus-minus character."""
