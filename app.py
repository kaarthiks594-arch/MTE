import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="centered")

# =====================================================
# LOAD DATABASE (DB1.xlsx)
# =====================================================
@st.cache_data
def load_db():
    modules_df = pd.read_excel("DB1.xlsx", sheet_name="modules")
    models_df = pd.read_excel("DB1.xlsx", sheet_name="models")
    variants_df = pd.read_excel("DB1.xlsx", sheet_name="variants")

    # Clean text columns
    for df in [modules_df, models_df, variants_df]:
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Convert MTE to numeric
    variants_df["MTE"] = pd.to_numeric(variants_df["MTE"], errors="coerce")

    return modules_df, models_df, variants_df


# =====================================================
# LOAD EQUIPMENT DATABASE (ken_DATA.xlsx)
# =====================================================
@st.cache_data
def load_ken():
    df = pd.read_excel("ken_DATA.xlsx")
    df.columns = df.columns.str.strip()  # remove hidden spaces
    df["Equipment Code"] = df["Equipment Code"].astype(str).str.strip()
    return df


modules_df, models_df, variants_df = load_db()
ken_df = load_ken()

# =====================================================
# UI
# =====================================================
st.title(" MTE Calculator")

equipment_code = st.text_input("Enter Equipment Code")

module_name = st.selectbox(
    "Select Module",
    modules_df["module_name"].unique()
)

# =====================================================
# SEARCH BUTTON
# =====================================================
if st.button("Search"):

    if not equipment_code:
        st.error("Please enter Equipment Code")
        st.stop()

    equipment_code = equipment_code.strip()

    # Check equipment exists
    equipment_row = ken_df[ken_df["Equipment Code"] == equipment_code]

    if equipment_row.empty:
        st.error("Equipment Code not found")
        st.stop()

    # IMPORTANT:
    # Module column name in ken_DATA must match module_name exactly
    if module_name not in ken_df.columns:
        st.error(f"Column '{module_name}' not found in ken_DATA.xlsx")
        st.write("Available columns:", list(ken_df.columns))
        st.stop()

    model_name = str(equipment_row.iloc[0][module_name]).strip()

    if model_name.lower() == "nan" or model_name == "":
        st.error("No model found for this module")
        st.stop()

    st.session_state["module_name"] = module_name
    st.session_state["model_name"] = model_name

    st.success(f"Model Found: {model_name}")

# =====================================================
# SHOW VARIANTS
# =====================================================
if "model_name" in st.session_state:

    module_name = st.session_state["module_name"]
    model_name = st.session_state["model_name"]

    # Get module_id
    module_row = modules_df[
        modules_df["module_name"].str.lower() == module_name.lower()
    ]

    if module_row.empty:
        st.error("Module not found in DB1.xlsx")
        st.stop()

    module_id = module_row.iloc[0]["module_id"]

    # Get model_id
    model_row = models_df[
        (models_df["model_name"].str.lower() == model_name.lower()) &
        (models_df["module_id"] == module_id)
    ]

    if model_row.empty:
        st.error("Model not found in DB1.xlsx")
        st.stop()

    model_id = model_row.iloc[0]["model_id"]

    # Get variants
    model_variants = variants_df[
        variants_df["model_id"] == model_id
    ]

    if model_variants.empty:
        st.warning("No variants available")
        st.stop()

    st.subheader("Select Variants")

    selected_variants = st.multiselect(
        "Choose variants",
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

        st.write(f"**Module Name:** {module_name}")
        st.write(f"**Model Name:** {model_name}")

        st.write("**Selected Variants:**")
        for _, row in selected_rows.iterrows():
            st.write(f"- {row['variant_name']} ({row['MTE']})")

        st.success(f"Overall MTE: {total_mte}")

    if clear:
        st.session_state.clear()
        st.rerun()
