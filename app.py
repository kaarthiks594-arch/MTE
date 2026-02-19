import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="wide")


@st.cache_data
def load_db():
    xls = pd.ExcelFile("DB.xlsx")
    modules_df = pd.read_excel(xls, sheet_name="modules")
    models_df = pd.read_excel(xls, sheet_name="models")
    variants_df = pd.read_excel(xls, sheet_name="variants")

    modules_df["module_id"] = modules_df["module_id"].astype(str).str.strip()
    models_df["model_id"] = models_df["model_id"].astype(str).str.strip()
    models_df["module_id"] = models_df["module_id"].astype(str).str.strip()
    variants_df["model_id"] = variants_df["model_id"].astype(str).str.strip()

    return modules_df, models_df, variants_df


# ---------------------------------
# LOAD KEN DATA
# ---------------------------------
@st.cache_data
def load_ken():
    df = pd.read_excel("ken_DATA.xlsx")
    df["Equipment Code"] = df["Equipment Code"].astype(str).str.strip()

    equipment_codes = df["Equipment Code"].dropna().unique().tolist()
    modules = [
        col.strip() for col in df.columns
        if col.lower().strip() not in ["equipment code", "index"]
    ]

    return df, equipment_codes, modules


modules_df, models_df, variants_df = load_db()
ken_df, equipment_codes, ken_modules = load_ken()

# ---------------------------------
# UI
# ---------------------------------
st.title("🔢 MTE Calculator")

col1, col2 = st.columns(2)

with col1:
    equipment_code = st.selectbox("Select Equipment Code", equipment_codes)

with col2:
    module_name = st.selectbox("Select Module", ken_modules)

# ---------------------------------
# KEN LOOKUP
# ---------------------------------
if equipment_code and module_name:
    row = ken_df.loc[ken_df["Equipment Code"] == equipment_code]

    if not row.empty:
        matched_column = None
        for col in ken_df.columns:
            if col.lower().strip() == module_name.lower().strip():
                matched_column = col
                break

        if matched_column:
            model_name = str(row.iloc[0][matched_column]).strip()

            if model_name and model_name.lower() != "nan":

                st.success(f"Model Found: {model_name}")

                # get variants
                model_row = models_df.loc[
                    models_df["model_name"] == model_name
                ]

                if not model_row.empty:
                    model_id = model_row.iloc[0]["model_id"]

                    model_variants = variants_df.loc[
                        variants_df["model_id"] == model_id
                    ]

                    variant_options = model_variants["variant_name"].tolist()

                    selected_variants = st.multiselect(
                        "Select Variants",
                        variant_options
                    )

                    if selected_variants:
                        selected_rows = model_variants[
                            model_variants["variant_name"].isin(selected_variants)
                        ]

                        total_mte = round(selected_rows["MTE"].sum(), 3)

                        st.subheader("Selected Variants")
                        st.dataframe(selected_rows[["variant_name", "MTE"]])

                        st.success(f"Total MTE: {total_mte}")

            else:
                st.error("No model found for this module")
        else:
            st.error("Invalid module selected")
    else:
        st.error("Equipment code not found")
