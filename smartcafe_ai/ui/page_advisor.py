import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ui.components import render_metric_card

def render():
    st.title("AI Cố Vấn")
    st.markdown("Dự báo nhu cầu tiêu thụ dựa trên dữ liệu lịch sử và đề xuất kế hoạch nhập hàng tối ưu.")
    
    st.markdown("---")
    
    # Bộ lọc
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        selected_item = st.selectbox(
            "Chọn mặt hàng phân tích",
            ["Cà phê hạt (Túi)", "Sữa đặc (Hộp)", "Ly nhựa (Cái)", "Đường (Gói)"]
        )
    with col_filter2:
        forecast_period = st.selectbox(
            "Thời gian dự báo",
            ["7 ngày tới", "14 ngày tới", "30 ngày tới"]
        )
        
    st.markdown("### Tổng quan")
    metric_cols = st.columns(3)
    with metric_cols[0]:
        render_metric_card("Tiêu thụ tuần trước", "45 Túi", "12%")
    with metric_cols[1]:
        render_metric_card("Dự báo tuần tới", "52 Túi", "15%")
    with metric_cols[2]:
        render_metric_card("Tồn kho hiện tại", "15 Túi", "-8%")
        
    st.markdown("### Biểu đồ Dự báo")
    
    # Tạo dữ liệu giả cho Plotly
    dates_past = pd.date_range(end=pd.Timestamp.today(), periods=30)
    past_values = np.random.randint(3, 10, size=30)
    
    days_to_predict = int(forecast_period.split()[0])
    dates_future = pd.date_range(start=pd.Timestamp.today(), periods=days_to_predict+1)[1:]
    future_values = np.random.randint(5, 12, size=days_to_predict)
    upper_bound = future_values + 2
    lower_bound = future_values - 2

    # Vẽ biểu đồ với Plotly
    fig = go.Figure()
    
    # Dữ liệu lịch sử
    fig.add_trace(go.Scatter(
        x=dates_past, y=past_values,
        mode='lines+markers',
        name='Thực tế',
        line=dict(color='#8D6E63', width=2)
    ))
    
    # Dữ liệu dự báo
    fig.add_trace(go.Scatter(
        x=dates_future, y=future_values,
        mode='lines+markers',
        name='Dự báo',
        line=dict(color='#E57373', width=2, dash='dash')
    ))
    
    # Vùng tin cậy
    fig.add_trace(go.Scatter(
        x=dates_future.tolist() + dates_future.tolist()[::-1],
        y=upper_bound.tolist() + lower_bound.tolist()[::-1],
        fill='toself',
        fillcolor='rgba(229, 115, 115, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='Vùng biến động'
    ))

    fig.update_layout(
        xaxis_title="Thời gian",
        yaxis_title="Số lượng",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Đề xuất Kế hoạch Nhập hàng")
    st.info("Hệ thống phân tích mức độ tiêu thụ và tồn kho hiện tại để đưa ra gợi ý nhập hàng phù hợp.")
    
    suggestion_data = pd.DataFrame({
        "Mặt hàng": ["Cà phê hạt", "Sữa đặc", "Ly nhựa"],
        "Tồn kho (hiện tại)": [15, 8, 200],
        "Dự báo (7 ngày tới)": [52, 40, 800],
        "Đề xuất nhập thêm": [40, 35, 700],
        "Trạng thái": ["Cần nhập gấp", "Cần nhập", "Cần nhập"]
    })
    
    st.dataframe(suggestion_data, use_container_width=True, hide_index=True)
