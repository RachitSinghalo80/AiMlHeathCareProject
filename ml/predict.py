import joblib
import pandas as pd

MODEL_PATH = "model/xgboost_model.pkl"

_model = None
_feature_order = None


def load_model():
    global _model, _feature_order
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _feature_order = _model.feature_names_in_
    return _model


def _sanitize_input(input_data: dict) -> dict:
    """
    Ensures all inputs are numeric.
    Handles OCR noise, UI strings, units, booleans.
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


def predict_risk(input_data: dict) -> float:
    model = load_model()

    clean_input = _sanitize_input(input_data)
    df = pd.DataFrame([clean_input])

    # 🔑 ALIGN COLUMN ORDER WITH TRAINING
    df = df.reindex(columns=_feature_order, fill_value=0)

    probability = model.predict_proba(df)[0][1]
    return float(probability)

