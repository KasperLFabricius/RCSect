import numpy as np


class ConcreteType1:
    """Legacy PCROSS concrete family type 1.

    Compression is positive on the material side. Tension is ignored (0 MPa).
    The first-phase recreation keeps the legacy-type-1 parabola/plateau form used
    by the benchmark corpus:
      - 0 <= eps < eps_c2: parabolic stress rise
      - eps_c2 <= eps <= eps_cu2: constant design compression stress
      - eps > eps_cu2: crushed concrete (0 MPa)

    Parameters:
      - fck: characteristic compression strength [MPa]
      - gamma_c: material safety factor for concrete
      - alpha_cc: coefficient on concrete design strength
    """

    def __init__(self, fck: float = None, gamma_c: float = 1.45, alpha_cc: float = 1.0, f_ck: float = None):
        if fck is None:
            fck = f_ck
        if fck is None:
            raise ValueError("ConcreteType1 requires fck or f_ck")
        self.f_ck = fck
        self.fck = fck
        self.gamma_c = gamma_c
        self.alpha_cc = alpha_cc
        self.f_cd = self.alpha_cc * self.fck / self.gamma_c

        if self.fck <= 50.0:
            self.eps_c2 = 2.0 / 1000.0
            self.eps_cu2 = 3.5 / 1000.0
            self.n = 2.0
        else:
            self.eps_c2 = (2.0 + 0.085 * (self.fck - 50.0) ** 0.53) / 1000.0
            self.eps_cu2 = (2.6 + 35.0 * ((90.0 - self.fck) / 100.0) ** 4) / 1000.0
            self.n = 1.4 + 23.4 * ((90.0 - self.fck) / 100.0) ** 4

    def stress(self, eps: np.ndarray) -> np.ndarray:
        eps = np.asarray(eps)
        sigma = np.zeros_like(eps, dtype=float)

        mask_parabola = (eps >= 0.0) & (eps < self.eps_c2)
        sigma[mask_parabola] = self.f_cd * (
            1.0 - (1.0 - eps[mask_parabola] / self.eps_c2) ** self.n
        )

        mask_rect = (eps >= self.eps_c2) & (eps <= self.eps_cu2)
        sigma[mask_rect] = self.f_cd

        sigma[eps > self.eps_cu2] = 0.0
        return sigma


class MildSteelType1:
    """Legacy PCROSS mild steel family type 1.

    Inputs follow PCROSS-style naming:
      - fytk, fyck: characteristic yield strength in tension/compression [MPa]
      - futk: characteristic ultimate strength [MPa]
      - eut: characteristic ultimate strain [-]
      - gamma_y, gamma_u, gamma_E: safety factors for yield/ultimate/modulus

    Design values:
      - E_d = E_k / gamma_E
      - f_yd_t = fytk / gamma_y ; f_yd_c = fyck / gamma_y
      - f_ud_t = futk / (gamma_y * gamma_u) ; same for compression magnitude
      - eps_ud = 0.9 * eut / gamma_u
    """

    def __init__(
        self,
        *,
        fytk: float,
        fyck: float | None = None,
        eut: float,
        futk: float | None = None,
        E_modulus: float = 200000.0,
        gamma_y: float = 1.15,
        gamma_u: float = 1.0,
        gamma_E: float = 1.0,
        include_hardening: bool = False,
    ):
        self.fytk = fytk
        self.fyck = fytk if fyck is None else fyck
        self.eut = eut
        self.futk = futk if futk is not None else fytk
        self.gamma_y = gamma_y
        self.gamma_u = gamma_u
        self.gamma_E = gamma_E
        self.include_hardening = include_hardening

        self.E_k = E_modulus
        self.E_s = self.E_k / self.gamma_E

        self.f_yd_t = self.fytk / self.gamma_y
        self.f_yd_c = self.fyck / self.gamma_y
        self.eps_yd_t = self.f_yd_t / self.E_s
        self.eps_yd_c = self.f_yd_c / self.E_s

        self.f_ud_t = self.futk / (self.gamma_y * self.gamma_u)
        self.f_ud_c = self.futk / (self.gamma_y * self.gamma_u)
        self.eps_ud = 0.9 * self.eut / self.gamma_u

        # backward compatibility aliases
        self.gamma_s = self.gamma_y
        self.f_yk = self.fytk
        self.f_yk_t = self.fytk
        self.f_yk_c = self.fyck

    def stress(self, eps: np.ndarray) -> np.ndarray:
        eps = np.asarray(eps)
        abs_eps = np.abs(eps)
        sigma = np.zeros_like(eps, dtype=float)

        mask_t = eps >= 0.0
        mask_c = ~mask_t

        mask_el_t = mask_t & (eps <= self.eps_yd_t)
        mask_el_c = mask_c & (abs_eps <= self.eps_yd_c)
        sigma[mask_el_t] = eps[mask_el_t] * self.E_s
        sigma[mask_el_c] = eps[mask_el_c] * self.E_s

        mask_y_t = mask_t & (eps > self.eps_yd_t) & (eps <= self.eps_ud)
        mask_y_c = mask_c & (abs_eps > self.eps_yd_c) & (abs_eps <= self.eps_ud)

        if self.include_hardening:
            slope_t = 0.0 if self.eps_ud == self.eps_yd_t else (self.f_ud_t - self.f_yd_t) / (self.eps_ud - self.eps_yd_t)
            slope_c = 0.0 if self.eps_ud == self.eps_yd_c else (self.f_ud_c - self.f_yd_c) / (self.eps_ud - self.eps_yd_c)
            sigma[mask_y_t] = self.f_yd_t + slope_t * (eps[mask_y_t] - self.eps_yd_t)
            sigma[mask_y_c] = -(self.f_yd_c + slope_c * (abs_eps[mask_y_c] - self.eps_yd_c))
        else:
            sigma[mask_y_t] = self.f_yd_t
            sigma[mask_y_c] = -self.f_yd_c

        sigma[abs_eps > self.eps_ud] = 0.0
        return sigma


class PrestressedSteelType1:
    """Legacy PCROSS prestressed steel family type 1.

    Phase-1 benchmark-needed representation:
      - IS controls characteristic modulus and characteristic strengths.
      - gamma_E reduces modulus (E_d = E_k / gamma_E).
      - gamma_y reduces 0.1%-proof/yield design level.
      - gamma_u reduces ultimate design stress and ultimate design strain.
    """

    def __init__(
        self,
        *,
        IS: float,
        gamma_y: float = 1.15,
        gamma_u: float = 1.0,
        gamma_E: float = 1.0,
        initial_strain: float = 0.0,
    ):
        self.IS = IS
        # Benchmark-needed assumptions for type-1 prestress family.
        if int(IS) == 1:
            self.f_p01k = 1500.0
            self.f_pk = 1700.0
            self.e_uk = 0.035
            self.E_k = 195000.0
        else:
            raise ValueError(f"Unsupported PrestressedSteelType1 IS={IS} in phase-1 scope")

        self.gamma_y = gamma_y
        self.gamma_u = gamma_u
        self.gamma_E = gamma_E
        self.gamma_s = gamma_y
        self.initial_strain = initial_strain

        self.E_p = self.E_k / self.gamma_E
        self.f_pd = self.f_p01k / self.gamma_y
        self.eps_pd = self.f_pd / self.E_p
        self.f_ud = self.f_pk / (self.gamma_y * self.gamma_u)
        self.eps_ud = 0.9 * self.e_uk / self.gamma_u

    def stress(self, total_eps: np.ndarray) -> np.ndarray:
        total_eps = np.asarray(total_eps)
        sigma = np.zeros_like(total_eps, dtype=float)
        abs_eps = np.abs(total_eps)
        sign_eps = np.sign(total_eps)

        mask_el = abs_eps <= self.eps_pd
        sigma[mask_el] = total_eps[mask_el] * self.E_p

        mask_y = (abs_eps > self.eps_pd) & (abs_eps <= self.eps_ud)
        sigma[mask_y] = sign_eps[mask_y] * self.f_pd

        sigma[abs_eps > self.eps_ud] = 0.0
        return sigma


class PrestressedSteelType6:
    """Legacy PCROSS prestressed steel family type 6.

    Inputs:
      - IS: legacy material subtype selector (phase-1 supports IS=6)
      - fytk, futk, eut, E_modulus: characteristic values
      - gamma_y, gamma_u, gamma_E: safety factors for yield/ultimate/modulus
    """

    def __init__(
        self,
        *,
        IS: float,
        fytk: float,
        futk: float,
        eut: float,
        E_modulus: float,
        gamma_y: float = 1.15,
        gamma_u: float = 1.0,
        gamma_E: float = 1.0,
        initial_strain: float = 0.0,
    ):
        if int(IS) != 6:
            raise ValueError(f"PrestressedSteelType6 expects IS=6, got {IS}")
        self.IS = IS
        self.fytk = fytk
        self.futk = futk
        self.eut = eut
        self.E_k = E_modulus
        self.gamma_y = gamma_y
        self.gamma_u = gamma_u
        self.gamma_E = gamma_E
        self.gamma_s = gamma_y
        self.initial_strain = initial_strain

        self.E_p = self.E_k / self.gamma_E
        self.f_pd = self.fytk / self.gamma_y
        self.eps_pd = self.f_pd / self.E_p
        self.f_ud = self.futk / (self.gamma_y * self.gamma_u)
        self.eps_ud = 0.9 * self.eut / self.gamma_u

    def stress(self, total_eps: np.ndarray) -> np.ndarray:
        total_eps = np.asarray(total_eps)
        sigma = np.zeros_like(total_eps, dtype=float)
        abs_eps = np.abs(total_eps)
        sign_eps = np.sign(total_eps)

        mask_elastic = abs_eps <= self.eps_pd
        sigma[mask_elastic] = total_eps[mask_elastic] * self.E_p

        mask_yield = (abs_eps > self.eps_pd) & (abs_eps <= self.eps_ud)
        if self.f_ud > self.f_pd and self.eps_ud > self.eps_pd:
            slope = (self.f_ud - self.f_pd) / (self.eps_ud - self.eps_pd)
            sigma[mask_yield] = sign_eps[mask_yield] * (
                self.f_pd + slope * (abs_eps[mask_yield] - self.eps_pd)
            )
        else:
            sigma[mask_yield] = sign_eps[mask_yield] * self.f_pd

        sigma[abs_eps > self.eps_ud] = 0.0
        return sigma


# Backward-compatibility aliases used by existing non-benchmark code/tests.
Concrete = ConcreteType1


class MildSteel(MildSteelType1):
    def __init__(
        self,
        f_yk: float,
        gamma_s: float = 1.20,
        E_s: float = 200000.0,
        gamma_E: float = 1.0,
        e_uk: float = 0.02,
        gamma_u: float = 1.0,
        f_uk: float = None,
        include_hardening: bool = False,
        f_yk_t: float = None,
        f_yk_c: float = None,
    ):
        super().__init__(
            fytk=f_yk if f_yk_t is None else f_yk_t,
            fyck=f_yk if f_yk_c is None else f_yk_c,
            eut=e_uk,
            futk=f_uk if f_uk is not None else f_yk,
            E_modulus=E_s,
            gamma_y=gamma_s,
            gamma_u=gamma_u,
            gamma_E=gamma_E,
            include_hardening=include_hardening,
        )


class PrestressedSteel(PrestressedSteelType6):
    def __init__(
        self,
        f_p01k: float,
        f_pk: float,
        e_uk: float,
        gamma_s: float = 1.20,
        E_p: float = 195000.0,
        initial_strain: float = 0.0,
        gamma_E: float = 1.0,
        gamma_u: float = 1.0,
    ):
        super().__init__(
            IS=6,
            fytk=f_p01k,
            futk=f_pk,
            eut=e_uk,
            E_modulus=E_p,
            gamma_y=gamma_s,
            gamma_u=gamma_u,
            gamma_E=gamma_E,
            initial_strain=initial_strain,
        )
        self.f_p01k = f_p01k
        self.f_pk = f_pk
        self.e_uk = e_uk
