import joblib
import joblib
import pandas as pd

MODEL_PATH = "model/xgboost_model.pkl"

_model = None
_feature_order = None

def load_model():
    global _model, _feature_order
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        # store training-time feature order
        _feature_order = _model.feature_names_in_
    return _model

def predict_risk(input_data: dict):
    model = load_model()

    df = pd.DataFrame([input_data])

    # 🔑 ALIGN COLUMN ORDER WITH TRAINING
    df = df.reindex(columns=_feature_order, fill_value=0)

    probability = model.predict_proba(df)[0][1]
    return probability
