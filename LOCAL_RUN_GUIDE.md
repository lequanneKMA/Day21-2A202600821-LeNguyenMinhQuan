# Hướng Dẫn Chạy Cục Bộ (Local Run Guide)

Vì bạn muốn chạy tất cả thông qua môi trường ảo (venv) cục bộ, dưới đây là các bước chi tiết để bạn tự chạy và chụp màn hình nộp bài lab:

---

## 1. Kích hoạt môi trường ảo (Virtual Environment)
Mở terminal tại thư mục gốc của project (`Day21-Track2-CI-CD-for-AI-Systems`) và chạy lệnh sau để kích hoạt venv:
```bash
source .venv/bin/activate
```

---

## 2. Khởi tạo DVC và Theo dõi dữ liệu
Chạy script `init_dvc.sh` đã được tạo sẵn để tự động khởi tạo DVC và theo dõi các file dữ liệu Wine Quality:
```bash
bash init_dvc.sh
```
*Lưu ý: Nếu bạn có Cloud Storage Bucket thực tế, hãy mở file `.dvc/config` ra và thay thế `gs://YOUR_BUCKET_NAME/dvc` thành tên bucket của bạn.*

---

## 3. Chạy các thí nghiệm MLflow và tìm tham số tốt nhất (Bước 1)
Chúng tôi đã viết sẵn một script Python `run_experiments.py` để tự động chạy cả 3 thí nghiệm MLflow cục bộ, so sánh kết quả và tự động cập nhật bộ siêu tham số tối ưu nhất vào `params.yaml`:
```bash
python run_experiments.py
```
Sau đó, để mở giao diện MLflow UI và chụp màn hình nộp bài, bạn chạy:
```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```
Mở trình duyệt truy cập vào: [http://localhost:5000](http://localhost:5000). Bạn sẽ thấy giao diện so sánh 3 lần chạy.

---

## 4. Chạy Unit Test cục bộ (Bước 2)
Chạy bộ kiểm thử tự động `pytest` để đảm bảo code huấn luyện và việc sinh file metrics/model hoạt động chính xác:
```bash
pytest tests/ -v
```
Bạn sẽ thấy 3 test cases đều đạt trạng thái `PASSED`.

---

## 5. Khởi chạy FastAPI Server cục bộ (Model Serving)
Khởi động uvicorn server để chạy Model Serving API cục bộ:
```bash
python src/serve.py
```
Server sẽ chạy tại cổng `8000`.

---

## 6. Kiểm tra API bằng lệnh curl
Mở một terminal mới (nhớ kích hoạt venv) và chạy các lệnh curl sau để kiểm tra:

### Kiểm tra sức khỏe (Health Check):
```bash
curl http://localhost:8000/health
```
**Kết quả mong đợi:**
```json
{"status": "ok"}
```

### Dự đoán chất lượng rượu (Predict):
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [7.4, 0.70, 0.00, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4, 0]}'
```
**Kết quả mong đợi:**
```json
{"prediction": 0, "label": "thap"}
```

---

## 7. Bổ sung dữ liệu mới và huấn luyện lại (Bước 3)
Chạy script mô phỏng thêm dữ liệu mới (tăng từ 2998 mẫu lên 5996 mẫu):
```bash
python add_new_data.py
```
Sau đó chạy lại script thí nghiệm hoặc train để có mô hình mới:
```bash
python src/train.py
```
