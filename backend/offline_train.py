from app.services.ml_service import ml_service
import os

def train_now():
    data_file = "enhanced_training_data.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ Error: {data_file} not found!")
        return

    print(f"🚀 Starting training using {data_file}...")
    
    result = ml_service.train_models(data_file)
    
    if result.get("status") == "success":
        print("\n✅ TRAINING SUCCESSFUL!")
        print(f"   Random Forest MAE: {result.get('rf_mae')}")
        print(f"   XGBoost MAE:       {result.get('xgb_mae')}")
        print("\nModels saved to /ml_models directory.")
        print("The backend will automatically pick up these new models on next request/restart.")
    else:
        print(f"\n❌ Training Failed: {result.get('message')}")

if __name__ == "__main__":
    train_now()
