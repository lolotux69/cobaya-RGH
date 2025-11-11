#!/bin/bash

# 1. Crée un environnement
python3 -m venv cobaya_env
source cobaya_env/bin/activate
# 2. Mets pip à jour
pip install --upgrade pip
# 3. Installe Cobaya (stable)
pip install cobaya emcee matplotlib
