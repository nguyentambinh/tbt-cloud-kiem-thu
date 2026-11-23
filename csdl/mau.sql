-- Nguyễn Tâm Bình - 2324801030003
-- Dữ liệu mẫu quản lý khóa học: tạo bảng, khóa ngoại, chỉ mục, thêm dữ liệu, truy vấn gộp

DROP TABLE IF EXISTS dang_ky, khoa_hoc, sinh_vien CASCADE;

CREATE TABLE sinh_vien (
  id SERIAL PRIMARY KEY,
  mssv VARCHAR(13) UNIQUE NOT NULL,
  ho_ten VARCHAR(80) NOT NULL,
  lop VARCHAR(20) NOT NULL,
  ngay_tao TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE khoa_hoc (
  id SERIAL PRIMARY KEY,
  ma VARCHAR(20) UNIQUE NOT NULL,
  ten VARCHAR(120) NOT NULL,
  tin_chi SMALLINT NOT NULL CHECK (tin_chi BETWEEN 1 AND 6)
);

CREATE TABLE dang_ky (
  sinh_vien_id INT NOT NULL REFERENCES sinh_vien(id) ON DELETE CASCADE,
  khoa_hoc_id INT NOT NULL REFERENCES khoa_hoc(id) ON DELETE CASCADE,
  diem NUMERIC(4, 2) CHECK (diem BETWEEN 0 AND 10),
  PRIMARY KEY (sinh_vien_id, khoa_hoc_id)
);
CREATE INDEX idx_dang_ky_khoa_hoc ON dang_ky(khoa_hoc_id);

INSERT INTO khoa_hoc (ma, ten, tin_chi) VALUES
  ('DTDM', 'Điện toán đám mây', 3),
  ('HM', 'Học máy', 3),
  ('KTPM', 'Kiến trúc và thiết kế phần mềm', 3),
  ('PTUDDNT', 'Phát triển ứng dụng đa nền tảng', 4);

INSERT INTO sinh_vien (mssv, ho_ten, lop)
SELECT '23248010' || lpad(n::text, 5, '0'), 'Sinh viên ' || n, CASE WHEN n % 2 = 0 THEN 'D23KTPM01' ELSE 'D23CNTT04' END
FROM generate_series(1, 200) AS n;

INSERT INTO dang_ky (sinh_vien_id, khoa_hoc_id, diem)
SELECT s.id, k.id, round((5 + random() * 5)::numeric, 2)
FROM sinh_vien s CROSS JOIN khoa_hoc k
WHERE (s.id + k.id) % 3 <> 0;

-- Điểm trung bình, số sinh viên mỗi môn
SELECT k.ten AS mon, count(*) AS so_sinh_vien, round(avg(d.diem), 2) AS diem_tb
FROM dang_ky d JOIN khoa_hoc k ON k.id = d.khoa_hoc_id
GROUP BY k.ten ORDER BY diem_tb DESC;

-- Năm sinh viên có điểm trung bình cao nhất
SELECT s.mssv, s.ho_ten, s.lop, round(avg(d.diem), 2) AS diem_tb
FROM sinh_vien s JOIN dang_ky d ON d.sinh_vien_id = s.id
GROUP BY s.id ORDER BY diem_tb DESC LIMIT 5;
