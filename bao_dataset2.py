# bao_dataset2.py
import pandas as pd
import numpy as np

def load_bao_dr16(path="/media/lolo/Big-Disk-03/Partage/PDF/Sciences/Relativité/RGH/Grok-4.1.2-RGH/cobaya-RGH/data/BAO/sdss_DR16_ELG_FSBAO_DMDHfs8gridlikelihood.txt"):
    """
    Charge les données eBOSS DR16 BAO.
    """
    df = pd.read_csv(path, sep=r"\s+", comment="#", header=None)
    df.columns = ["DM", "H", "fs8", "likelihood"]
    print(f"📊 Colonnes BAO : {list(df.columns)}")
    print(df.head())
    return df


def bao_likelihood2(DM_model, H_model, fs8_model, df):
    """
    Recherche du point le plus proche dans la grille DR16
    pour approximer la log-vraisemblance.
    """
    dm = df["DM"].to_numpy()
    hh = df["H"].to_numpy()
    fs8 = df["fs8"].to_numpy()
    L = df["likelihood"].to_numpy()

    dist = np.sqrt((dm - DM_model)**2 + (hh - H_model)**2 + (fs8 - fs8_model)**2)
    idx = np.argmin(dist)
    return np.log(L[idx] + 1e-300)  # évite log(0)
