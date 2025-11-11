#!/bin/bash
set -e
mkdir -p outputs/logs outputs/chains outputs/plots
echo "[RUN] Starting short Cobaya MCMC test with CLASS-RGH..."
date

# === Localisation automatique de CLASS-RGH ===
BASE_DIR=$(dirname "$(realpath "$0")")/..
CLASS_DIR="$BASE_DIR/../class_RGH_github"
BUILD_DIR=$(find "$CLASS_DIR/build" -type d -name "lib.linux-*" | head -n 1)

if [ -d "$BUILD_DIR" ]; then
  export PYTHONPATH="$BUILD_DIR:$PYTHONPATH"
  export PATH="$CLASS_DIR:$PATH"
  echo "[ENV] CLASS-RGH loaded from: $BUILD_DIR"
else
  echo "[ERROR] Impossible de trouver le build de CLASS dans $CLASS_DIR"
  exit 1
fi

# === Lancement Cobaya ===
cobaya-run config/full_test.yaml -o outputs/chains/test_chain --force | tee outputs/logs/test_run.log
echo "[DONE] Test completed."
date
#!/bin/bash
set -e
mkdir -p outputs/logs outputs/chains outputs/plots
echo "[RUN] Starting short Cobaya MCMC test with CLASS-RGH..."
date
cobaya-run config/full_test.yaml -o outputs/chains/test_chain --force | tee outputs/logs/test_run.log
echo "[DONE] Test completed."
date
