# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
import cv2
from src.vision import SmartCafeVision
from src.database import save_inventory_to_csv, get_inventory_history

@st.cache_resource
def load_vision_model():
    return SmartCafeVision()

def render():
    st.title("Kiểm Kho")
    st.markdown("Hệ thống nhận diện và đếm số lượng hàng tồn kho tự động bằng Computer Vision.")
    
    st.markdown("---")
    
    # Sử dụng Tabs thay vì selectbox để chuyển đổi mượt mà
    tab1, tab2, tab3 = st.tabs(["Tải ảnh từ thiết bị", "Chụp ảnh trực tiếp", "Lịch sử kiểm kho"])
    
    image_source = None
    
    with tab1:
        uploaded_file = st.file_uploader("Chọn ảnh kho hàng để phân tích", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image_source = uploaded_file

    with tab2:
        camera_file = st.camera_input("Chụp ảnh kho hàng trực tiếp từ thiết bị")
        if camera_file is not None:
            image_source = camera_file
            
    with tab3:
        st.markdown("### Lịch sử Kiểm kho")
        df_history = get_inventory_history()
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có dữ liệu lịch sử nào được lưu.")

    if image_source is not None:
        st.markdown("### Kết quả Phân tích")
        col1, col2 = st.columns([1.5, 1])
        
        vision_core = load_vision_model()
        
        # Đọc ảnh từ file nguồn và đảm bảo định dạng RGB (Tránh lỗi với ảnh PNG có kênh alpha)
        image = Image.open(image_source).convert('RGB')
        frame = np.array(image)
        # Convert RGB (PIL) to BGR (OpenCV)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        with st.spinner('Đang phân tích hình ảnh...'):
            # Chạy qua model YOLO
            processed_frame, inventory_counts = vision_core.process_frame(frame_bgr)
            
            # Convert BGR back to RGB for hiển thị
            processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            with col1:
                st.markdown("**Ảnh đầu vào (Đã qua xử lý)**")
                st.image(processed_frame_rgb, use_container_width=True)
                
            with col2:
                st.markdown("**Số liệu chi tiết**")
                
                # Tạo dataframe từ kết quả thật
                # Định dạng lại tên cho đẹp
                display_names = {
                    'cafe_hat': 'Cà phê hạt',
                    'cafe_xay': 'Cà phê xay',
                    'ly_giay': 'Ly giấy',
                    'ly_nhua': 'Ly nhựa',
                    'sua_dac': 'Sữa đặc'
                }
                
                # Lọc ra những mặt hàng có số lượng > 0 hoặc hiển thị tất cả
                data_list = [{"Mặt hàng": display_names.get(k, k), "Số lượng": v} for k, v in inventory_counts.items()]
                result_df = pd.DataFrame(data_list)
                
                st.dataframe(result_df, use_container_width=True, hide_index=True)
                
                total_items = sum(inventory_counts.values())
                if total_items > 0:
                    st.success(f"Hoàn tất! Phát hiện tổng cộng {total_items} vật thể.")
                else:
                    st.warning("Không phát hiện được vật thể nào.")
                    
                if st.button("Lưu vào cơ sở dữ liệu", type="primary", use_container_width=True):
                    success = save_inventory_to_csv(inventory_counts)
                    if success:
                        st.toast("Đã lưu dữ liệu kiểm kho vào CSV thành công!")
