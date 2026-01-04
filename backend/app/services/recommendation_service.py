import statistics
from typing import Dict, List

async def get_smart_recommendation(
    forecast_value: float,
    weather_data: Dict,
    comparison: Dict,
    language: str = 'en',
    historical_consumption: List[float] = None,
    bill_type: str = 'electricity'  # New parameter to customize recommendations
) -> str:
    """
    AI-powered recommendation engine that analyzes patterns and provides actionable insights.
    Provides different recommendations for electricity vs water bills.
    """
    
    # Get weather info
    temp = weather_data.get('main', {}).get('temp', 30)
    humidity = weather_data.get('main', {}).get('humidity', 60)
    
    # Initialize recommendation components
    insights = []
    
    # 1. TREND ANALYSIS
    trend = comparison.get('trend', 'stable')
    percentage = comparison.get('percentage', 0)
    
    if trend == 'up' and percentage > 15:
        if language == 'te':
            insights.append(f"⚠️ హెచ్చరిక: మీ వినియోగం గత నెలతో పోలిస్తే {percentage}% పెరిగింది.")
        else:
            insights.append(f"⚠️ Alert: Your consumption has risen by {percentage}% compared to last month.")
    elif trend == 'down' and percentage > 10:
        if language == 'te':
            insights.append(f"✅ అద్భుతం! మీ వినియోగం {percentage}% తగ్గింది. మంచి పని!")
        else:
            insights.append(f"✅ Great job! Your consumption dropped by {percentage}%. Keep it up!")
    
    # 2. CONSUMPTION PATTERN ANALYSIS (if historical data available)
    if historical_consumption and len(historical_consumption) >= 3:
        avg_consumption = statistics.mean(historical_consumption)
        std_dev = statistics.stdev(historical_consumption) if len(historical_consumption) > 1 else 0
        
        # Detect if current forecast is an outlier
        if forecast_value > avg_consumption + (2 * std_dev):
            if language == 'te':
                insights.append(f"📊 మీ అంచనా వినియోగం ({forecast_value:.0f} యూనిట్లు) మీ సగటు ({avg_consumption:.0f}) కంటే చాలా ఎక్కువగా ఉంది.")
            else:
                insights.append(f"📊 Your forecasted consumption ({forecast_value:.0f} units) is significantly higher than your average ({avg_consumption:.0f}).")
        
        # Detect seasonal patterns
        if len(historical_consumption) >= 6:
            recent_trend = historical_consumption[-3:]
            if all(recent_trend[i] < recent_trend[i+1] for i in range(len(recent_trend)-1)):
                if language == 'te':
                    insights.append("📈 గత 3 నెలల్లో నిరంతర పెరుగుదల గమనించబడింది.")
                else:
                    insights.append("📈 Continuous increase detected over the last 3 months.")
    
    # 3. WEATHER-BASED INSIGHTS (Electricity-specific)
    if bill_type == 'electricity':
        if temp > 35:
            if language == 'te':
                insights.append(f"🌡️ అధిక ఉష్ణోగ్రత ({temp}°C): AC వినియోగాన్ని తగ్గించడానికి అభిమానులను ఉపయోగించండి మరియు తలుపులు/కిటికీలు మూసివేయండి.")
            else:
                insights.append(f"🌡️ High temperature ({temp}°C): Use fans and keep doors/windows closed to reduce AC usage.")
        elif temp < 22:
            if language == 'te':
                insights.append(f"❄️ చల్లని వాతావరణం ({temp}°C): సహజ వెంటిలేషన్‌ను పెంచి, శీతలీకరణ వినియోగాన్ని తగ్గించండి.")
            else:
                insights.append(f"❄️ Cool weather ({temp}°C): Increase natural ventilation and reduce cooling usage.")
        
        if humidity > 70:
            if language == 'te':
                insights.append(f"💧 అధిక తేమ ({humidity}%): డీహ్యూమిడిఫైయర్‌ను జాగ్రత్తగా ఉపయోగించండి - ఇది శక్తిని వినియోగిస్తుంది.")
            else:
                insights.append(f"💧 High humidity ({humidity}%): Use dehumidifiers cautiously - they consume energy.")
    
    # 4. ACTIONABLE SAVINGS TIPS (Utility-Specific)
    if bill_type == 'water':
        # Water-specific tips
        if forecast_value > 25:  # High water consumption (> 25 KL)
            if language == 'te':
                water_tips = [
                    "🚿 తక్కువ ప్రవాహ షవర్‌హెడ్స్ వాడండి - 50% నీటి ఆదా",
                    "🚰 కుళాయిల లీక్స్ తక్షణం సరిచేయండి - 1 చుక్క/సెకను = 15 KL/నెల వృధా",
                    "🌱 మొక్కలకు ఉదయం/సాయంత్రం నీరు పెట్టండి - తక్కువ బాష్పీభవనం",
                    "♻️ బాత్రూమ్ నీటిని తోటకు మళ్లించండి (గ్రేవాటర్)"
                ]
            else:
                water_tips = [
                    "🚿 Install low-flow showerheads - save 50% water",
                    "🚰 Fix tap leaks immediately - 1 drip/sec = 15 KL/month wasted",
                    "🌱 Water plants in morning/evening - less evaporation",
                    "♻️ Reuse bathroom water for garden (greywater recycling)"
                ]
            insights.extend(water_tips[:2])
    else:
        # Electricity-specific tips
        if forecast_value > 300:  # High electricity consumption
            if language == 'te':
                savings_tips = [
                    "💡 LED బల్బులకు మారండి - 80% వరకు ఆదా చేయండి",
                    "🔌 ఉపయోగంలో లేనప్పుడు పరికరాలను అన్‌ప్లగ్ చేయండి (ఫాంటమ్ లోడ్)",
                    "⏰ పీక్ అవర్లకు (6-9 PM) వెలుపల భారీ ఉపకరణాలను ఉపయోగించండి",
                    "🌡️ AC థర్మోస్టాట్‌ను 24-26°C కు సెట్ చేయండి"
                ]
            else:
                savings_tips = [
                    "💡 Switch to LED bulbs - save up to 80%",
                    "🔌 Unplug devices when not in use (phantom load)",
                    "⏰ Use heavy appliances outside peak hours (6-9 PM)",
                    "🌡️ Set AC thermostat to 24-26°C"
                ]
            insights.extend(savings_tips[:2])
    
    # 5. FORECAST-SPECIFIC ADVICE
    if forecast_value > 0:
        if language == 'te':
            insights.append(f"🎯 వచ్చే నెల లక్ష్యం: {forecast_value - 50:.0f} యూనిట్ల క్రింద ఉంచడానికి ప్రయత్నించండి.")
        else:
            insights.append(f"🎯 Target for next month: Try to stay below {forecast_value - 50:.0f} units.")
    
    # 6. NO DATA CASE
    if not insights:
        if language == 'te':
            return "📊 మరింత వ్యక్తిగత సిఫార్సుల కోసం మరిన్ని బిల్లులను అప్‌లోడ్ చేయండి."
        else:
            return "📊 Upload more bills for personalized recommendations."
    
    # Combine all insights
    return " ".join(insights)
