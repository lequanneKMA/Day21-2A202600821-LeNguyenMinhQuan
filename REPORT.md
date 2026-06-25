# Báo Cáo Thực Hành: CI/CD cho AI Systems (Day 21)

## 1. Kết Quả Thí Nghiệm & Lựa Chọn Siêu Tham Số (Bước 1)

Chúng tôi đã chạy 3 thí nghiệm với các bộ siêu tham số khác nhau của thuật toán `RandomForestClassifier` trên tập dữ liệu **Wine Quality** (Wine Quality Dataset). Kết quả thu được như sau:

| Lần chạy | Siêu tham số | Accuracy (Tập Eval) | F1-Score (Tập Eval) | Nhận xét |
| :---: | :--- | :---: | :---: | :--- |
| **Lan 1** | `n_estimators: 100`, `max_depth: 5`, `min_samples_split: 2` | **~0.7480** | **~0.7412** | Đạt yêu cầu, mô hình học vừa phải. |
| **Lan 2** | `n_estimators: 50`, `max_depth: 3`, `min_samples_split: 2` | ~0.7160 | ~0.7025 | Độ chính xác thấp hơn do giới hạn độ sâu cây. |
| **Lan 3** | `n_estimators: 200`, `max_depth: 10`, `min_samples_split: 5` | ~0.7820 | ~0.7790 | Đạt độ chính xác tốt nhất, mô hình học sâu hơn. |

**Bộ siêu tham số được chọn:**
* `n_estimators: 200`
* `max_depth: 10`
* `min_samples_split: 5`

**Lý do chọn:** Bộ siêu tham số ở lần chạy 3 đạt độ chính xác `Accuracy` cao nhất (~78.2%), vượt trội đáng kể so với hai lần chạy còn lại và vượt ngưỡng yêu cầu deploy tối thiểu (0.70). Do đó, bộ thông số này được lưu vào `params.yaml` để sử dụng cho pipeline CI/CD.

---

## 2. Thiết Kế Hệ Thống CI/CD & Model Serving (Bước 2 & 3)

Hệ thống được tổ chức hoàn chỉnh theo đúng kiến trúc MLOps:
1. **DVC (Data Version Control):** Quản lý phiên bản cho 3 file dữ liệu (`data/train_phase1.csv`, `data/eval.csv`, `data/train_phase2.csv`) trỏ tới Google Cloud Storage (GCS) remote. Tránh lưu trữ các file dữ liệu nặng trực tiếp trên Git repo.
2. **FastAPI Serving API (`src/serve.py`):**
   * Endpoint `GET /health` trả về trạng thái hoạt động của server.
   * Endpoint `POST /predict` nhận đầu vào 12 đặc trưng hóa học của rượu vang và trả về dự đoán (`0: thap`, `1: trung_binh`, `2: cao`).
   * Có cơ chế tự động tải mô hình mới nhất từ GCS hoặc tải từ fallback cục bộ nếu không kết nối được GCS.
3. **GitHub Actions Workflow (`.github/workflows/mlops.yml`):**
   * **Job 1 (Unit Test):** Chạy kiểm thử tự động với `pytest` để xác minh chức năng huấn luyện và các file outputs được sinh ra chính xác.
   * **Job 2 (Train):** Xác thực GCS credentials, sử dụng `dvc pull` để lấy dữ liệu thực, chạy huấn luyện và upload mô hình `model.pkl` lên GCS.
   * **Job 3 (Eval Gate):** Đọc giá trị `accuracy` từ kết quả train. Nếu `accuracy < 0.70`, dừng pipeline và hủy bỏ deploy để tránh phát hành mô hình lỗi.
   * **Job 4 (Deploy):** Kết nối SSH vào Cloud VM qua SSH key, restart service `mlops-serve.service` để cập nhật mô hình mới và kiểm tra sức khỏe server.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

1. **Khó khăn về quyền truy cập DVC trong môi trường CI/CD:**
   * *Vấn đề:* Khi chạy GitHub Actions, lệnh `dvc pull` cần file khóa xác thực GCP (`sa-key.json`) để tải dữ liệu.
   * *Giải quyết:* Cấu hình secret `CLOUD_CREDENTIALS` trên GitHub chứa nội dung JSON của Service Account. Trong workflow, ghi nội dung này ra file `sa-key.json` trước khi chạy `dvc pull`.
2. **Khởi chạy server FastAPI khi mô hình chưa sẵn sàng:**
   * *Vấn đề:* Khi khởi động FastAPI trên VM lần đầu, nếu chưa có file mô hình từ GCS, server uvicorn sẽ crash và không thể nhận deploy.
   * *Giải quyết:* Cấu hình hàm `download_model()` tải mô hình lúc import module và có cơ chế fallback load mô hình cục bộ hoặc khởi chạy server dạng lazy loading để tránh crash hệ thống.
3. **Lỗi xác thực thanh toán khi đăng ký tài khoản Cloud (AWS / GCP):**
   * *Vấn đề:* Cổng thanh toán của Google Cloud báo lỗi xác minh thẻ (`OR_BACR2_44`/yêu cầu nạp trước 250k) và tài khoản AWS rơi vào trạng thái chờ kích hoạt 24 giờ, khiến việc tạo tài nguyên Cloud thực tế (S3/GCS bucket và VM) tạm thời bị gián đoạn.
   * *Giải quyết:* Toàn bộ code cho pipeline CI/CD (GitHub Actions) và API Serving (`serve.py`) đã được viết chuẩn hóa theo thiết kế GCP thực tế để sẵn sàng hoạt động ngay khi tài khoản được xác minh. Để nộp bài và chứng minh tính đúng đắn của logic phiên bản hóa, DVC được cấu hình tạm thời sử dụng Local Remote (`dvc_local_remote`) để thực hiện thành công các lệnh `dvc add` và `dvc push`. Toàn bộ unit test và API serving đã được khởi chạy cục bộ thành công 100% để chụp màn hình làm bằng chứng nộp bài.



