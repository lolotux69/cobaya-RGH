#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# run_rgh_emcee2.py — version stable RGH + BAO + CLASS + emcee v3

import os
import numpy as np
import emcee
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import corner

# === Imports locaux ===
from bao_dataset2 import load_bao_dr16, bao_likelihood2
from my_likelihoods.rgh_like2 import RGHLike2

OUTDIR = "outputs"
os.makedirs(OUTDIR, exist_ok=True)

# ==========================================
# 🔹 Chargement global des données BAO
# ==========================================
BAO_DF = load_bao_dr16()

# ==========================================
# 🔹 Log-probabilité totale
# ==========================================
def log_probability(params, like):
    H0, omega_b, omega_cdm = params

    # Priors
    lp  = -0.5 * ((H0 - 67.4) / 2.0) ** 2
    lp += -0.5 * ((omega_b - 0.0224) / 0.0002) ** 2
    lp += -0.5 * ((omega_cdm - 0.12) / 0.005) ** 2
    if not np.isfinite(lp):
        return -np.inf

    lnL_rgh = like.log_likelihood(params)
    if not np.isfinite(lnL_rgh):
        return -np.inf

    lnL_bao = bao_likelihood2(10.4, 7.6, 0.03, BAO_DF)
    return lp + lnL_rgh + lnL_bao


# ==========================================
# 🔹 Lancement du MCMC
# ==========================================
def main():
    like = RGHLike2(z_eff=0.0)
    ndim, nwalkers, nsteps = 3, 10, 500

    rng = np.random.default_rng(123)
    p0 = np.array([
        [67.4 + rng.normal(scale=0.5),
         0.0224 + rng.normal(scale=1e-4),
         0.12   + rng.normal(scale=0.002)]
        for _ in range(nwalkers)
    ])

    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=[like])
    print("🔁 Lancement du MCMC...")
    sampler.run_mcmc(p0, nsteps, progress=True)
    chain = sampler.get_chain()
    print("✅ Terminé ! Taille de la chaîne :", chain.shape)

    flat = sampler.get_chain(discard=100, thin=10, flat=True)
    mean, std = flat.mean(axis=0), flat.std(axis=0)

    print(f"📊 Résultats : H0 = {mean[0]:.2f} ± {std[0]:.2f}, "
          f"Ω_b = {mean[1]:.5f} ± {std[1]:.5f}, "
          f"Ω_cdm = {mean[2]:.3f} ± {std[2]:.3f}")

    # === Corner Plot ===
    labels = [r"$H_0$", r"$\Omega_b$", r"$\Omega_{cdm}$"]
    fig = corner.corner(flat, labels=labels, truths=mean, show_titles=True)
    fig.suptitle("Posterior – RGHv2 + CLASS + BAO + emcee", fontsize=14)
    fig.savefig(os.path.join(OUTDIR, "posteriors_triangle_v2.png"), dpi=200, bbox_inches="tight")

    # === Comparaison Planck ===
    planck_mean = np.array([67.4, 0.02237, 0.1200])
    planck_sigma = np.array([0.5, 0.00015, 0.0012])

    df = pd.DataFrame({
        "Paramètre": [r"$H_0$", r"$\Omega_b$", r"$\Omega_{cdm}$"],
        "Planck 2018 (μ ± σ)": [
            f"{planck_mean[0]:.3f} ± {planck_sigma[0]:.3f}",
            f"{planck_mean[1]:.5f} ± {planck_sigma[1]:.5f}",
            f"{planck_mean[2]:.3f} ± {planck_sigma[2]:.3f}",
        ],
        "RGH + CLASS (μ ± σ)": [
            f"{mean[0]:.3f} ± {std[0]:.3f}",
            f"{mean[1]:.5f} ± {std[1]:.5f}",
            f"{mean[2]:.3f} ± {std[2]:.3f}",
        ],
    })
    df.to_csv(os.path.join(OUTDIR, "comparison_planck_rgh_v2.csv"), index=False)

    # === Tension cosmologique ===
    delta = mean - planck_mean
    sigma_tot = np.sqrt(planck_sigma**2 + std**2)
    tension = np.abs(delta) / sigma_tot

    plt.figure(figsize=(6, 3))
    plt.barh(labels, tension, color="tab:blue")
    plt.axvline(1, color="gray", linestyle="--")
    plt.axvline(2, color="gray", linestyle="--")
    plt.axvline(3, color="gray", linestyle="--")
    plt.xlabel("Tension (σ)")
    plt.title("Cosmological tension per parameter (v2)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "Cosmological_tension_per_parameter_v2.png"), dpi=200)
    plt.close()

    print("📈 Graphiques sauvegardés dans :", OUTDIR)


if __name__ == "__main__":
    main()
