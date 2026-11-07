# paperlens-data

Gói dữ liệu cho PaperLens: bài báo điện hóa mới (kèm η10, Tafel, độ bền… do AI trích từ tóm tắt) và tiêu chí chấm chung. Mỗi ngày một tác vụ định kỳ của Claude cập nhật `paperlens_pack.json` theo `TASK.md`.

Web PaperLens (bản file trên máy) tự tải `paperlens_pack.json` mỗi ngày một lần khi mở. Nhập tên repo này ở tab **Cài đặt AI & tra cứu → Gói dữ liệu GitHub**. Dữ liệu vẫn dùng được khi không còn AI; chỉ việc cập nhật hằng ngày cần Claude.

Repo chỉ chứa thông tin công khai của bài đã đăng và tiêu chí chấm chung, không chứa bản thảo hay kết quả chấm của người dùng.

- `paperlens_pack.json`: dữ liệu (định dạng ở `SCHEMA.md`)
- `tools/merge_pack.py`: gộp dữ liệu mới, lọc trùng, kiểm tra, tính mốc
- `TASK.md`: hướng dẫn cho tác vụ hằng ngày
- `log/`: nhật ký cập nhật
