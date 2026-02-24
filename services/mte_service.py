import pandas as pd

KEN_PATH = "data/ken_DATA.xlsx"
DB_PATH = "data/DB.xlsx"

def load_data():
    ken = pd.read_excel(KEN_PATH)
    db = pd.read_excel(DB_PATH)
    return ken, db

def find_model(ken, equipment_no, module_name):
    row = ken[
        (ken["Equipment No"] == equipment_no) &
        (ken["Module Name"] == module_name)
    ]

    if row.empty:
        return None

    return row.iloc[0]["Model Name"]

def get_main_models(db, model_name):
    db_filtered = db[db["Model Name"] == model_name]

    sub_models = db_filtered["Sub Model"].dropna().unique()

    # Extract main model prefix (example: KDL from KDL16L)
    main_models = list(set([sm[:3] for sm in sub_models]))

    return sorted(main_models)

def get_sub_models(db, model_name, main_model):
    db_filtered = db[db["Model Name"] == model_name]
    sub_models = db_filtered["Sub Model"].dropna().unique()

    return sorted([sm for sm in sub_models if sm.startswith(main_model)])

def get_variants(db, model_name, sub_model):
    db_filtered = db[
        (db["Model Name"] == model_name) &
        (db["Sub Model"] == sub_model)
    ]

    return db_filtered["Variant Name"].unique()

def calculate_mte(db, model_name, sub_model, selected_variants):
    filtered = db[
        (db["Model Name"] == model_name) &
        (db["Sub Model"] == sub_model) &
        (db["Variant Name"].isin(selected_variants))
    ]

    return filtered["MTE"].sum()
