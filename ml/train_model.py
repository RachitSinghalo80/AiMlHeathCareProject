import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

DATA_PATH = "data/diabetes_dataset.csv"
MODEL_PATH = "model/xgboost_model.pkl"

def train():
    df = pd.read_csv(DATA_PATH)

    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]

    # Ensure binary
    y = y.apply(lambda x: 1 if x >= 1 else 0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

    model = XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="auc",
        scale_pos_weight=scale_pos_weight,
        random_state=42
    )

    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)

    print("Model trained and saved to", MODEL_PATH)

if __name__ == "__main__":
    train()
