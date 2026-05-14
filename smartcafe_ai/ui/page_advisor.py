import streamlit as st
import pandas as pd

from src.database import get_inventory_history
from ui.components import render_metric_card

DISPLAY_NAMES = {
    "cafe_hat": "Cà phê hạt",
    "cafe_xay": "Cà phê xay",
    "ly_giay": "Ly giấy",
    "ly_nhua": "Ly nhựa",
    "sua_dac": "Sữa đặc",
}


def _build_forecast(history_df: pd.DataFrame, days: int) -> pd.DataFrame:
    if history_df.empty:
        return pd.DataFrame()

    history_df = history_df.copy()
    history_df["Thời gian"] = pd.to_datetime(history_df["Thời gian"], errors="coerce")
    history_df = history_df.dropna(subset=["Thời gian"]).sort_values("Thời gian")
    if history_df.empty:
        return pd.DataFrame()

    latest = history_df.iloc[-1]
    previous = history_df.iloc[-2] if len(history_df) > 1 else latest

    rows = []
    for item in DISPLAY_NAMES.keys():
        curr = int(latest.get(item, 0) or 0)
        prev = int(previous.get(item, 0) or 0)
        daily_usage = max(prev - curr, 0)
        predicted_need = daily_usage * days
        safety_stock = max(int(predicted_need * 0.2), 1) if predicted_need > 0 else 0
        recommend = max(predicted_need + safety_stock - curr, 0)
        status = "Ổn định" if recommend == 0 else "Cần nhập"
        if curr == 0 and predicted_need > 0:
            status = "Cần nhập gấp"
        rows.append(
            {
                "Mặt hàng": DISPLAY_NAMES[item],
                "Tồn kho (hiện tại)": curr,
                f"Dự báo ({days} ngày tới)": predicted_need,
                "Đề xuất nhập thêm": recommend,
                "Trạng thái": status,
            }
        )

    return pd.DataFrame(rows)


def render():
    st.title("AI Cố Vấn")
    st.markdown("Dự báo nhu cầu từ dữ liệu kiểm kho thực tế và đề xuất nhập hàng.")
    st.markdown("---")

    history_df = get_inventory_history(limit=90)
    if history_df.empty:
        st.info("Chưa có dữ liệu kiểm kho để phân tích. Vui lòng kiểm kho trước.")
        return

    forecast_period = st.selectbox("Thời gian dự báo", ["7 ngày tới", "14 ngày tới", "30 ngày tới"])
    days_to_predict = int(forecast_period.split()[0])

    forecast_df = _build_forecast(history_df, days_to_predict)
    if forecast_df.empty:
        st.info("Không đủ dữ liệu hợp lệ để dự báo.")
        return

    total_current = int(forecast_df["Tồn kho (hiện tại)"].sum())
    total_predicted = int(forecast_df[f"Dự báo ({days_to_predict} ngày tới)"].sum())
    total_recommend = int(forecast_df["Đề xuất nhập thêm"].sum())

    st.markdown("### Tổng quan")
    metric_cols = st.columns(3)
    with metric_cols[0]:
        render_metric_card("Tồn kho hiện tại", f"{total_current}")
    with metric_cols[1]:
        render_metric_card("Dự báo tiêu thụ", f"{total_predicted}")
    with metric_cols[2]:
        render_metric_card("Đề xuất nhập thêm", f"{total_recommend}")

    st.markdown("### Biểu đồ khuyến nghị nhập hàng")
    st.bar_chart(forecast_df.set_index("Mặt hàng")[["Đề xuất nhập thêm"]])

    st.markdown("### Bảng khuyến nghị")
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)
