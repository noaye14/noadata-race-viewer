import pandas as pd
import numpy as np
import streamlit as st

# -------------------------------------------------------
# APP CONFIGURATION
# -------------------------------------------------------
st.set_page_config(
    page_title="NOADATA Race Stats",
    layout="wide",
    page_icon="🏇",
)

# Custom header style
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
        font-family: "Segoe UI", Arial, sans-serif;
    }
    .title-bar {
        text-align: center;
        background-color: #004aad;
        color: white;
        padding: 0.8em;
        border-radius: 10px;
        font-size: 1.6em;
        font-weight: bold;
        margin-bottom: 1.2em;
    }
    .stSelectbox label {
        font-size: 1.1em !important;
        font-weight: 600 !important;
    }
    table {
        font-size: 0.9em !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title-bar">🏇 NOADATA Race Statistics Viewer</div>', unsafe_allow_html=True)

# -------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner="Loading race data…")
def load_data():
    url = "https://www.noadata.com/nhstatscard.html"
    tables = pd.read_html(url)
    df = tables[0]

    # Drop race_id column (case-insensitive)
    df.columns = [c.strip() for c in df.columns]
    race_id_col = [c for c in df.columns if c.lower() == "race_id"]
    if race_id_col:
        df = df.drop(columns=race_id_col)

    # Combine date/time for dropdown
    df["R_KEY"] = df["R_DATE"].astype(str) + " " + df["R_TIME"].astype(str)
    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Could not load data from NOADATA.\n\nError: {e}")
    st.stop()

# -------------------------------------------------------
# USER SELECTION
# -------------------------------------------------------
race_keys = sorted(df["R_KEY"].unique())
selected_race = st.selectbox("Select Race (Date + Time):", race_keys, index=None, placeholder="Choose a race...")

COLOR_COLS = ["T_SR21", "T_AE21", "T_SR90", "T_AE90", "J_SR21", "J_AE21"]

# -------------------------------------------------------
# DATA DISPLAY
# -------------------------------------------------------
if selected_race:
    race_df = df[df["R_KEY"] == selected_race].copy()

    # Exclude helper columns
    exclude = ["R_KEY"] + [c for c in race_df.columns if c.lower() == "race_id"]
    race_df = race_df[[c for c in race_df.columns if c not in exclude]]

    # Compute min/max for gradient columns
    minmax = {c: (race_df[c].min(), race_df[c].max()) for c in COLOR_COLS if c in race_df.columns}

    def style_row(row):
        styles = []
        for col, val in row.items():
            # Green–amber–red gradient
            if col in COLOR_COLS and not pd.isna(val):
                vmin, vmax = minmax[col]
                ratio = (val - vmin) / (vmax - vmin + 1e-9)
                ratio = np.clip(ratio, 0, 1)
                if ratio < 0.5:
                    r, g = 255, int(255 * (ratio * 2))
                else:
                    r, g = int(255 * (1 - (ratio - 0.5) * 2)), 255
                styles.append(f"background-color: rgb({r},{g},0);")
            # Turquoise if TCK_CHG == 'Y' or CLS_CHG starts with 'D'
            elif (col == "TCK_CHG" and str(val) == "Y") or (
                col == "CLS_CHG" and str(val).startswith("D")
            ):
                styles.append("background-color: #40E0D0;")
            else:
                styles.append("")
        return styles

    st.markdown("### 📊 Race Data Table")
    st.dataframe(
        race_df.style.apply(style_row, axis=1),
        use_container_width=True,
        height=600
    )

else:
    st.info("👆 Please select a race from the dropdown above.")

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------
st.markdown(
    """
    <div style='text-align:center; margin-top:20px; color:#666; font-size:0.9em;'>
        Data source: <a href='https://www.noadata.com/nhstatscard.html' target='_blank'>NOADATA</a> |
        Built with ❤️ using <a href='https://streamlit.io' target='_blank'>Streamlit</a>
    </div>
    """,
    unsafe_allow_html=True
)
