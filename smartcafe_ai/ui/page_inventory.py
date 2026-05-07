# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
from PIL import Image
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import cv2
from src.vision import SmartCafeVision
from src.database import save_inventory_to_csv, get_inventory_history

@st.cache_resource
def load_vision_model():
    return SmartCafeVision()

danh_sach_mat_hang = ['cafe_hat', 'cafe_xay', 'ly_giay', 'ly_nhua', 'sua_dac']
display_names = {
    'cafe_hat': 'Cà phê hạt',
    'cafe_xay': 'Cà phê xay',
    'ly_giay': 'Ly giấy',
    'ly_nhua': 'Ly nhựa',
    'sua_dac': 'Sữa đặc'
}

def render():
    for item in danh_sach_mat_hang:
        if item not in st.session_state:
            st.session_state[item] = 0

    with st.sidebar:
        st.markdown("### ⚙️ Cài đặt hệ thống")
        conf_threshold = st.slider("Độ nhạy AI (Confidence)", min_value=0.05, max_value=1.0, value=0.40, step=0.05)
        allowed_classes = st.multiselect(
            "🔍 Bộ lọc nhận diện",
            options=danh_sach_mat_hang,
            default=danh_sach_mat_hang,
            format_func=lambda x: display_names.get(x, x)
        )

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
        
        image_bytes = image_source.getvalue()
        current_state_hash = hash((image_bytes, conf_threshold, tuple(allowed_classes)))
        
        if st.session_state.get('last_state_hash') != current_state_hash:
            with st.spinner('Đang phân tích hình ảnh...'):
                # Chạy qua model YOLO
                processed_frame, inventory_counts = vision_core.process_frame(frame_bgr, conf_threshold, allowed_classes)
                
                # Convert BGR back to RGB for hiển thị
                st.session_state['processed_frame_rgb'] = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                
                for item, count in inventory_counts.items():
                    st.session_state[item] = count
                    
                st.session_state['last_state_hash'] = current_state_hash
                
        if 'processed_frame_rgb' in st.session_state:
            with col1:
                st.markdown("**Ảnh đầu vào (Đã qua xử lý)**")
                st.image(st.session_state['processed_frame_rgb'], use_container_width=True)
                
            with col2:
                st.markdown("**Số liệu chi tiết**")
                st.markdown("<p style='color: #D2691E; font-size: 14px;'><b>✍️ Tùy chỉnh kết quả:</b> Sửa số lượng nếu AI đếm sai.</p>", unsafe_allow_html=True)
                
                for item in danh_sach_mat_hang:
                    st.number_input(
                        label=display_names.get(item, item),
                        min_value=0,
                        step=1,
                        key=item
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                chart_data = pd.DataFrame(
                    [st.session_state[item] for item in danh_sach_mat_hang],
                    index=[display_names.get(item, item) for item in danh_sach_mat_hang],
                    columns=['Số lượng']
                )
                st.bar_chart(chart_data)
                
                total_items = sum(st.session_state[item] for item in danh_sach_mat_hang)
                if total_items > 0:
                    st.success(f"Hoàn tất! Tổng cộng {total_items} vật thể.")
                else:
                    st.warning("Không phát hiện được vật thể nào.")
                    
                if st.button("Lưu vào cơ sở dữ liệu", type="primary", use_container_width=True):
                    final_counts = {item: st.session_state[item] for item in danh_sach_mat_hang}
                    success = save_inventory_to_csv(final_counts)
                    if success:
                        st.toast("Đã lưu dữ liệu kiểm kho vào CSV thành công!")
                        
    else:
        for item in danh_sach_mat_hang:
            st.session_state[item] = 0
        st.session_state['last_state_hash'] = None
