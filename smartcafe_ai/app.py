import streamlit as st

# Cấu hình trang phải đặt đầu tiên
st.set_page_config(
    page_title="SmartCafé AI",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.components import render_sidebar
import ui.page_inventory as page_inventory
import ui.page_advisor as page_advisor

def main():
    # Sidebar điều hướng
    selected_page = render_sidebar()

    # Định tuyến
    if selected_page == "Kiểm Kho":
        page_inventory.render()
    elif selected_page == "AI Cố Vấn":
        page_advisor.render()

if __name__ == "__main__":
    main()
