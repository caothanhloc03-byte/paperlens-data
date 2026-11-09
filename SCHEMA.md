# Định dạng `paperlens_pack.json`

```json
{
  "version": 1,
  "updated": "2026-11-08T03:20:00+00:00",
  "papers": [ { …bài báo… } ],
  "rules":  [ { …tiêu chí… } ],
  "bench":  { "HER": { "alkaline": { "eta10": {"n":120,"p25":60,"median":95,"p75":140,"best":18}, "tafel": {…}, "stab_h": {…} } } }
}
```

## Bài báo
| trường | ý nghĩa |
|---|---|
| title, doi, year, venue, url, cites | thông tin thư mục |
| abstract | một câu tóm tắt tự viết (tiếng Anh, ≤200 ký tự), không chép nguyên văn |
| reaction | HER, OER, ORR, CO2RR, NRR, HOR, OWS, other |
| electrolyte | acidic, alkaline, neutral hoặc null |
| material, mclass, synth | vật liệu, nhóm vật liệu, phương pháp tổng hợp |
| eta10, eta100 | quá thế (mV) ở 10 và 100 mA cm⁻² |
| tafel | mV dec⁻¹ |
| stab_h, stab_j | thời gian bền (h) và mật độ dòng khi đo bền (mA cm⁻²) |
| cell_v | điện áp cả pin (V) |
| h2_usd_kg | giá H₂ (USD/kg) nếu là bài kinh tế – kỹ thuật |
| src, added | nguồn tìm thấy, thời điểm thêm |

## Tiêu chí (`rules`)
`id` (bắt đầu bằng G), `field` (HER/OER/GEN), `sub` (mục con, ví dụ `7.4`), `text`, `basis`, `chk`, `status` (luôn `proposed`; người dùng duyệt trong web), `n` (số bài/nguồn ủng hộ; web dùng tiêu chí có `chk` và `n ≥ 2` để chấm thay AI).

Mục con hay dùng: 2.x Abstract · 3.1 nêu khoảng trống · 3.6 khoảng trống công nghiệp · 4.x tính mới · 5.x tổng hợp và thiết kế thí nghiệm (5.4 dãy mẫu một biến, 5.5 lặp lại/sai số) · 6.x cơ chế và lý giải (6.5 chứng minh lý thuyết) · 7.x hiệu năng (7.2 Tafel, 7.3 ECSA, 7.4 độ bền, 7.6 điều kiện đo, 7.7 so chuẩn) · 8.x đặc trưng vật liệu · 9.x hình · 10.x dữ liệu và tái lập · 11.x kinh tế – kỹ thuật · 12.x ngôn ngữ · 1.x cấu trúc. Danh sách đầy đủ ở tab "Sổ tay tiêu chí" của web.

## Phép kiểm máy `chk`
```
{"t":"text","sec":"abs|intro|methods|results|disc|concl|all","any":["regex",…],"all":["regex",…],"min":1}
{"t":"val","key":"eta10|etaHigh|tafel|cdl|stab|cycles|cell|fe","op":">=|<=|present","v":số}
{"t":"flag","key":"ir|rhe|refel|compTable|bench|highJ|electrolyte"}
{"t":"and"|"or","of":[…]}
{"t":"not","of":[…]}   (đảo kết quả phép kiểm đầu tiên; dùng cho tiêu chí có điều kiện: "nếu bài làm X thì phải có Y" → or(not(X), Y), để bài không làm X vẫn đạt)
```
Regex kiểu JavaScript, không phân biệt hoa thường, viết bằng tiếng Anh như trong bài báo. Đơn vị: eta mV; tafel mV dec⁻¹; cdl mF cm⁻²; stab giờ; cell V; fe %.
