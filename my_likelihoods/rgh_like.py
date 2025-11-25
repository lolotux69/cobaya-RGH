# rgh_like.py

from typing import Optional
from cobaya.likelihood import Likelihood

class rgh_like(Likelihood):
    z_eff: float = 0.0
    data_file: Optional[str] = None

    def initialize(self):
        print(f">>> [rgh_like] initialize() appelée avec z_eff={self.z_eff}")

    def logp(self, **params):
        return -0.5 * (self.z_eff - 0.0) ** 2
