from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
import joblib
import os

app = FastAPI()

GCS_BUCKET = os.environ.get("CLOUD_BUCKET", os.environ.get("GCS_BUCKET", ""))
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """
    Tai file model.pkl tu GCS ve may khi server khoi dong.

    Ham nay duoc goi mot lan khi module duoc import.
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    if not GCS_BUCKET:
        print("GCS_BUCKET is not set. Checking for local models...")
        if os.path.exists(MODEL_PATH):
            print(f"Using existing local model at {MODEL_PATH}")
            return
        elif os.path.exists("models/model.pkl"):
            print("Copying workspace models/model.pkl to ~/models/model.pkl")
            import shutil

            shutil.copyfile("models/model.pkl", MODEL_PATH)
            return
        else:
            print("No local model found. Server will start but prediction might fail.")
            return

    try:
        # Khoi tao client GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET)
        blob = bucket.blob("models/latest/model.pkl")

        # Tai file model tu GCS
        blob.download_to_filename(MODEL_PATH)
        print("Model da duoc tai xuong tu GCS.")
    except Exception as e:
        print(f"Error downloading model from GCS: {e}")
        # Fallback to local workspace model if possible
        if not os.path.exists(MODEL_PATH):
            if os.path.exists("models/model.pkl"):
                print("Falling back to local models/model.pkl from workspace.")
                import shutil

                shutil.copyfile("models/model.pkl", MODEL_PATH)
            else:
                raise e


# Goi ham tai model
download_model()

# Load model if it exists
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    print(f"Warning: Model file not found at {MODEL_PATH}. Prediction endpoint will be unavailable.")


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    global model
    if len(req.features) != 12:
        raise HTTPException(
            status_code=400, detail="Expected 12 features (wine quality)"
        )

    # Lazily load model if not loaded
    if model is None:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
        else:
            raise HTTPException(
                status_code=503, detail="Model not loaded on server."
            )

    pred = model.predict([req.features])
    pred_val = int(pred[0])

    labels = {0: "thap", 1: "trung_binh", 2: "cao"}
    label = labels.get(pred_val, "unknown")

    return {"prediction": pred_val, "label": label}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
