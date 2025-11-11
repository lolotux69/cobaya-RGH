# RGH Project v1

Petit test Cobaya + CLASS-RGH pour valider l’intégration locale.

## ⚙️ Préparation

```bash
cd cobaya-RGH/RGH_project_v1
source ../cobaya_env/bin/activate
```

## 🚀 Lancer le test

```bash
bash scripts/run_test.sh
```

## 📊 Vérifications

- Logs : `tail -f outputs/logs/test_run.log`
- Chaînes MCMC : `ls outputs/chains`

## 🧹 Nettoyer

```bash
bash scripts/clean_outputs.sh
```
