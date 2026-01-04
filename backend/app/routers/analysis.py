from fastapi import APIRouter, Depends
from app.models.models import User, Bill
from app.routers.deps import get_current_user

router = APIRouter()

@router.get("/forecast")
async def get_forecast(
    lang: str = None,
    bill_type: str = 'electricity',
    current_user: User = Depends(get_current_user)
):
    # Determine language
    target_lang = lang if lang else (current_user.language_pref or 'en')

    # 1. Fetch Weather Data
    from app.services.weather_service import WeatherService
    from app.services.recommendation_service import get_smart_recommendation
    
    current_weather = await WeatherService.get_current_weather()
    if not current_weather:
        current_weather = {"main": {"temp": 30, "humidity": 60}, "weather": [{"main": "Clear"}]}

    # 2. Fetch Bills (FILTERED BY BILL TYPE)
    bills = await Bill.find(
        Bill.user_id == str(current_user.id),
        Bill.is_verified == True,
        Bill.bill_type == bill_type
    ).sort("+bill_date").to_list()
    
    consumption_history = [b.units_consumed for b in bills]
    
    # Calculate Stats
    total_units = sum(consumption_history) if consumption_history else 0
    total_cost = sum([b.total_amount for b in bills]) if bills else 0
    
    # Chart Data
    chart_data = []
    for bill in bills:
        chart_data.append({
            "month": bill.bill_date.strftime("%b") if bill.bill_date else "Unknown",
            "consumption": bill.units_consumed,
            "cost": bill.total_amount
        })
        
    # 3. Prepare Weather Info
    weather_info = {
        "temperature": current_weather["main"]["temp"],
        "humidity": current_weather["main"]["humidity"],
        "description": current_weather["weather"][0]["main"] if current_weather.get("weather") else "Clear",
        "rainfall": 0
    }
    
    # Helper: Electricity Cost Calculation
    def calculate_electricity_cost(units):
        total = 0
        if units <= 50:
            total = units * 2.65
        elif units <= 100:
            total = (50 * 2.65) + ((units - 50) * 3.35)
        elif units <= 200:
            total = (50 * 2.65) + (50 * 3.35) + ((units - 100) * 5.40)
        else:
            total = (50 * 2.65) + (50 * 3.35) + (100 * 5.40) + ((units - 200) * 7.10)
        return round(total, 2)
    
    # Helper: Water Cost Calculation
    def calculate_water_cost(kiloliters):
        water_charge = 0
        if kiloliters <= 15:
            water_charge = kiloliters * 10
        elif kiloliters <= 30:
            water_charge = (15 * 10) + ((kiloliters - 15) * 12)
        elif kiloliters <= 50:
            water_charge = (15 * 10) + (15 * 12) + ((kiloliters - 30) * 22)
        else:
            water_charge = (15 * 10) + (15 * 12) + (20 * 22) + ((kiloliters - 50) * 22)
        
        sewerage_cess = water_charge * 0.35
        return round(water_charge + sewerage_cess, 2)

    # Select cost calculator
    calculate_bill_cost = calculate_water_cost if bill_type == 'water' else calculate_electricity_cost

    # 4. ML Prediction
    if not consumption_history:
        forecast_value = 0
        forecast_cost = 0
    else:
        from app.services.ml_service import ml_service
        
        prediction_input = {
            "month": __import__("datetime").datetime.now().month,
            "day": __import__("datetime").datetime.now().day,
            "temperature": weather_info["temperature"],
            "humidity": weather_info["humidity"]
        }
        
        try:
            forecast_value = ml_service.predict_consumption(prediction_input, consumption_history)
        except:
            forecast_value = sum(consumption_history[-3:]) / 3 if len(consumption_history) >= 3 else consumption_history[-1] if consumption_history else 0
        
        forecast_cost = calculate_bill_cost(forecast_value)

    # 5. Comparison
    if len(consumption_history) >= 2:
        last_month = consumption_history[-1]
        prev_month = consumption_history[-2]
        diff = last_month - prev_month
        percentage = round((diff / prev_month) * 100, 1) if prev_month > 0 else 0
        
        if percentage > 5:
            trend = "up"
        elif percentage < -5:
            trend = "down"
        else:
            trend = "stable"
    else:
        trend, percentage = "stable", 0

    comparison = {"trend": trend, "percentage": abs(percentage)}

    # 6. Get Recommendation
    if not consumption_history:
        recommendation = target_lang == 'en' and "Upload more bills for accurate insights!" or "ఖచ్చితమైన అంచనా కోసం మరిన్ని బిల్లులను అప్‌లోడ్ చేయండి!"
    else:
        recommendation = await get_smart_recommendation(
            forecast_value,
            current_weather,
            comparison,
            target_lang,
            consumption_history,
            bill_type
        )
    
    return {
        "forecast": round(forecast_value),
        "forecast_cost": forecast_cost,
        "stats": {"total_units": total_units, "total_cost": total_cost},
        "chart_data": chart_data,
        "recommendation": recommendation,
        "current_weather": {
            "temp": round(weather_info["temperature"]),
            "humidity": weather_info["humidity"],
            "desc": weather_info["description"]
        },
        "comparison": comparison
    }


@router.get("/consumption-pattern")
async def get_consumption_pattern(current_user: User = Depends(get_current_user)):
    bills = await Bill.find(
        Bill.user_id == str(current_user.id),
        Bill.is_verified == True
    ).sort("+bill_date").to_list()
    
    data = [{"month": b.bill_date.strftime("%b %Y") if b.bill_date else "Unknown", "units": b.units_consumed} for b in bills]
    return {"pattern": data}
