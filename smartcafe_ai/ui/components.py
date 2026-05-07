import streamlit as st

def render_sidebar():
    """
    Renders the sidebar navigation.
    Returns the selected page.
    """
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#8D6E63" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
                <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
                <line x1="6" y1="1" x2="6" y2="4"></line>
                <line x1="10" y1="1" x2="10" y2="4"></line>
                <line x1="14" y1="1" x2="14" y2="4"></line>
            </svg>
            <h2 style="color: #8D6E63; margin-top: 10px; font-weight: 600;">SmartCafé AI</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    selected_page = st.sidebar.radio(
        "Chức năng",
        options=["Kiểm Kho", "AI Cố Vấn"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<small style='color: gray;'>Phiên bản 1.0.0</small>", unsafe_allow_html=True)
    
    return selected_page

def render_metric_card(title, value, delta=None):
    """
    Renders a clean metric card using Streamlit's built-in metric.
    """
    st.metric(label=title, value=value, delta=delta)
