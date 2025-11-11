# 🪐 cobaya-RGH : Exploration cosmologique avec CLASS, Cobaya et emcee

## 🔧 1. Présentation

Ce dépôt contient une version personnalisée de l'environnement **Cobaya/CLASS** pour explorer des modèles cosmologiques,
ainsi qu'une version simplifiée du pipeline basée sur **emcee** (MCMC Python pur).

L’objectif est de reproduire et comparer des postérieurs cosmologiques (H₀, Ω_b, Ω_cdm)
en utilisant un *likelihood* maison : `rgh_like`.

---

## 🧰 2. Installation de l’environnement

### a. Cloner le dépôt
```bash
git clone https://github.com/lolotux69/cobaya-RGH.git
cd cobaya-RGH
```

### b. Créer un environnement Python isolé
```bash
python3 -m venv cobaya_env
source cobaya_env/bin/activate
```

### c. Installer les dépendances
```bash
pip install --upgrade pip
pip install numpy scipy matplotlib pandas emcee corner classylss cobaya
```

> 💡 Si `classylss` ne s’installe pas via `pip`, consulte [https://github.com/lesgourg/class_public](https://github.com/lesgourg/class_public)
et compile-le manuellement (librairie CLASS).

---

## 📂 3. Structure du dépôt

```
cobaya-RGH/
│
├── my_likelihoods/
│   └── rgh_like.py        # Likelihood personnalisé (maison)
│
├── run_rgh_emcee.py       # Script MCMC simplifié utilisant emcee + CLASS
├── outputs/               # Contiendra les chaînes et graphiques générés
├── comparison_planck_rgh.csv  # Comparaison Planck/RGH des paramètres
└── README.md              # Ce fichier
```

---

## 🚀 4. Exécution du MCMC

Une fois l’environnement activé :

```bash
PYTHONPATH=$(pwd) python run_rgh_emcee.py
```

Le script :

1. Charge `rgh_like` comme vraisemblance,  
2. Exécute un MCMC via `emcee`,  
3. Calcule les moyennes et écarts-types pour :  
   - **H₀** (taux d’expansion actuel),  
   - **Ω_b** (densité baryonique),  
   - **Ω_cdm** (matière noire froide),  
4. Génère automatiquement un graphique triangulaire (`corner_plot`)  
   et un fichier de résultats CSV comparant les postérieurs **Planck** / **RGH**.

---

## 📊 5. Résultats produits

À la fin de l’exécution, tu obtiens :

```
✅ Terminé ! Taille de la chaîne : (8, 500, 3)
📊 Résultats : H₀ = 70.55 ± 1.82, Ω_b = 0.02244 ± 0.00020, Ω_cdm = 0.097 ± 0.004
```

### Fichiers créés :
| Fichier | Contenu |
|----------|----------|
| `outputs/posteriors_triangle.png` | Diagramme triangulaire des postérieurs |
| `outputs/corner_planck.png` | Référence Planck |
| `outputs/corner_rgh.png` | Résultat RGH |
| `outputs/corner_comparison.png` | Superposition Planck / RGH |
| `comparison_planck_rgh.csv` | Tableau des moyennes ± σ |

---

## 🧪 6. Personnalisation

Tu peux :
- Modifier les paramètres ou bornes directement dans `run_rgh_emcee.py`.
- Changer le nombre d’itérations MCMC (`nsteps`) ou le nombre de walkers (`nwalkers`).
- Relancer simplement le script pour obtenir de nouvelles chaînes.

---

## 🧭 7. Auteur & Licence

Projet développé par **lolotux69**  
Basé sur **Cobaya**, **CLASS** et **emcee**.  
Licence MIT.

---

🪶 *« Un MCMC propre vaut mieux qu’un YAML en feu. »* 😄
