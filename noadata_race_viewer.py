import pandas as pd
import numpy as np
import streamlit as st

# -----------------------------
# STEP 1: Load data
# -----------------------------
url = "https://www.noadata.com/nhstatscard.html"
st.title("🏇 NOADATA Race Statistics Viewer")

with st.spinner("Loading data..."):
    tables = pd.read_html(url)
df = tables[0]

# Drop race_id column (case-insensitive)
df.columns = [c.strip() for c in df.columns]
race_id_col = [c for c in df.columns if c.lower() == "race_id"]
if race_id_col:
    df = df.drop(columns=race_id_col)

# Combine date/time for dropdown
df["R_KEY"] = df["R_DATE"].astype(str) + " " + df["R_TIME"].astype(str)
race_keys = sorted(df["R_KEY"].unique())

# -----------------------------
# STEP 2: User selection
# -----------------------------
selected_race = st.selectbox("Select Race (Date + Time):", race_keys)

# Columns to apply gradient to
COLOR_COLS = ["T_SR21", "T_AE21", "T_SR90", "T_AE90", "J_SR21", "J_AE21"]

# -----------------------------
# STEP 3: Display function
# -----------------------------
if selected_race:
    race_df = df[df["R_KEY"] == selected_race].copy()

    # Exclude helper columns
    exclude = ["R_KEY"] + [c for c in race_df.columns if c.lower() == "race_id"]
    race_df = race_df[[c for c in race_df.columns if c not in exclude]]

    # Compute min/max for gradient columns
    minmax = {c: (race_df[c].min(), race_df[c].max()) for c in COLOR_COLS if c in race_df.columns}

    # Gradient and turquoise cell highlighting
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

    st.dataframe(
        race_df.style.apply(style_row, axis=1),
        use_container_width=True,
        height=600
    )
