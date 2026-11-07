# Tác vụ hằng ngày: cập nhật gói dữ liệu PaperLens

Bạn (Claude) chạy tác vụ này mỗi ngày trong một phiên mới. Mục tiêu: bổ sung bài báo điện hóa mới (kèm số liệu do AI trích từ tóm tắt) và, mỗi Chủ nhật, các tiêu chí chấm chung vào `paperlens_pack.json`. Web PaperLens bản trên máy tự tải file này để chấm bài **không cần AI**.

Quy tắc an toàn: chỉ ghi thông tin công khai của bài đã đăng (tiêu đề, DOI, năm, tạp chí, tóm tắt ≤600 ký tự, số liệu trong tóm tắt). Không ghi gì về bản thảo của người dùng. Không sửa file nào ngoài `paperlens_pack.json`, `log/` và các file tạm.

## 1. Tìm bài mới (khoảng 20–60 bài/ngày)
Dùng công cụ `search` của SciSpace. Chạy 8 truy vấn, mỗi truy vấn tối đa 15 kết quả, lọc năm hiện tại (thêm `year:<năm nay>` vào truy vấn):
- hydrogen evolution reaction electrocatalyst overpotential alkaline
- hydrogen evolution reaction electrocatalyst acidic
- oxygen evolution reaction electrocatalyst overpotential
- transition metal phosphide / sulfide / selenide electrocatalyst water splitting
- single-atom catalyst hydrogen evolution
- high-entropy alloy electrocatalyst water splitting
- anion exchange membrane water electrolyzer catalyst stability
- techno-economic analysis levelized cost of hydrogen electrolysis

Nếu SciSpace lỗi, dùng WebFetch tới OpenAlex (không cần khóa):
`https://api.openalex.org/works?search=<từ khóa>&filter=from_publication_date:<7 ngày trước>&sort=publication_date:desc&per-page=25&select=id,doi,title,publication_year,primary_location,cited_by_count,abstract_inverted_index`

Bỏ bài đã có trong `paperlens_pack.json` (so DOI, hoặc tiêu đề khi không có DOI).

## 2. Trích số liệu (chỉ từ tóm tắt, không suy đoán)
Với mỗi bài, tạo một mục theo `SCHEMA.md`: `reaction` (HER/OER/ORR/CO2RR/NRR/HOR/OWS/other), `electrolyte` (acidic/alkaline/neutral), `material`, `mclass` (phosphide, sulfide, oxide, hydroxide, alloy, single-atom, carbide, nitride, MOF-derived, other), `synth`, và các số `eta10` (mV ở 10 mA cm⁻²), `eta100`, `tafel` (mV dec⁻¹), `stab_h`, `stab_j`, `cell_v`, `h2_usd_kg`. Giá trị nào tóm tắt không nêu thì để `null`. Ghi `src` là nguồn tìm thấy.
Lưu thành `tmp/new_papers.json` (một mảng JSON).

## 3. Mỗi Chủ nhật: tiêu chí chấm chung
Đọc các bài trong 7 ngày qua và các tiêu chí đã có trong gói. Đề xuất tối đa 5 **tiêu chí chấm tổng quát** mà phản biện lĩnh vực này đang đòi hỏi (ví dụ ngưỡng độ bền, phép đo bắt buộc, cách báo cáo). Mỗi tiêu chí gắn với một mục con của bộ 12 tiêu chí PaperLens (xem `SCHEMA.md`), kèm `chk` là phép kiểm máy, và `n` là số bài trong tuần ủng hộ tiêu chí đó. Không nêu tên vật liệu hay công thức cụ thể. Lưu `tmp/new_rules.json`.
Nếu bài mới ủng hộ thêm tiêu chí đã có, ghi `tmp/confirm.json` dạng `{"G…": số_bài}`.

## 4. Gộp và đẩy lên
```
python3 tools/merge_pack.py --papers tmp/new_papers.json [--rules tmp/new_rules.json] [--confirm tmp/confirm.json]
```
Script tự lọc trùng, bỏ số liệu ngoài khoảng hợp lý, bỏ tiêu chí chứa công thức vật liệu, kiểm tra `chk`, tính lại mốc (`bench`). Ghi một dòng vào `log/<YYYY-MM>.md`: ngày, số bài thêm, số tiêu chí thêm, nguồn dùng, lỗi nếu có. Xóa thư mục `tmp/`, commit với thông điệp `data: <ngày> +<n> papers` và push lên nhánh `main`.

Nếu không push được hoặc không tìm được bài nào, vẫn ghi log và báo lý do ở cuối phiên.
