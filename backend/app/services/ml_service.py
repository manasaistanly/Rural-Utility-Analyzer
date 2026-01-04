import numpy as np
import pandas as pd
from typing import List, Dict
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.arima.model import ARIMA
import xgboost as xgb

# Directory to save models
MODEL_DIR = "ml_models"
os.makedirs(MODEL_DIR, exist_ok=True)

class MLService:
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.load_models()

    def load_models(self):
        try:
            self.rf_model = joblib.load(f"{MODEL_DIR}/rf_model.pkl")
            self.xgb_model = joblib.load(f"{MODEL_DIR}/xgb_model.pkl")
            print("Models loaded successfully.")
        except:
            print("No trained models found. Using mock logic until training.")

    def train_models(self, data_path: str):
        """
        Train Random Forest and XGBoost on CSV data.
        Expected CSV cols: 'date', 'units_consumed', 'temp', 'humidity'
        """
        try:
            df = pd.read_csv(data_path)
            # Basic Feature Engineering
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.month
            df['day_of_year'] = df['date'].dt.dayofyear
            
            X = df[['month', 'day_of_year', 'temp', 'humidity']]
            y = df['units_consumed']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 1. Random Forest
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X_train, y_train)
            rf_mae = mean_absolute_error(y_test, rf.predict(X_test))
            joblib.dump(rf, f"{MODEL_DIR}/rf_model.pkl")
            self.rf_model = rf
            
            # 2. XGBoost
            xg = xgb.XGBRegressor(objective='reg:squarederror')
            xg.fit(X_train, y_train)
            xg_mae = mean_absolute_error(y_test, xg.predict(X_test))
            joblib.dump(xg, f"{MODEL_DIR}/xgb_model.pkl")
            self.xgb_model = xg

            return {
                "status": "success",
                "rf_mae": round(rf_mae, 2),
                "xgb_mae": round(xg_mae, 2),
                "message": "Models trained and saved successfully."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def predict_consumption(self, weather_data: Dict, historical_data: List[float]) -> float:
        """
        Generate forecast value (float). 
        Arguments swapped to match analysis.py call: (weather_data, historical_data)
        """
        # Feature vector for current prediction
        import datetime
        now = datetime.datetime.now()
        
        # Extract features (handle date if needed, here simplified)
        X_pred = pd.DataFrame([{
            'month': now.month,
            'day_of_year': now.timetuple().tm_yday,
            'temp': weather_data.get('temperature', 30), # analysis.py sends 'temperature'
            'humidity': weather_data.get('humidity', 60)
        }])

        prediction = 0
        
        # 1. Try ML Models
        if self.rf_model:
            try:
                prediction = float(self.rf_model.predict(X_pred)[0])
            except:
                pass
        
        # 2. Fallback to XGBoost if RF failed
        if prediction == 0 and self.xgb_model:
            try:
                prediction = float(self.xgb_model.predict(X_pred)[0])
            except:
                pass
                
        # 3. Fallback to Simple Average if ML failed
        if prediction == 0 and historical_data:
            # Simple average of last 3 months
            if len(historical_data) >= 3:
                prediction = sum(historical_data[-3:]) / 3
            else:
                prediction = sum(historical_data) / len(historical_data)

        # Apply slight increase/decrease based on weather logic if using fallback
        if not self.rf_model and weather_data.get('temperature', 30) > 35:
            prediction *= 1.10  # +10% for high heat
            
        return round(prediction, 2)

ml_service = MLService()
