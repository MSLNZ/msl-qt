"""Unicode characters.

```pycon
>>> from msl.qt import DEGREE_C, PLUS_MINUS
>>> f"The temperature is 21.4 {PLUS_MINUS} 0.5 {DEGREE_C}"
'The temperature is 21.4 ± 0.5 ℃'

```
"""

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
"""[str][] &mdash; Degree character."""

DEGREE_C = "\u2103"
"""[str][] &mdash; Degree Centigrade character."""

DEGREE_F = "\u2109"
"""[str][] &mdash; Degree Fahrenheit character."""

INFINITY = "\u221e"
"""[str][] &mdash; Infinity character."""

MICRO = "\u00b5"
"""[str][] &mdash; Micro character."""

PLUS_MINUS = "\u00b1"
"""[str][] &mdash; Plus-minus character."""


class GREEK(Enum):
    """Greek characters.

    Attributes:
        Alpha (str): "\u0391"
        Beta (str): "\u0392"
        Gamma (str): "\u0393"
        Delta (str): "\u0394"
        Epsilon (str): "\u0395"
        Zeta (str): "\u0396"
        Eta (str): "\u0397"
        Theta (str): "\u0398"
        Iota (str): "\u0399"
        Kappa (str): "\u039a"
        Lambda (str): "\u039b"
        Mu (str): "\u039c"
        Nu (str): "\u039d"
        Xi (str): "\u039e"
        Omicron (str): "\u039f"
        Pi (str): "\u03a0"
        Rho (str): "\u03a1"
        Sigma (str): "\u03a3"
        Tau (str): "\u03a4"
        Upsilon (str): "\u03a5"
        Phi (str): "\u03a6"
        Chi (str): "\u03a7"
        Psi (str): "\u03a8"
        Omega (str): "\u03a9"
        alpha (str): "\u03b1"
        beta (str): "\u03b2"
        gamma (str): "\u03b3"
        delta (str): "\u03b4"
        epsilon (str): "\u03b5"
        zeta (str): "\u03b6"
        eta (str): "\u03b7"
        theta (str): "\u03b8"
        iota (str): "\u03b9"
        kappa (str): "\u03ba"
        lambda_ (str): "\u03bb"
        mu (str): "\u03bc"
        nu (str): "\u03bd"
        xi (str): "\u03be"
        omicron (str): "\u03bf"
        pi (str): "\u03c0"
        rho (str): "\u03c1"
        sigmaf (str): "\u03c2"
        sigma (str): "\u03c3"
        tau (str): "\u03c4"
        upsilon (str): "\u03c5"
        phi (str): "\u03c6"
        chi (str): "\u03c7"
        psi (str): "\u03c8"
        omega (str): "\u03c9"
        thetasym (str): "\u03d1"
        upsih (str): "\u03d2"
        straightphi (str): "\u03d5"
        piv (str): "\u03d6"
        Gammad (str): "\u03dc"
        gammad (str): "\u03dd"
        varkappa (str): "\u03f0"
        varrho (str): "\u03f1"
        straightepsilon (str): "\u03f5"
        backepsilon (str): "\u03f6"
    """

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
