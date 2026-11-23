# Bộ thử dịch vụ TBT Cloud

Ba bài thử cho ba loại dịch vụ: ứng dụng web từ Git, cơ sở dữ liệu PostgreSQL và máy chủ AI có GPU.

## 1. Ứng dụng web từ Git

Tạo dịch vụ **Ứng dụng web từ Git**, ô Kho Git nhập:

```
https://github.com/nguyentambinh/portfolio.git
```

Nhánh `main`. Tạo xong, mở địa chỉ web ở trang chi tiết dịch vụ. Chân trang hiện "đang chạy tại <địa chỉ>" là trang đã được tải từ GitHub về máy và nginx đang phục vụ.

## 2. Cơ sở dữ liệu PostgreSQL

Tạo dịch vụ **Cơ sở dữ liệu PostgreSQL**, sao chép **chuỗi kết nối** ở trang chi tiết (dạng `postgresql://app:<mật khẩu>@<host>:<cổng>/app`).

Trên máy tính của bạn:

```
git clone https://github.com/nguyentambinh/tbt-cloud-kiem-thu.git
cd tbt-cloud-kiem-thu/csdl
pip install "psycopg[binary]"
python thu_csdl.py "postgresql://app:<mật khẩu>@<host>:<cổng>/app"
```

Script kết nối, tạo 3 bảng (sinh viên, khóa học, đăng ký) với khóa ngoại, chỉ mục, ràng buộc CHECK, thêm dữ liệu mẫu, in điểm trung bình từng môn, đo tốc độ ghi 5.000 dòng và 200 truy vấn, thử một giao dịch bị ràng buộc chặn phải hủy cả giao dịch. Dữ liệu mẫu được giữ lại để xem bằng psql hoặc DBeaver:

```
psql "postgresql://app:<mật khẩu>@<host>:<cổng>/app" -c "SELECT * FROM khoa_hoc"
```

## 3. Máy chủ AI (GPU)

Tạo dịch vụ **Máy chủ AI (GPU)**, SSH vào máy bằng lệnh ở trang chi tiết, rồi:

```
nvidia-smi
git clone https://github.com/nguyentambinh/tbt-cloud-kiem-thu.git
cd tbt-cloud-kiem-thu/ai
/opt/ai/bin/python thu_gpu.py
/opt/ai/bin/python thu_llm.py "Điện toán đám mây là gì?"
```

- `thu_gpu.py`: tên GPU, VRAM, tốc độ nhân ma trận fp16/fp32 (có khởi động trước khi đo), huấn luyện mạng CNN trên MNIST một epoch bằng GPU, so với CPU.
- `thu_llm.py`: chạy mô hình ngôn ngữ Qwen2.5-0.5B-Instruct trên GPU, in câu trả lời và tốc độ token/giây. Lần đầu tải mô hình khoảng 1 GB.

Muốn dùng JupyterLab: trong máy chạy `jupyter lab --no-browser --port 8888`, trên máy bạn mở đường hầm `ssh -L 8888:localhost:8888 ...` (lệnh có sẵn ở trang chi tiết) rồi vào http://localhost:8888.
