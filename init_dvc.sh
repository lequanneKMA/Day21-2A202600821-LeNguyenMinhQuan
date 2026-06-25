#!/bin/bash
# Khoi tao DVC va theo doi du lieu (GCP GCS)

# 1. Khoi tao DVC neu chua ton tai
if [ ! -d ".dvc" ]; then
    dvc init --no-scm
else
    echo "Thu muc .dvc da ton tai, bo qua khoi tao."
fi

# 2. Viet file config de dung remote GCS
cat <<EOF > .dvc/config
[core]
    analytics = false
    remote = myremote
[remote "myremote"]
    url = gs://YOUR_BUCKET_NAME/dvc
    credentialpath = sa-key.json
EOF

# 3. Theo doi cac file du lieu
dvc add data/train_phase1.csv
dvc add data/eval.csv
dvc add data/train_phase2.csv

echo "DVC da duoc khoi tao va theo doi cac tap du lieu thanh cong!"
echo "Hay cap nhat ten bucket GCS cua ban trong .dvc/config."
