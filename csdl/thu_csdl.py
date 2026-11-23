# Nguyễn Tâm Bình - 2324801030003
# Thử cơ sở dữ liệu PostgreSQL: kết nối, chạy dữ liệu mẫu, đo ghi/đọc, giao dịch, ràng buộc
# Dùng: python thu_csdl.py "postgresql://app:<mật khẩu>@<host>:<cổng>/app"
import pathlib
import sys
import time

try:
    import psycopg
except ImportError:
    sys.exit('Chưa có thư viện psycopg. Cài bằng: pip install "psycopg[binary]"')


def main():
    if len(sys.argv) != 2:
        sys.exit('Dùng: python thu_csdl.py "postgresql://app:<mật khẩu>@<host>:<cổng>/app"')
    t0 = time.perf_counter()
    with psycopg.connect(sys.argv[1], connect_timeout=10) as conn:
        print(f'Kết nối được sau {(time.perf_counter() - t0) * 1000:.0f} ms')
        print('Máy chủ:', conn.execute('SELECT version()').fetchone()[0].split(',')[0])

        sql = (pathlib.Path(__file__).parent / 'mau.sql').read_text(encoding='utf-8')
        t = time.perf_counter()
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f'Tạo bảng và dữ liệu mẫu: {(time.perf_counter() - t) * 1000:.0f} ms')

        print('\nĐiểm trung bình từng môn:')
        for mon, so, tb in conn.execute('SELECT k.ten, count(*), round(avg(d.diem), 2) FROM dang_ky d JOIN khoa_hoc k ON k.id = d.khoa_hoc_id GROUP BY k.ten ORDER BY 3 DESC'):
            print(f'  {mon:<34} {so:>4} sinh viên   điểm TB {tb}')

        t = time.perf_counter()
        with conn.cursor() as cur:
            cur.executemany('INSERT INTO sinh_vien (mssv, ho_ten, lop) VALUES (%s, %s, %s)', [(f'99{n:011d}', f'Ghi thử {n}', 'THU') for n in range(5000)])
        conn.commit()
        ghi = time.perf_counter() - t
        t = time.perf_counter()
        for _ in range(200):
            conn.execute("SELECT count(*) FROM sinh_vien WHERE lop = 'THU'").fetchone()
        doc = time.perf_counter() - t
        print(f'\nGhi 5.000 dòng: {ghi:.2f} s ({5000 / ghi:,.0f} dòng/s)')
        print(f'200 truy vấn đếm: {doc:.2f} s ({doc / 200 * 1000:.1f} ms/truy vấn)')

        try:
            with conn.transaction():
                conn.execute("INSERT INTO sinh_vien (mssv, ho_ten, lop) VALUES ('GIAODICH', 'Sẽ bị hủy', 'THU')")
                conn.execute("INSERT INTO dang_ky (sinh_vien_id, khoa_hoc_id, diem) VALUES (1, 1, 11)")
        except psycopg.IntegrityError:
            con_lai = conn.execute("SELECT count(*) FROM sinh_vien WHERE mssv = 'GIAODICH'").fetchone()[0]
            print(f'\nGiao dịch có điểm 11 bị ràng buộc CHECK chặn, dòng thêm trước đó bị hủy theo: còn {con_lai} dòng')

        conn.execute("DELETE FROM sinh_vien WHERE lop = 'THU'")
        conn.commit()
        bang = conn.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'").fetchone()[0]
        print(f'\nXong: {bang} bảng trong schema public, dữ liệu mẫu giữ lại để xem bằng psql hoặc DBeaver.')


if __name__ == '__main__':
    main()
