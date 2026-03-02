import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="centered")

# ---------------------------------------------------
# LOAD DB1.xlsx (3 sheets)
# ---------------------------------------------------
@st.cache_data
def load_db():
    try:
        xls = pd.ExcelFile("DB1.xlsx")

        models_df = pd.read_excel(xls, sheet_name="models")
        variants_df = pd.read_excel(xls, sheet_name="variants")

        # Clean text columns
        for col in models_df.columns:
            models_df[col] = models_df[col].astype(str).str.strip()

        for col in variants_df.columns:
            variants_df[col] = variants_df[col].astype(str).str.strip()

        variants_df["MTE"] = pd.to_numeric(variants_df["MTE"], errors="coerce")

        return models_df, variants_df

    except Exception as e:
        st.error(f"DB1.xlsx error: {e}")
        st.stop()


# ---------------------------------------------------
# LOAD ken_DATA.xlsx
# ---------------------------------------------------
@st.cache_data
def load_ken():
    try:
        df = pd.read_excel("ken_DATA.xlsx")
        df.columns = df.columns.str.strip()
        df["Equipment Code"] = df["Equipment Code"].astype(str).str.strip()
        return df

    except Exception as e:
        st.error(f"ken_DATA.xlsx error: {e}")
        st.stop()


models_df, variants_df = load_db()
ken_df = load_ken()
