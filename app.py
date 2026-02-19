import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTE Calculator", layout="centered")

# ---------------------------------------------------
# LOAD EXCEL FILES
# ---------------------------------------------------
@st.cache_data
def load_db():
    xls = pd.ExcelFile("DB.xlsx")
    modules_df = pd.read_excel(xls, sheet_name="modules")
    models_df = pd.read_excel(xls, sheet_name="models")
    variants_df = pd.read_excel(xls, sheet_name="variants")

    # Clean all text columns
    for col in modules_df.columns:
        modules_df[col] = modules_df[col].astype(str).str.strip()

    for col in models_df.columns:
        models_df[col] = models_df[col].astype(str).str.strip()

    for col in variants_df.columns:
        variants_df[col] = variants_df[col].astype(str).str.strip()

    variants_df["MTE"] = pd.to_numeric(variants_df["MTE"], errors="coerce")

    return modules_df, models_df, variants_df


@st.cache_data
def load_ken():
    df = pd.read_excel("ken_DATA.xlsx")

    df.columns = df.columns.str.strip()
    df["Equipment Code"] = df["Equipment Code"].astype(str).str.strip()

    return df


modules_df, models_df, variants_df = load_db()
ken_df = load_ken()

# ---------------------------------------------------
# UI
# ---------------------------------------------------
st.title(" MTE Calculator")

equipment_code = st.text_input("Equipment Code")
module_name = st.selectbox(
    "Module",
    [col for col in ken_df.columns if col.lower() != "equipment code"]
)

# ---------------------------------------------------
# SEARCH BUTTON
# ---------------------------------------------------
if st.button("Search"):

    if not equipment_code:
        st.error("Please enter equipment code")
    else:
        equipment_code = equipment_code.strip()

        row = ken_df.loc[ken_df["Equipment Code"] == equipment_code]

        if row.empty:
            st.error("Equipment not found")
        else:
            model_name = str(row.iloc[0][module_name]).strip()

            if not model_name or model_name.lower() == "nan":
                st.error("No model found for this module")
            else:
                st.session_state["model_name"] = model_name
                st.session_state["module_name"] = module_name
                st.success(f"Model Found: {model_name}")

# ---------------------------------------------------
# SHOW VARIANTS (AFTER SEARCH)
# ---------------------------------------------------
if "model_name" in st.session_state:

    model_name = st.session_state["model_name"]
    module_name = st.session_state["module_name"]

    # Match model in DB.xlsx (case insensitive safe match)
    model_row = models_df[
        models_df["model_name"].str.lower() == model_name.lower()
    ]

    if model_row.empty:
        st.error("Model not found in DB.xlsx")
    else:
        model_id = model_row.iloc[0]["model_id"]

        model_variants = variants_df[
            variants_df["model_id"] == model_id
        ]

        if model_variants.empty:
            st.warning("No variants available")
        else:
            st.subheader("Select Variants")

            selected_variants = st.multiselect(
                "Variants",
                model_variants["variant_name"].tolist()
            )

            # ---------------------------------------------------
            # CALCULATE BUTTON
            # ---------------------------------------------------
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

                st.success(f"Total MTE: {total_mte}")

            if clear:
                st.session_state.clear()
                st.rerun()
