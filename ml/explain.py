import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

MODEL_PATH = "model/xgboost_model.pkl"

_model = None
_explainer = None
_feature_order = None

# ---------- Load model and explainer ----------
def _load():
    global _model, _explainer, _feature_order
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _explainer = shap.TreeExplainer(_model)
        _feature_order = _model.feature_names_in_

# ---------- Helper function  ----------   
def _sanitize_input(input_data: dict) -> dict:
    """
    Ensure all model features are numeric before SHAP.
    Handles OCR strings, units, booleans safely.
    """
    clean = {}

    for key in _feature_order:
        val = input_data.get(key, 0)

        if val is None:
            clean[key] = 0.0
            continue

        if isinstance(val, bool):
            clean[key] = int(val)
            continue

        if isinstance(val, str):
            val = (
                val.lower()
                   .replace("%", "")
                   .replace("mg/dl", "")
                   .replace("mg/dL", "")
                   .replace(",", ".")
                   .strip()
            )

        try:
            clean[key] = float(val)
        except ValueError:
            clean[key] = 0.0

    return clean
     

# ---------- SHAP values for one prediction ----------
def explain_prediction(input_data: dict, top_k: int = 8):
    _load()
    clean_input = _sanitize_input(input_data)
    df = pd.DataFrame([clean_input])
    df = df.reindex(columns=_feature_order, fill_value=0)


    shap_values = _explainer.shap_values(df)[0]
    features = list(zip(df.columns, shap_values))
    features.sort(key=lambda x: abs(x[1]), reverse=True)

    return features[:top_k]

# ---------- SHAP bar plot ----------
def shap_bar_plot(shap_features):
    names = [f[0].replace("_", " ").title() for f in shap_features]
    values = [f[1] for f in shap_features]
    colors = ["#d62728" if v > 0 else "#2ca02c" for v in values]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(names, values, color=colors)
    ax.axvline(0, color="gray", linewidth=0.8)
    ax.set_xlabel("Impact on Risk")
    ax.set_title("Key Factors Influencing Risk")
    plt.tight_layout()
    return fig

# ---------- SHAP grouping ----------
def group_shap_features(shap_features):
    groups = {
        "Metabolic Factors": [],
        "Lifestyle Factors": [],
        "Medical History": []
    }

    for name, value in shap_features:
        if name in ["bmi", "HbA1c_level", "blood_glucose_level"]:
            groups["Metabolic Factors"].append((name, value))
        elif name.startswith("smoking"):
        # Only show if smoking INCREASES risk
            if value > 0:
                groups["Lifestyle Factors"].append((name, value))

        elif name.startswith("gender"):
    # ❌ Do not include gender in risk drivers
            continue

        else:
            groups["Medical History"].append((name, value))

    return groups

# ---------- Top modifiable factors ----------
def top_modifiable_factors(shap_features, k=3):
    modifiable = [
        (n, v) for n, v in shap_features
        if n in ["bmi", "blood_glucose_level"]
    ]
    modifiable.sort(key=lambda x: abs(x[1]), reverse=True)
    return modifiable[:k]

# ---------- Scenario simulation ----------
def simulate_scenario(input_data: dict, feature: str, new_value: float):
    modified = input_data.copy()
    modified[feature] = new_value
    return modified
