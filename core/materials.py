import numpy as np


class ConcreteType1:
    """Legacy PCROSS concrete family type 1 (benchmark-needed diagram).

    Sign convention in this codebase:
    - material law input strain uses fraction form (e.g. 0.0035 == 0.35%)
    - compression is positive
    - tension carries zero stress

    Manual figure uses e in percent. We therefore convert with e_pct = 100*eps.
    Characteristic diagram:
      E0 = 51*f_c/(13+f_c)
      0 <= e < 0.2: f = 10*E0*e + 100*(3/4*f_c - E0)*e^2 + 250*(E0 - f_c)*e^3
      0.2 <= e < 0.35: f = f_c
    Design diagram is sigma = f / gamma_c.
    """

    def __init__(self, fck: float = None, gamma_c: float = 1.45, alpha_cc: float = 1.0, f_ck: float = None):
        if fck is None:
            fck = f_ck
        if fck is None:
            raise ValueError("ConcreteType1 requires fck or f_ck")

        self.fck = float(fck)
        self.f_ck = self.fck  # compatibility alias
        self.gamma_c = float(gamma_c)
        self.alpha_cc = float(alpha_cc)

        # Keep this compatibility attribute used in existing warnings/diagnostics.
        self.f_cd = self.alpha_cc * self.fck / self.gamma_c

        # Existing solver pivot logic uses these limits (fraction units).
        self.eps_c2 = 0.002
        self.eps_cu2 = 0.0035

    def stress(self, eps: np.ndarray) -> np.ndarray:
        eps_arr = np.asarray(eps, dtype=float)
        e_pct = 100.0 * eps_arr

        sigma = np.zeros_like(eps_arr, dtype=float)

        mask_cubic = (e_pct >= 0.0) & (e_pct < 0.2)
        if np.any(mask_cubic):
            E0 = 51.0 * self.fck / (13.0 + self.fck)
            e = e_pct[mask_cubic]
            f_char = (
                10.0 * E0 * e
                + 100.0 * ((0.75 * self.fck) - E0) * e**2
                + 250.0 * (E0 - self.fck) * e**3
            )
            sigma[mask_cubic] = (self.alpha_cc * f_char) / self.gamma_c

        mask_plateau = (e_pct >= 0.2) & (e_pct < 0.35)
        sigma[mask_plateau] = (self.alpha_cc * self.fck) / self.gamma_c

        # e_pct < 0 (tension) and e_pct >= 0.35 (crushed) stay at zero.
        return sigma


class MildSteelType1:
    """Legacy PCROSS mild reinforcement family type 1 (benchmark-needed diagram)."""

    def __init__(
        self,
        *,
        fytk: float,
        fyck: float,
        eut: float,
        futk: float,
        gamma_y: float,
        gamma_u: float,
        gamma_E: float,
        E_modulus: float = 2.0e5,
        include_hardening: bool = True,
    ):
        self.fytk = float(fytk)
        self.fyck = float(fyck)
        self.eut = float(eut)
        self.futk = float(futk)
        self.gamma_y = float(gamma_y)
        self.gamma_u = float(gamma_u)
        self.gamma_E = float(gamma_E)

        self.E_k = float(E_modulus)
        self.E_s = self.E_k / self.gamma_E

        self.f_yd_t = self.fytk / self.gamma_y
        self.f_yd_c = self.fyck / self.gamma_y
        self.eps_yd_t = self.f_yd_t / self.E_s
        self.eps_yd_c = self.f_yd_c / self.E_s

        # Design hardening endpoint per provided figure interpretation.
        self.f_ud_t = self.futk / self.gamma_u
        self.eps_ud = self.eut

        self.include_hardening = bool(include_hardening)

        # Compatibility aliases
        self.gamma_s = self.gamma_y
        self.f_yk = self.fytk
        self.f_yk_t = self.fytk
        self.f_yk_c = self.fyck

    def stress(self, eps: np.ndarray) -> np.ndarray:
        eps_arr = np.asarray(eps, dtype=float)
        sigma = np.zeros_like(eps_arr, dtype=float)

        # Tension side: elastic -> linear hardening to (eut, futk/gamma_u).
        mask_t = eps_arr >= 0.0
        if np.any(mask_t):
            e_t = eps_arr[mask_t]
            sigma_t = np.empty_like(e_t)

            mask_t_el = e_t <= self.eps_yd_t
            sigma_t[mask_t_el] = self.E_s * e_t[mask_t_el]

            mask_t_hard = ~mask_t_el
            if np.any(mask_t_hard):
                if self.eut > self.eps_yd_t:
                    slope = (self.f_ud_t - self.f_yd_t) / (self.eut - self.eps_yd_t)
                    e_h = np.minimum(e_t[mask_t_hard], self.eut)
                    sigma_t[mask_t_hard] = self.f_yd_t + slope * (e_h - self.eps_yd_t)
                else:
                    sigma_t[mask_t_hard] = self.f_yd_t

            sigma[mask_t] = sigma_t

        # Compression side: elastic -> constant -fyck/gamma_y.
        mask_c = eps_arr < 0.0
        if np.any(mask_c):
            e_c_abs = np.abs(eps_arr[mask_c])
            sigma_c = np.empty_like(e_c_abs)

            mask_c_el = e_c_abs <= self.eps_yd_c
            sigma_c[mask_c_el] = -self.E_s * e_c_abs[mask_c_el]
            sigma_c[~mask_c_el] = -self.f_yd_c
            sigma[mask_c] = sigma_c

        return sigma


class PrestressedSteelType1:
    """Legacy PCROSS prestressed steel family type 1 (figure-based).

    IS is initial prestress strain in percent from material input.
    Internal solver strain is fraction, so initial strain fraction is IS/100.

    Figure defines only tension side; compression is clamped to zero.
    Design stresses are characteristic ordinates divided by gamma_y.
    """

    RES_PCT = 3.5

    def __init__(
        self,
        *,
        IS: float,
        gamma_y: float,
        gamma_u: float = 1.0,
        gamma_E: float = 1.0,
    ):
        self.IS = float(IS)
        self.gamma_y = float(gamma_y)
        self.gamma_u = float(gamma_u)
        self.gamma_E = float(gamma_E)

        self.initial_strain = self.IS / 100.0

        # Compatibility attributes used elsewhere in diagnostics.
        self.E_p = 2.0e5 / self.gamma_E
        self.eps_ud = self.RES_PCT / 100.0
        self.gamma_s = self.gamma_y

    def stress(self, total_eps: np.ndarray) -> np.ndarray:
        eps_arr = np.asarray(total_eps, dtype=float)
        e_pct = 100.0 * eps_arr

        sigma = np.zeros_like(eps_arr, dtype=float)

        abs_e = np.abs(e_pct)
        sign_e = np.sign(e_pct)

        mask1 = (abs_e >= 0.0) & (abs_e < 0.6)
        sigma[mask1] = sign_e[mask1] * (2000.0 * abs_e[mask1]) / self.gamma_y

        mask2 = (abs_e >= 0.6) & (abs_e < 1.0)
        e = abs_e[mask2]
        sigma[mask2] = sign_e[mask2] * ((-2500.0 * e**2 + 5000.0 * e - 900.0) / self.gamma_y)

        mask3 = (abs_e >= 1.0) & (abs_e < 1.75)
        sigma[mask3] = sign_e[mask3] * ((60.0 * abs_e[mask3] + 1540.0) / self.gamma_y)

        mask4 = (abs_e >= 1.75) & (abs_e <= self.RES_PCT)
        sigma[mask4] = sign_e[mask4] * (1645.0 / self.gamma_y)

        # Above RES we treat as rupture for benchmark path: zero stress.
        return sigma


class PrestressedSteelType6:
    """Legacy PCROSS prestressed steel family type 6 (figure-consistent).

    IS is initial prestress strain in percent from material input.
    Compression side carries zero stress.
    """

    def __init__(
        self,
        *,
        IS: float,
        fytk: float,
        futk: float,
        eut: float,
        gamma_y: float,
        gamma_u: float,
        gamma_E: float,
        E_modulus: float = 2.0e5,
    ):
        self.IS = float(IS)
        self.fytk = float(fytk)
        self.futk = float(futk)
        self.eut = float(eut)
        self.gamma_y = float(gamma_y)
        self.gamma_u = float(gamma_u)
        self.gamma_E = float(gamma_E)

        self.initial_strain = self.IS / 100.0

        self.E_k = float(E_modulus)
        self.E_p = self.E_k / self.gamma_E

        self.f_pd = self.fytk / self.gamma_y
        self.f_ud = self.futk / self.gamma_u
        self.eps_pd = self.f_pd / self.E_p
        self.eps_ud = self.eut

        self.gamma_s = self.gamma_y

    def stress(self, total_eps: np.ndarray) -> np.ndarray:
        eps_arr = np.asarray(total_eps, dtype=float)
        sigma = np.zeros_like(eps_arr, dtype=float)

        mask_t = eps_arr > 0.0
        if not np.any(mask_t):
            return sigma

        e_t = eps_arr[mask_t]
        sigma_t = np.empty_like(e_t)

        mask_el = e_t <= self.eps_pd
        sigma_t[mask_el] = self.E_p * e_t[mask_el]

        mask_hard = ~mask_el
        if np.any(mask_hard):
            if self.eut > self.eps_pd:
                slope = (self.f_ud - self.f_pd) / (self.eut - self.eps_pd)
                e_h = np.minimum(e_t[mask_hard], self.eut)
                sigma_t[mask_hard] = self.f_pd + slope * (e_h - self.eps_pd)
            else:
                sigma_t[mask_hard] = self.f_pd

        # Above eut: clamp to zero (no extra branches beyond defined segment).
        sigma_t[e_t > self.eut] = 0.0

        sigma[mask_t] = sigma_t
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
            gamma_y=gamma_s,
            gamma_u=gamma_u,
            gamma_E=gamma_E,
            E_modulus=E_s,
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
            IS=100.0 * float(initial_strain),
            fytk=f_p01k,
            futk=f_pk,
            eut=e_uk,
            gamma_y=gamma_s,
            gamma_u=gamma_u,
            gamma_E=gamma_E,
            E_modulus=E_p,
        )
        self.f_p01k = float(f_p01k)
        self.f_pk = float(f_pk)
        self.e_uk = float(e_uk)
