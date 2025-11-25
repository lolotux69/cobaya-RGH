# bao_dataset.py

import numpy as np
import pandas as pd

def load_bao_dr16(path="data/BAO/sdss_DR16_ELG_FSBAO_DMDHfs8gridlikelihood.txt"):
    """
    Charge les données BAO DR16 eBOSS au format numpy/pandas.
    Renvoie les colonnes utiles pour la vraisemblance.
    """
    # Ignore les lignes de commentaire
    df = pd.read_csv(path, delim_whitespace=True, comment="#")
    print("📊 Colonnes disponibles :", list(df.columns))
    return df

def bao_likelihood(DM_model, H_model, fs8_model, df):
    """
    Interpole la vraisemblance BAO eBOSS DR16 en fonction
    des valeurs RGH prévues pour D_M, H et fσ8.
    """
    # Conversion du DataFrame → numpy arrays
    X = df.iloc[:, 0:3].values  # (D_M, H, fσ8)
    L = df.iloc[:, 3].values    # vraisemblance tabulée

    # Création d’un interpolateur multi-dimensionnel
    interp = LinearNDInterpolator(X, np.log(L + 1e-300))  # log-likelihood

    # Valeur prédite par ton modèle RGH
    lnL = interp(DM_model, H_model, fs8_model)

    # Si extrapolation → pénaliser
    if np.isnan(lnL):
        lnL = -1e6

    return lnL

from scipy.interpolate import LinearNDInterpolator
import numpy as np
import pandas as pd

def load_bao_dr16(path="data/BAO/sdss_DR16_ELG_FSBAO_DMDHfs8gridlikelihood.txt"):
    df = pd.read_csv(path, sep=r"\s+", comment="#", engine="python")
    print("📊 Colonnes disponibles :", list(df.columns))
    return df

def bao_likelihood(DM_model, H_model, fs8_model, df):
    """
    Interpole la vraisemblance BAO eBOSS DR16 en fonction
    des valeurs RGH prévues pour D_M, H et fσ8.
    """
    X = df.iloc[:, 0:3].values
    L = df.iloc[:, 3].values
    interp = LinearNDInterpolator(X, np.log(L + 1e-300))
    lnL = interp(DM_model, H_model, fs8_model)
    if np.isnan(lnL):
        lnL = -1e6
    return lnL
