import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="wide")

# Load your data
@st.cache_data
def load_data():
    return pd.read_excel("DB.xlsx")

df = load_data()

st.title("MTE Calculator")

# -----------------------------
# STEP 1: Select Model
# -----------------------------
models = sorted(df["Model"].dropna().unique())
selected_model = st.selectbox("Select Model", models)

# -----------------------------
# STEP 2: Select Sub Model
# -----------------------------
if selected_model:
    sub_df = df[df["Model"] == selected_model]
    sub_models = sorted(sub_df["Sub Model"].dropna().unique())

    selected_sub_model = st.selectbox("Select Sub Model", sub_models)

# -----------------------------
# STEP 3: Select Variant
# -----------------------------
if selected_sub_model:
    variant_df = sub_df[sub_df["Sub Model"] == selected_sub_model]
    variants = sorted(variant_df["Variant"].dropna().unique())

    selected_variant = st.selectbox("Select Variant", variants)

# -----------------------------
# RESULT
# -----------------------------
if selected_variant:
    result_df = variant_df[variant_df["Variant"] == selected_variant]
    st.dataframe(result_df)
