import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="centered")

# ---------------------------------------------------
# LOAD DATABASE FILE
# ---------------------------------------------------
@st.cache_data
def load_db():
    xls = pd.ExcelFile("DB1.xlsx")

    modules_df = pd.read_excel(xls, sheet_name="modules")
    models_df = pd.read_excel(xls, sheet_name="models")
    variants_df = pd.read_excel(xls, sheet_name="variants")

    # Clean text
    for df in [modules_df, models_df, variants_df]:
        df.columns = df.columns.str.strip()
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    variants_df["MTE"] = pd.to_numeric(variants_df["MTE"], errors="coerce")

    return modules_df, models_df, variants_df


# ---------------------------------------------------
# LOAD KEN DATA
# ---------------------------------------------------
@st.cache_data
def load_ken():
    df = pd.read_excel("ken_DATA.xlsx")

    df.columns = df.columns.str.strip()

    # Clean text
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    return df


modules_df, models_df, variants_df = load_db()
ken_df = load_ken()

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.title("MTE Calculator")

equipment_code = st.text_input("Enter Equipment Code")

# Module dropdown from ken file (excluding Equipment Code)
module_options = [
    col for col in ken_df.columns
    if col.lower() != "equipment code"
]

selected_module = st.selectbox("Select Module", module_options)

# ---------------------------------------------------
# SEARCH
# ---------------------------------------------------
if st.button("Search"):

    if not equipment_code:
        st.error("Please enter equipment code")
    else:

        # CASE-INSENSITIVE COLUMN MATCH
        matching_column = None
        for col in ken_df.columns:
            if col.lower() == selected_module.lower():
                matching_column = col
                break

        if matching_column is None:
            st.error(f"Column '{selected_module}' not found in ken_DATA.xlsx")
            st.write("Available columns:", list(ken_df.columns))
            st.stop()

        row = ken_df[
            ken_df["Equipment Code"].str.lower() == equipment_code.lower()
        ]

        if row.empty:
            st.error("Equipment not found")
            st.stop()

        model_name = row.iloc[0][matching_column]

        if not model_name or model_name.lower() == "nan":
            st.error("No model found for this module")
            st.stop()

        st.session_state["module"] = selected_module
        st.session_state["model"] = model_name

        st.success(f"Model Found: {model_name}")

# ---------------------------------------------------
# VARIANT SECTION
# ---------------------------------------------------
if "model" in st.session_state:

    module_name = st.session_state["module"]
    model_name = st.session_state["model"]

    # Match model in DB1
    model_row = models_df[
        models_df["model_name"].str.lower() == model_name.lower()
    ]

    if model_row.empty:
        st.error("Model not found in DB1.xlsx")
        st.stop()

    model_id = model_row.iloc[0]["model_id"]

    model_variants = variants_df[
        variants_df["model_id"] == model_id
    ]

    if model_variants.empty:
        st.warning("No variants found")
        st.stop()

    st.subheader("Select Variants")

    selected_variants = st.multiselect(
        "Variants",
        model_variants["variant_name"].tolist()
    )

    col1, col2 = st.columns(2)

    with col1:
        calculate = st.button("Calculate MTE")

    with col2:
        clear = st.button("Clear")

    if calculate and selected_variants:

        selected_rows = model_variants[
            model_variants["variant_name"].isin(selected_variants)
        ]

        total_mte = round(selected_rows["MTE"].sum(), 3)

        st.markdown("---")
        st.subheader("Result")

        st.write(f"**Module:** {module_name}")
        st.write(f"**Model:** {model_name}")
        st.write("**Selected Variants:**")

        for _, row in selected_rows.iterrows():
            st.write(f"- {row['variant_name']} ({row['MTE']})")

        st.success(f"Overall MTE: {total_mte}")

    if clear:
        st.session_state.clear()
        st.rerun()
