import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'en' | 'te';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string) => string;
}

const translations = {
    en: {
        "app.title": "Smart Rural Utility Analyzer",
        "login": "Login",
        "register": "Register",
        "dashboard": "Dashboard",
        "upload": "Upload Bill",
        "forecast": "Forecast",
        "welcome": "Welcome back",
        "units": "Units Consumed",
        "amount": "Total Amount",
        "electricity": "Electricity",
        "water": "Water",
        "analyze": "Analyze",
        "logout": "Logout",
        "members": "Family Members",
        "submit": "Submit",
        "upload_instruction": "Take a photo of your bill or upload an image",
        "alert": "Alert",
        "recommendation": "Recommendation",
    },
    te: {
        "app.title": "గ్రామీణ వినియోగ విశ్లేషణ",
        "login": "లాగిన్",
        "register": "నమోదు",
        "dashboard": "డాష్‌బోర్డ్",
        "upload": "బిల్లు అప్‌లోడ్",
        "forecast": "మేము అంచనా",
        "welcome": "స్వాగతం",
        "units": "వినియోగించిన యూనిట్లు",
        "amount": "మొత్తం చెల్లించాల్సినది",
        "electricity": "కరెంట్",
        "water": "నీరు",
        "analyze": "విశ్లేషించండి",
        "logout": "లాగౌట్",
        "members": "కుటుంబ సభ్యులు",
        "submit": "సమర్పించు",
        "upload_instruction": "మీ బిల్లు ఫోటో తీయండి లేదా అప్‌లోడ్ చేయండి",
        "alert": "హెచ్చరిక",
        "recommendation": "సలహా",
    }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: React.ReactNode }) => {
    const [language, setLanguage] = useState<Language>('en');

    const t = (key: string) => {
        return translations[language][key as keyof typeof translations['en']] || key;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};
