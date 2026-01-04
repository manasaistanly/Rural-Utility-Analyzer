import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_realistic_data():
    print("Generating realistic utility data for Hyderabad context...")
    
    # Range: 3 years of data
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 1, 1)
    days = (end_date - start_date).days
    dates = [start_date + timedelta(days=x) for x in range(days)]
    
    data = []
    
    for date in dates:
        month = date.month
        
        # --- WEATHER SIMULATION (Hyderabad) ---
        # Summer (Mar-May): Hot, Dry
        if 3 <= month <= 5:
            base_temp = np.random.normal(38, 2)
            base_humidity = np.random.normal(40, 5)
        # Monsoon (Jun-Sep): Warm, Humid
        elif 6 <= month <= 9:
            base_temp = np.random.normal(30, 2)
            base_humidity = np.random.normal(80, 5)
        # Winter (Oct-Feb): Pleasant, Dry
        else:
            base_temp = np.random.normal(25, 2)
            base_humidity = np.random.normal(50, 5)
            
        temp = round(base_temp, 1)
        humidity = round(base_humidity, 1)
        
        # --- ELECTRICITY CONSUMPTION LOGIC (kWh) ---
        # Base load (Fridge, Lights, TV): 5-8 units/day
        elec_base = np.random.uniform(5, 8)
        
        # AC Load (Summer/Hot days): heavy impact
        elec_cooling = 0
        if temp > 35:
            elec_cooling = np.random.uniform(10, 15) # AC running 6-8 hours
        elif temp > 30:
            elec_cooling = np.random.uniform(2, 5)   # Fans running all day
            
        electricity_units = round(elec_base + elec_cooling, 1)
        
        # --- WATER CONSUMPTION LOGIC (KL) ---
        # Base load (Showing, Cooking, Cleaning): 0.5 - 0.8 KL/day
        water_base = np.random.uniform(0.5, 0.8)
        
        # Summer extra (more showers, gardening evaporation)
        water_extra = 0
        if temp > 35:
            water_extra = np.random.uniform(0.2, 0.4)
            
        water_units = round(water_base + water_extra, 2)
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "units_consumed": electricity_units, # For now training main model on Electricity
            "temp": temp,
            "humidity": humidity,
            "type": "electricity"
        })
        
        # Add water rows too? 
        # For this ML service, we currently train one unified model. 
        # Since electricity varies more, we train on electricity patterns mainly.

    df = pd.DataFrame(data)
    
    # Save to CSV
    filename = "enhanced_training_data.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Generated {len(df)} records in {filename}")
    print("   - Includes seasonal patterns (Summer peaks)")
    print("   - Realistic temperature/humidity correlation")

if __name__ == "__main__":
    generate_realistic_data()
