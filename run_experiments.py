import mlflow
import os
import yaml
from src.train import train

# Dat bien moi truong cho MLflow
os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///mlflow.db"
os.environ["MLFLOW_ARTIFACT_ROOT"] = "./mlartifacts"

# Danh sach cac sieu tham so thu nghiem (Buoc 1)
experiments = [
    {"n_estimators": 100, "max_depth": 5, "min_samples_split": 2},
    {"n_estimators": 50, "max_depth": 3, "min_samples_split": 2},
    {"n_estimators": 200, "max_depth": 10, "min_samples_split": 5},
]

best_acc = -1.0
best_params = None

# Chay thu nghiem
for i, params in enumerate(experiments, 1):
    print(f"\n=== Chay thi nghiem lan {i}: params = {params} ===")
    acc = train(params)
    if acc > best_acc:
        best_acc = acc
        best_params = params

print(f"\nDo chinh xac tot nhat: {best_acc:.4f} voi sieu tham so: {best_params}")

# Luu sieu tham so tot nhat vao params.yaml
with open("params.yaml", "w") as f:
    yaml.dump(best_params, f)
print("Da cap nhat params.yaml voi bo sieu tham so tot nhat!")
