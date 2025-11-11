# run_rgh_emcee.py
from classy import Class
import emcee
import numpy as np
import multiprocessing

# ==========================================================
# 🔹 Ta vraisemblance personnalisée (ancienne rgh_like)
# ==========================================================
class RGHLike:
    def __init__(self, z_eff=0.0):
        self.z_eff = z_eff

    def log_likelihood(self, params):
        """
        params = [H0, omega_b, omega_cdm]
        Tu peux ici appeler CLASS et calculer ta log-prob custom.
        """
        H0, omega_b, omega_cdm = params

        # On fixe quelques garde-fous physiques :
        if not (40 < H0 < 100 and 0.015 < omega_b < 0.03 and 0.08 < omega_cdm < 0.15):
            return -np.inf  # rejet automatique

        # Initialise CLASS
        cosmo = Class()
        cosmo.set({
            'H0': H0,
            'omega_b': omega_b,
            'omega_cdm': omega_cdm,
            'output': 'mPk',
            'P_k_max_h/Mpc': 2.0
        })
        try:
            cosmo.compute()
            # Exemple arbitraire : on récupère l’amplitude du spectre de puissance à k=0.1
            pk = cosmo.pk(0.1, 0)
            cosmo.struct_cleanup()
        except Exception:
            return -np.inf

        # Ici une pseudo-vraisemblance juste pour tester
        model_val = pk / 1e4
        chi2 = (model_val - self.z_eff)**2 / 0.1**2
        return -0.5 * chi2


# ==========================================================
# 🔹 Fonction de log-probabilité totale
# ==========================================================
def log_probability(params, like):
    logp_prior = 0.0
    H0, omega_b, omega_cdm = params

    # priors simples (gaussiens)
    logp_prior += -0.5 * ((H0 - 67.4)/2)**2
    logp_prior += -0.5 * ((omega_b - 0.0224)/0.0002)**2
    logp_prior += -0.5 * ((omega_cdm - 0.12)/0.005)**2

    if not np.isfinite(logp_prior):
        return -np.inf

    return logp_prior + like.log_likelihood(params)


# ==========================================================
# 🔹 Main
# ==========================================================
if __name__ == "__main__":
    like = RGHLike(z_eff=0.0)

    ndim = 3
    nwalkers = 8
    nsteps = 500

    # Initialisation aléatoire des marcheurs autour des valeurs plausibles
    p0 = np.array([
        [67.4 + np.random.randn()*0.5,
         0.0224 + np.random.randn()*0.0001,
         0.12 + np.random.randn()*0.002]
        for i in range(nwalkers)
    ])

    # Création du sampler
    with multiprocessing.Pool() as pool:
        sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=[like], pool=pool)
        print("🔁 Lancement du MCMC...")
        sampler.run_mcmc(p0, nsteps, progress=True)

    print("✅ Terminé ! Taille de la chaîne :", sampler.chain.shape)

    # Moyenne et écarts types
    flat_samples = sampler.get_chain(discard=100, thin=10, flat=True)
    mean = np.mean(flat_samples, axis=0)
    std = np.std(flat_samples, axis=0)

    print(f"📊 Résultats : H0 = {mean[0]:.2f} ± {std[0]:.2f}, "
          f"Ω_b = {mean[1]:.5f} ± {std[1]:.5f}, "
          f"Ω_cdm = {mean[2]:.3f} ± {std[2]:.3f}")

# ==========================================================
# 🔹 Visualisation avec corner.py
# ==========================================================
# --- Corner plot propre ---
import matplotlib.pyplot as plt
import corner

# 1) repartir d'une figure propre
plt.close('all')

labels = [r"$H_0$", r"$\Omega_b$", r"$\Omega_{cdm}$"]

figure = corner.corner(
    flat_samples,
    labels=labels,
    truths=mean,
    show_titles=True,
    title_fmt=".4f",
    title_kwargs={"fontsize": 10},   # titres plus compacts sur la diagonale
    label_kwargs={"fontsize": 12},   # labels lisibles
    plot_datapoints=False,           # plus clean
    smooth=1.0,                      # contours lissés
)

# 2) suptitle + marge haute suffisante
figure.suptitle("outputs/Posterior distributions – RGHLike + CLASS + emcee", fontsize=14)
plt.subplots_adjust(top=0.90)        # laisse 10 % en haut pour éviter le chevauchement

# 3) sauver proprement (et/ou montrer)
plt.savefig("outputs/posteriors_triangle.png", dpi=200, bbox_inches="tight")
plt.show()

# ==========================================================
# 🔹 Comparaison avec Planck 2018
# ==========================================================
import numpy as np
import corner
import matplotlib.pyplot as plt

# Valeurs Planck 2018 (ΛCDM)
planck_mean = np.array([67.4, 0.02237, 0.1200])
planck_sigma = np.array([0.5, 0.00015, 0.0012])

# Échantillons simulés de Planck (juste pour l'affichage)
rng = np.random.default_rng(42)
planck_samples = rng.normal(planck_mean, planck_sigma, size=(2000, 3))

labels = [r"$H_0$", r"$\Omega_b$", r"$\Omega_{cdm}$"]

# 1️⃣ Planck seul
fig1 = corner.corner(
    planck_samples,
    labels=labels,
    color="tab:orange",
    show_titles=True,
    title_fmt=".4f",
    title_kwargs={"fontsize": 10},
    label_kwargs={"fontsize": 12},
)
fig1.suptitle("Posterior – Planck 2018", fontsize=14)
plt.subplots_adjust(top=0.9)
plt.savefig("outputs/corner_planck.png", dpi=200, bbox_inches="tight")

# 2️⃣ RGH seul (ton résultat)
fig2 = corner.corner(
    flat_samples,
    labels=labels,
    color="tab:blue",
    show_titles=True,
    title_fmt=".4f",
    title_kwargs={"fontsize": 10},
    label_kwargs={"fontsize": 12},
)
fig2.suptitle("Posterior – RGHLike + CLASS + emcee", fontsize=14)
plt.subplots_adjust(top=0.9)
plt.savefig("outputs/corner_rgh.png", dpi=200, bbox_inches="tight")

# 3️⃣ Superposition Planck + RGH
fig3 = corner.corner(
    planck_samples,
    labels=labels,
    color="tab:orange",
    show_titles=False,
    label_kwargs={"fontsize": 12},
)
corner.corner(
    flat_samples,
    labels=labels,
    color="tab:blue",
    show_titles=False,
    fig=fig3,
)
fig3.suptitle("Posterior comparison – Planck (orange) vs RGH (blue)", fontsize=14)
plt.subplots_adjust(top=0.9)
plt.savefig("outputs/corner_comparison.png", dpi=200, bbox_inches="tight")

plt.show()

# ==========================================================
# 📈 Comparaison numérique Planck vs RGH
# ==========================================================
import pandas as pd

# Calcul des statistiques RGH à partir de la chaîne
rgh_mean = np.mean(flat_samples, axis=0)
rgh_std = np.std(flat_samples, axis=0)

# Tableau comparatif
data = {
    "Paramètre": [r"$H_0$", r"$\Omega_b$", r"$\Omega_{cdm}$"],
    "Planck 2018 (μ ± σ)": [
        f"{planck_mean[0]:.3f} ± {planck_sigma[0]:.3f}",
        f"{planck_mean[1]:.5f} ± {planck_sigma[1]:.5f}",
        f"{planck_mean[2]:.3f} ± {planck_sigma[2]:.3f}",
    ],
    "RGH + CLASS (μ ± σ)": [
        f"{rgh_mean[0]:.3f} ± {rgh_std[0]:.3f}",
        f"{rgh_mean[1]:.5f} ± {rgh_std[1]:.5f}",
        f"{rgh_mean[2]:.3f} ± {rgh_std[2]:.3f}",
    ],
    "Δ (RGH - Planck)": [
        f"{rgh_mean[0] - planck_mean[0]:+.3f}",
        f"{rgh_mean[1] - planck_mean[1]:+.5f}",
        f"{rgh_mean[2] - planck_mean[2]:+.3f}",
    ],
}

df = pd.DataFrame(data)
print("\n📊 Comparaison Planck 2018 vs RGHLike :\n")
print(df.to_string(index=False))

# Optionnel : export CSV
df.to_csv("outputs/comparison_planck_rgh.csv", index=False)
print("\n💾 Tableau enregistré dans 'comparison_planck_rgh.csv'\n")


# ==========================================================
# 🔹 Analyse de tension Planck vs RGH (Δ / σ_tot)
# ==========================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Lecture du CSV généré précédemment
df = pd.read_csv("outputs/comparison_planck_rgh.csv")

# Extraction des valeurs numériques
def parse_val_sigma(s):
    """Extrait valeur et écart-type à partir d'une chaîne 'val ± sigma'"""
    val, sig = s.replace(" ", "").split("±")
    return float(val), float(sig)

planck_vals, planck_sigmas = zip(*[parse_val_sigma(x) for x in df["Planck 2018 (μ ± σ)"]])
rgh_vals, rgh_sigmas = zip(*[parse_val_sigma(x) for x in df["RGH + CLASS (μ ± σ)"]])

planck_vals, planck_sigmas = np.array(planck_vals), np.array(planck_sigmas)
rgh_vals, rgh_sigmas = np.array(rgh_vals), np.array(rgh_sigmas)

# Calcul des différences et des tensions
delta = rgh_vals - planck_vals
sigma_tot = np.sqrt(planck_sigmas**2 + rgh_sigmas**2)
tension_sigma = np.abs(delta) / sigma_tot

df["Tension (σ)"] = np.round(tension_sigma, 2)

print("\n📏 Tension entre Planck et RGH (en σ) :\n")
print(df[["Paramètre", "Δ (RGH - Planck)", "Tension (σ)"]].to_string(index=False))

# ==========================================================
# 🔹 Graphique en barres : Tension cosmologique
# ==========================================================
plt.figure(figsize=(6, 3.5))
plt.barh(df["Paramètre"], df["Tension (σ)"], color=["#1f77b4", "#2ca02c", "#d62728"])
plt.axvline(1, color="gray", linestyle="--", label="1σ")
plt.axvline(2, color="gray", linestyle="--", label="2σ")
plt.axvline(3, color="gray", linestyle="--", label="3σ")
plt.xlabel("Tension Planck ↔ RGH (en σ)")
plt.title("Cosmological tension per parameter")
plt.legend()
plt.tight_layout()
plt.savefig("outputs/Cosmological_tension_per_parameter.png", dpi=200, bbox_inches="tight")
plt.show()

# ==========================================================
# 📊 Tableau de comparaison Planck vs RGH (moyenne ± σ + tension)
# ==========================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Exemple : dictionnaires de valeurs (à remplacer par tes vraies moyennes ± sigma)
planck = {"H0": (67.40, 0.47), "Ω_b": (0.02237, 0.00015), "Ω_cdm": (0.120, 0.0012)}
rgh    = {"H0": (70.05, 1.78), "Ω_b": (0.02244, 0.00020), "Ω_cdm": (0.096, 0.005)}

# Calcul de la tension en σ
rows = []
for k in planck:
    Δ = abs(planck[k][0] - rgh[k][0])
    σ = np.sqrt(planck[k][1]**2 + rgh[k][1]**2)
    tension = Δ / σ
    rows.append([k,
                 f"{planck[k][0]:.4f} ± {planck[k][1]:.4f}",
                 f"{rgh[k][0]:.4f} ± {rgh[k][1]:.4f}",
                 f"{tension:.2f} σ"])

df = pd.DataFrame(rows, columns=["Paramètre", "Planck 2018", "RGH", "Tension"])

# Création de la figure
fig, ax = plt.subplots(figsize=(6, 1.5))
ax.axis("off")
table = plt.table(
    cellText=df.values,
    colLabels=df.columns,
    cellLoc="center",
    loc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.3)

plt.title("Comparaison Planck vs RGH – Moyennes ± σ et Tension", pad=10)
plt.tight_layout()
plt.savefig("comparison_table.png", dpi=300)
plt.show()
