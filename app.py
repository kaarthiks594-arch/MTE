import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="centered")

# ---------------------------------------------------
# LOAD DATABASE FILE
# ---------------------------------------------------
@st.cache_data
def load_db():
    try:
        xls = pd.ExcelFile("DB.xlsx")

        models_df = pd.read_excel(xls, sheet_name="models")
        variants_df = pd.read_excel(xls, sheet_name="variants")

        # Clean text
        for col in models_df.columns:
            models_df[col] = models_df[col].astype(str).str.strip()

        for col in variants_df.columns:
            variants_df[col] = variants_df[col].astype(str).str.strip()

        variants_df["MTE"] = pd.to_numeric(variants_df["MTE"], errors="coerce")

        return models_df, variants_df

    except Exception as e:
        st.error("Error loading DB.xlsx")
        st.stop()


# ---------------------------------------------------
# LOAD EQUIPMENT FILE
# ---------------------------------------------------
@st.cache_data
def load_ken():
    try:
        df = pd.read_excel("ken_DATA.xlsx")
        df.columns = df.columns.str.strip()
        df["Equipment Code"] = df["Equipment Code"].astype(str).str.strip()
        return df

    except Exception as e:
        st.error("Error loading ken_DATA.xlsx")
        st.stop()


models_df, variants_df = load_db()
ken_df = load_ken()

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.title("🔢 MTE Calculator")

equipment_code = st.text_input("Equipment Code")

module_name = st.selectbox(
    "Module",
    [col for col in ken_df.columns if col.lower() != "equipment code"]
)

# ---------------------------------------------------
# SEARCH
# ---------------------------------------------------
if st.button("Search"):

    if not equipment_code:
        st.error("Enter Equipment Code")
        st.stop()

    equipment_code = equipment_code.strip()

    row = ken_df[ken_df["Equipment Code"] == equipment_code]

    if row.empty:
        st.error("Equipment not found")
        st.stop()

    model_name = str(row.iloc[0][module_name]).strip()

    if model_name.lower() == "nan" or model_name == "":
        st.error("No model found for this module")
        st.stop()

    st.session_state["module"] = module_name
    st.session_state["model"] = model_name

# ---------------------------------------------------
# SHOW MODEL / SUBMODEL / VARIANTS
# ---------------------------------------------------
if "model" in st.session_state:

    module_name = st.session_state["module"]
    model_name = st.session_state["model"]

    st.success(f"Model Found: {model_name}")

    # Filter DB by module + model
    model_rows = models_df[
        (models_df["module_name"].str.lower() == module_name.lower()) &
        (models_df["model_name"].str.lower() == model_name.lower())
    ]

    if model_rows.empty:
        st.error("Model not found in DB.xlsx")
        st.stop()

    # Select Sub Model
    sub_models = model_rows["sub_model_name"].unique()

    selected_sub_model = st.selectbox(
        "Select Sub Model",
        sub_models
    )

    # Get model_id
    model_id = model_rows[
        model_rows["sub_model_name"] == selected_sub_model
    ].iloc[0]["model_id"]

    # Get variants
    model_variants = variants_df[
        variants_df["model_id"] == str(model_id)
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

    # ---------------------------------------------------
    # CALCULATE
    # ---------------------------------------------------
    if calculate and selected_variants:

        selected_rows = model_variants[
            model_variants["variant_name"].isin(selected_variants)
        ]

        total_mte = round(selected_rows["MTE"].sum(), 3)

        st.markdown("---")
        st.subheader("Result")

        st.write(f"**Module:** {module_name}")
        st.write(f"**Model:** {model_name}")
        st.write(f"**Sub Model:** {selected_sub_model}")
        st.write("**Selected Variants:**")

        for _, row in selected_rows.iterrows():
            st.write(f"- {row['variant_name']} ({row['MTE']})")

        st.success(f"Total MTE: {total_mte}")

    if clear:
        st.session_state.clear()
        st.rerun()
