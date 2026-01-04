import sys
sys.path.append('.')

from app.services.ml_service import ml_service

# Direct training without API
print("Starting ML Model Training...")
print("=" * 50)

data_path = "data/training_data_template.csv"

result = ml_service.train_models(data_path)

print("\n" + "=" * 50)
if result["status"] == "success":
    print("✅ TRAINING SUCCESSFUL!")
    print(f"\nRandomForest MAE: {result['rf_mae']}")
    print(f"XGBoost MAE: {result['xgb_mae']}")
    print(f"\n{result['message']}")
    print("\nModels saved in: ml_models/")
    print("\n🎯 Your forecasts will now be much more accurate!")
else:
    print(f"❌ TRAINING FAILED: {result['message']}")

print("=" * 50)
