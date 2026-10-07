import csv
from pathlib import Path

import cv2
import numpy as np

from starter.datasets import load_frame
from starter.projection import perturb_extrinsic, project_velo_to_image, overlay_points, draw_box2d


def compute_points_in_boxes(uv, mask, labels):
    """Đếm số lượng điểm (đã lọc qua FOV và depth) rơi vào bên trong 2D boxes."""
    uv_valid = uv  # uv đã được lọc bằng mask trong project_velo_to_image
    total_in_box = 0
    
    # Tạo một mask gộp cho tất cả các box
    in_any_box = np.zeros(len(uv_valid), dtype=bool)
    
    for obj in labels:
        x1, y1, x2, y2 = obj.bbox
        # Điểm rơi vào trong box này
        in_this_box = (uv_valid[:, 0] >= x1) & (uv_valid[:, 0] <= x2) & \
                      (uv_valid[:, 1] >= y1) & (uv_valid[:, 1] <= y2)
        in_any_box = in_any_box | in_this_box
        
    return int(np.sum(in_any_box))


def main():
    data_root = "data/kitti_mini"
    frame_id = "000011"
    
    # Load frame
    fr = load_frame(data_root, frame_id)
    points = fr["points"]
    calib = fr["calib"]
    image = fr["image"]
    labels = fr["labels"]
    
    # Thí nghiệm: Thay đổi Yaw (độ)
    yaw_levels = [0.0, 0.5, 1.0, 2.0, 3.0]
    
    csv_file = Path("results/yaw_perturb_sweep.csv")
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for yaw in yaw_levels:
        # Perturb
        calib_pert = perturb_extrinsic(calib, yaw_deg=yaw)
        
        # Project
        uv, depth, mask = project_velo_to_image(points, calib_pert, image.shape)
        
        # Tính toán metric
        points_in_fov = int(np.sum(mask))
        points_in_boxes = compute_points_in_boxes(uv, mask, labels)
        
        # Lưu kết quả
        results.append({
            "Yaw_deg": yaw,
            "Points_in_FOV": points_in_fov,
            "Points_in_Boxes": points_in_boxes,
            "Ratio_in_Boxes_pct": round(points_in_boxes / points_in_fov * 100, 2) if points_in_fov > 0 else 0
        })
        
        # Vẽ và lưu ảnh (chọn mức 0 và mức 3 làm minh hoạ và failure case)
        if yaw in [0.0, 3.0]:
            vis = overlay_points(image, uv, depth)
            for obj in labels:
                vis = draw_box2d(vis, obj.bbox, label=obj.type)
                
            prefix = "demo" if yaw == 0.0 else "fail"
            out_path = Path(f"results/figures/{prefix}_{frame_id}_yaw_{yaw}deg.png")
            cv2.imwrite(str(out_path), vis)
            print(f"Lưu ảnh: {out_path}")
            
    # Viết ra CSV
    with open(csv_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Yaw_deg", "Points_in_FOV", "Points_in_Boxes", "Ratio_in_Boxes_pct"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Đã lưu kết quả ra {csv_file}")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
