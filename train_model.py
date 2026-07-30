import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score
import joblib

np.random.seed(42)
n_samples = 100000

amount = np.random.exponential(scale=60, size=n_samples)
time_delta = np.random.exponential(scale=100, size=n_samples)
geo_distance = np.random.exponential(scale=15, size=n_samples)
is_foreign = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])

is_fraud = (
    ((amount > 350) & (geo_distance > 50)) | 
    ((time_delta < 3) & (amount > 150)) | 
    ((is_foreign == 1) & (geo_distance > 120))
).astype(int)

df = pd.DataFrame({
    'amount': amount,
    'time_delta': time_delta,
    'geo_distance': geo_distance,
    'is_foreign': is_foreign,
    'is_fraud': is_fraud
})

X = df[['amount', 'time_delta', 'geo_distance', 'is_foreign']]
y = df['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.08)
model.fit(X_train, y_train)

preds = model.predict(X_test)
precision = precision_score(y_test, preds)
print(f"Model Training Complete! Precision Score: {precision * 100:.2f}%")

joblib.dump(model, 'fraud_model.joblib')
print("Model saved as 'fraud_model.joblib'")