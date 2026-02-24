import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="wide")

st.title("MTE Calculator")

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    df = pd.read_excel("ken_DATA.xlsx")  # change to DB.xlsx if needed
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Error loading Excel file.")
    st.stop()

# =========================
# CHECK REQUIRED COLUMNS
# =========================

st.write("Available Columns in Excel:", df.columns.tolist())

#  Change these names if needed to match your Excel exactly
MODEL_COL = "Model"
SUBMODEL_COL = "SubModel"
VARIANT_COL = "Variant"

if MODEL_COL not in df.columns:
    st.error(f"Column '{MODEL_COL}' not found in Excel.")
    st.stop()

# =========================
# MODEL SELECTION
# =========================

models = sorted(df[MODEL_COL].dropna().unique())

selected_model = st.selectbox("Select Model", models)

# =========================
# SUB MODEL SELECTION
# =========================

filtered_model_df = df[df[MODEL_COL] == selected_model]

if SUBMODEL_COL in df.columns:
    submodels = sorted(filtered_model_df[SUBMODEL_COL].dropna().unique())
    
    selected_submodel = st.selectbox("Select Sub Model", submodels)
    
    filtered_sub_df = filtered_model_df[
        filtered_model_df[SUBMODEL_COL] == selected_submodel
    ]
else:
    filtered_sub_df = filtered_model_df

# =========================
# VARIANT SELECTION
# =========================

if VARIANT_COL in df.columns:
    variants = sorted(filtered_sub_df[VARIANT_COL].dropna().unique())
    
    selected_variant = st.selectbox("Select Variant", variants)
    
    final_df = filtered_sub_df[
        filtered_sub_df[VARIANT_COL] == selected_variant
    ]
else:
    final_df = filtered_sub_df

# =========================
# RESULT
# =========================

st.subheader("Filtered Result")
st.dataframe(final_df, use_container_width=True)
