import joblib
import shap
import pandas as pd

MODEL_PATH = "model/xgboost_model.pkl"

_model = None
_explainer = None

def _load():
    global _model, _explainer
    if _model is None:
        _model = joblib.load(MODEL_PATH)
        _explainer = shap.TreeExplainer(_model)

def explain_prediction(input_data: dict, top_k: int = 5):
    _load()

    df = pd.DataFrame([input_data])
    shap_values = _explainer.shap_values(df)[0]

    features = list(zip(df.columns, shap_values))
    features.sort(key=lambda x: abs(x[1]), reverse=True)

    return features[:top_k]
