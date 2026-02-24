import streamlit as st
from services.mte_service import *
from utils.auth import check_login

st.set_page_config(page_title="MTE Calculator", layout="wide")

# 🔐 Login Protection
check_login()

st.title("MTE Calculator")

# Load Excel Data
ken, db = load_data()

# -----------------------------
# Step 1: Equipment + Module
# -----------------------------

col1, col2 = st.columns(2)

with col1:
    equipment_no = st.text_input("Enter Equipment No")

with col2:
    module_name = st.text_input("Enter Module Name")

if st.button("Search"):

    model_name = find_model(ken, equipment_no, module_name)

    if not model_name:
        st.error("No matching Equipment or Module found")
        st.stop()

    st.success(f"Model Found: {model_name}")
    st.session_state["model_name"] = model_name

# -----------------------------
# Step 2: Main Model Selection
# -----------------------------

if "model_name" in st.session_state:

    model_name = st.session_state["model_name"]

    main_models = get_main_models(db, model_name)

    selected_main = st.selectbox("Select Main Model", main_models)

    # -----------------------------
    # Step 3: Sub Model Selection
    # -----------------------------

    sub_models = get_sub_models(db, model_name, selected_main)

    selected_sub = st.selectbox("Select Sub Model", sub_models)

    # -----------------------------
    # Step 4: Variant Selection
    # -----------------------------

    variants = get_variants(db, model_name, selected_sub)

    selected_variants = st.multiselect("Select Variants", variants)

    # -----------------------------
    # Step 5: Calculate
    # -----------------------------

    if st.button("Calculate MTE"):

        if not selected_variants:
            st.warning("Please select at least one variant")
        else:
            overall_mte = calculate_mte(
                db,
                model_name,
                selected_sub,
                selected_variants
            )

            st.success("MTE Calculation Result")

            st.write("### Summary")
            st.write(f"Model: {model_name}")
            st.write(f"Main Model: {selected_main}")
            st.write(f"Sub Model: {selected_sub}")
            st.write(f"Selected Variants: {selected_variants}")
            st.write(f"Overall MTE: {overall_mte}")
