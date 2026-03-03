import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor
import joblib

# 1. Load datasets
train_df = pd.read_csv("data/training.csv")
control_df = pd.read_csv("data/control.csv")

# 2. Drop unused columns
drop_cols = [
    "game_id",
    "player_id",
    "position",
    "date",
    "opponent"
]

train_df = train_df.drop(columns=drop_cols)
control_df = control_df.drop(columns=drop_cols)

# 3. Split X and y
X_train = train_df.drop(columns=["target_fantasy_points_game"])
y_train = train_df["target_fantasy_points_game"]

X_control = control_df.drop(columns=["target_fantasy_points_game"])
y_control = control_df["target_fantasy_points_game"]

# 4. Train Random Forest
#"""
model = RandomForestRegressor(
    n_estimators=75,
    max_depth=8,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1,
    verbose=1
)
#"""

"""
model = HistGradientBoostingRegressor(
    max_depth=8,
    learning_rate=0.05,
    max_iter=300,
    random_state=42
)
"""

print("Training rows:", len(X_train))
print("Features:", len(X_train.columns))

print("Training model...")
model.fit(X_train, y_train)

# 5. Evaluate on control set
preds = model.predict(X_control)

mae = mean_absolute_error(y_control, preds)
rmse = np.sqrt(mean_squared_error(y_control, preds))
r2 = r2_score(y_control, preds)

print("\n===== CONTROL SET PERFORMANCE =====")
print(f"MAE  : {mae:.3f}")
print(f"RMSE : {rmse:.3f}")
print(f"R2   : {r2:.3f}")

# 6. Feature importance
importance = pd.DataFrame({
    "feature": X_train.columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\n===== FEATURE IMPORTANCE =====")
print(importance.head(15))

# 7. Save model
joblib.dump(model, "fantasy_rf_model.pkl")
print("\nModel saved as fantasy_rf_model.pkl")