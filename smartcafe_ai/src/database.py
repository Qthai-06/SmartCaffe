import pandas as pd
import datetime
import os

def save_inventory_to_csv(inventory_counts):
    """
    Ghi dữ liệu kiểm kho xuống file data/inventory.csv
    
    Args:
        inventory_counts (dict): Dictionary chứa số lượng đếm được của các mặt hàng.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Sử dụng CSV theo yêu cầu của nhóm
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_file_path = os.path.join(data_dir, "inventory.csv")
    
    # 1. Lấy thời gian hiện tại format chuẩn
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Các mặt hàng được định nghĩa sẵn
    danh_sach_mat_hang = ['cafe_hat', 'cafe_xay', 'ly_giay', 'ly_nhua', 'sua_dac']
    
    # 2. Đọc file cũ hoặc tạo DataFrame mới
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        # Tạo DataFrame với các cột mới
        cols = ["Thời gian"] + danh_sach_mat_hang
        df = pd.DataFrame(columns=cols)
        
    # 3. Thêm dữ liệu mới từ tham số
    new_data = {"Thời gian": [now]}
    for item in danh_sach_mat_hang:
        new_data[item] = [inventory_counts.get(item, 0)]
        
    new_row = pd.DataFrame(new_data)
    
    # Dùng pd.concat để nối row thay cho append đã bị deprecated
    if not df.empty:
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    
    # 4. Lưu lại đè lên file
    df.to_csv(csv_file_path, index=False)
    
    return True

def get_inventory_history():
    """
    Lấy dữ liệu lịch sử từ file CSV.
    
    Returns:
        pd.DataFrame: Dữ liệu lịch sử kiểm kho.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file_path = os.path.join(base_dir, "data", "inventory.csv")
    
    try:
        df_history = pd.read_csv(csv_file_path)
        # Sắp xếp để xem dữ liệu mới nhất ở trên cùng
        if not df_history.empty and "Thời gian" in df_history.columns:
            df_history = df_history.sort_values(by="Thời gian", ascending=False)
        return df_history
    except FileNotFoundError:
        return pd.DataFrame() # Trả về DataFrame rỗng nếu chưa có file
