import numpy as np

class Concrete:
    """
    Eurocode 2 Parabola-Rectangle Concrete Model (EN 1992-1-1:2004 Section 3.1.7).
    Strains are treated as positive for compression.
    """
    def __init__(self, f_ck: float, gamma_c: float = 1.45, alpha_cc: float = 1.0):
        self.f_ck = f_ck
        self.gamma_c = gamma_c
        self.alpha_cc = alpha_cc
        self.f_cd = self.alpha_cc * self.f_ck / self.gamma_c
        
        # Eurocode 2 definitions for standard vs high-strength concrete
        if self.f_ck <= 50.0:
            self.eps_c2 = 2.0 / 1000.0
            self.eps_cu2 = 3.5 / 1000.0
            self.n = 2.0
        else:
            self.eps_c2 = (2.0 + 0.085 * (self.f_ck - 50.0)**0.53) / 1000.0
            self.eps_cu2 = (2.6 + 35.0 * ((90.0 - self.f_ck) / 100.0)**4) / 1000.0
            self.n = 1.4 + 23.4 * ((90.0 - self.f_ck) / 100.0)**4

    def stress(self, eps: np.ndarray) -> np.ndarray:
        """
        Calculates the concrete compressive stress for a given array of strains.
        Tensile strains (eps < 0) return 0.0.
        """
        eps = np.asarray(eps)
        sigma = np.zeros_like(eps, dtype=float)
        
        # Parabolic branch
        mask_parabola = (eps >= 0.0) & (eps < self.eps_c2)
        sigma[mask_parabola] = self.f_cd * (1.0 - (1.0 - eps[mask_parabola] / self.eps_c2)**self.n)
        
        # Rectangular branch
        mask_rect = (eps >= self.eps_c2) & (eps <= self.eps_cu2)
        sigma[mask_rect] = self.f_cd
        
        # Crushed concrete (strain exceeds ultimate limit)
        mask_crush = eps > self.eps_cu2
        sigma[mask_crush] = 0.0
        
        return sigma

class MildSteel:
    """
    Eurocode 2 Mild Reinforcing Steel Model.
    Supports both horizontal top branch and inclined strain-hardening branch.
    Strains are treated as positive for tension.
    """
    def __init__(self, f_yk: float, gamma_s: float = 1.20, E_s: float = 200000.0, 
                 e_uk: float = 0.02, f_uk: float = None, include_hardening: bool = False):
        self.f_yk = f_yk
        self.gamma_s = gamma_s
        self.E_s = E_s
        self.f_yd = self.f_yk / self.gamma_s
        self.eps_yd = self.f_yd / self.E_s
        self.eps_ud = 0.9 * e_uk  # Design ultimate strain limit per EC2
        
        self.include_hardening = include_hardening
        if self.include_hardening and f_uk is not None:
            self.k = f_uk / f_yk
            self.f_ud = (self.k * self.f_yk) / self.gamma_s
        else:
            self.f_ud = self.f_yd

    def stress(self, eps: np.ndarray) -> np.ndarray:
        """
        Calculates the steel stress for a given array of strains.
        Handles both tension (positive) and compression (negative).
        """
        eps = np.asarray(eps)
        sigma = np.zeros_like(eps, dtype=float)
        
        # Absolute strain for symmetric behavior
        abs_eps = np.abs(eps)
        sign_eps = np.sign(eps)
        
        # Elastic branch
        mask_elastic = abs_eps <= self.eps_yd
        sigma[mask_elastic] = eps[mask_elastic] * self.E_s
        
        # Yield / Hardening branch
        mask_yield = (abs_eps > self.eps_yd) & (abs_eps <= self.eps_ud)
        if self.include_hardening:
            slope = (self.f_ud - self.f_yd) / (self.eps_ud - self.eps_yd)
            sigma[mask_yield] = sign_eps[mask_yield] * (self.f_yd + slope * (abs_eps[mask_yield] - self.eps_yd))
        else:
            sigma[mask_yield] = sign_eps[mask_yield] * self.f_yd
            
        # Ruptured steel
        mask_rupture = abs_eps > self.eps_ud
        sigma[mask_rupture] = 0.0
        
        return sigma

class PrestressedSteel:
    """
    Prestressing Steel Model incorporating initial prestrain.
    """
    def __init__(self, f_p01k: float, f_pk: float, initial_strain: float, 
                 e_uk: float, gamma_s: float = 1.20, E_p: float = 195000.0):
        self.f_p01k = f_p01k
        self.f_pk = f_pk
        self.initial_strain = initial_strain
        self.gamma_s = gamma_s
        self.E_p = E_p
        
        self.f_pd = self.f_p01k / self.gamma_s
        self.eps_pd = self.f_pd / self.E_p
        
        # Design ultimate strain limit per EC2 (typically 0.9 * characteristic limit)
        self.eps_ud = 0.9 * e_uk
        
    def stress(self, geometric_eps: np.ndarray) -> np.ndarray:
        """
        Calculates the prestressing steel stress by adding the initial prestrain
        to the section's geometric strain.
        """
        total_eps = np.asarray(geometric_eps) + self.initial_strain
        sigma = np.zeros_like(total_eps, dtype=float)
        
        abs_eps = np.abs(total_eps)
        sign_eps = np.sign(total_eps)
        
        # Elastic branch
        mask_elastic = abs_eps <= self.eps_pd
        sigma[mask_elastic] = total_eps[mask_elastic] * self.E_p
        
        # Yield branch (Horizontal per idealized EC2 model)
        mask_yield = (abs_eps > self.eps_pd) & (abs_eps <= self.eps_ud)
        sigma[mask_yield] = sign_eps[mask_yield] * self.f_pd
        
        # Ruptured steel
        mask_rupture = abs_eps > self.eps_ud
        sigma[mask_rupture] = 0.0
        
        return sigma