import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump
df = pd.read_csv("data/visits.csv", parse_dates=["ts"])
y = df["outcome"]
numeric = ["hr","rr","sbp","temp","spo2","triage_cat","ecg_flag","lab_abn","prev_ed_30d"]
categorical = ["arrival_mode"]
pre = ColumnTransformer([("num","passthrough",numeric),("cat", OneHotEncoder(handle_unknown="ignore"), categorical)])
clf = Pipeline([("prep", pre),("lr", LogisticRegression(max_iter=2000, multi_class="ovr", class_weight="balanced"))])
X = df[numeric + categorical]
counts = y.value_counts(); use_stratify = counts.min() >= 2
if use_stratify:
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.4, random_state=42)
else:
    print(f"[WARN] Small class counts detected {dict(counts)}; training without stratify.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
clf.fit(X_train, y_train)
print("Evaluation on holdout:"); print(classification_report(y_test, clf.predict(X_test), zero_division=0))
dump(clf, "data/model.pkl"); print("Saved -> data/model.pkl")
