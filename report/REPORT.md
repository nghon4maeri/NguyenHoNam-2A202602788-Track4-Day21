# Báo cáo Day 6: LiDAR-Camera Projection QA

- **Họ tên:** Nguyen Ho Nam
- **MSSV:** 2A202602788
- **Lớp:** K4
- **Link repo:** https://github.com/nghon4maeri/NguyenHoNam-2A202602788-Track4-Day21
- **Topic:** A — LiDAR-camera projection QA
- **Dataset:** data/kitti_mini
- **Các frame đã dùng:** 000011

## 1. Claim

Lệch yaw 3° làm số lượng điểm LiDAR rơi vào trong 2D bounding box của các vật thể thay đổi từ 1628 điểm lên 1754 điểm (sai lệch gần 8%), gây hiện tượng bóng ma (ghosting) trên hình ảnh overlay và không thể hiện đúng hình dạng thật của vật thể trong không gian.

## 2. Evidence

Kết quả thí nghiệm quét độ lệch góc Yaw từ 0.0 đến 3.0 độ. File log kết quả: `results/yaw_perturb_sweep.csv`.

| Cấu hình / mức perturb (Yaw deg) | Số điểm trong FOV | Số điểm trong 2D Boxes | Tỷ lệ trong Boxes (%) |
|---|---|---|---|
| 0.0 | 19946 | 1628 | 8.16 |
| 0.5 | 19946 | 1649 | 8.27 |
| 1.0 | 19952 | 1656 | 8.30 |
| 2.0 | 19963 | 1723 | 8.63 |
| 3.0 | 19948 | 1754 | 8.79 |

![demo](../results/figures/demo_000011_yaw_0.0deg.png)

## 3. Failure case

Khi góc Yaw lệch 3 độ, toàn bộ điểm chiếu LiDAR bị trượt hẳn sang mép của vật thể. Trong hình dưới đây, đám mây điểm của chiếc xe hoàn toàn không còn khớp với bbox 2D, khiến dữ liệu bị dóng hàng sai.

Lỗi này thuộc lớp **Geometry (Hình học)**: Ma trận ngoại lai (Extrinsic matrix) biểu diễn sai phép quay giữa hệ toạ độ LiDAR và hệ toạ độ Camera, khiến tọa độ 3D bị chiếu lệch xuống mặt phẳng 2D.

![failure](../results/figures/fail_000011_yaw_3.0deg.png)

## 4. Khuyến nghị nếu triển khai thật

Trong môi trường xe tự hành (ADAS), cảm biến thường xuyên chịu rung lắc cơ học. Nếu chỉ sử dụng calibration tĩnh từ nhà máy, sau một thời gian dữ liệu sẽ lệch như failure case phía trên, làm nhiễu hệ thống sensor fusion. 
Khuyến nghị: Cần phát triển thêm một module online calibration (tự động cân chỉnh) để liên tục tính toán và cập nhật lại extrinsic trong thời gian thực.

## 5. Cách chạy lại

Các lệnh tái tạo lại toàn bộ kết quả từ repo sạch.

```bash
# Chạy tạo ảnh overlay và file số liệu
$env:PYTHONIOENCODING="utf-8"
.\.venv_openpcdet\Scripts\python.exe -m src.topic_a_experiment
```

## 6. Khai báo sử dụng AI

| Công cụ | Dùng cho việc gì | Bạn đã kiểm chứng thế nào |
|---|---|---|
| Antigravity (Gemini) | Hỗ trợ code projection, xây dựng pipeline đo đạc và phân tích số liệu | Chạy thử nghiệm thành công, xem trực tiếp ảnh kết quả và logic của file Python để xác nhận tính chính xác. |
