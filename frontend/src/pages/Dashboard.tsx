import React, { useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Volume2, Sun, Droplets, Zap, VolumeX } from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard = () => {
    const { t, language } = useLanguage();
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [billType, setBillType] = useState<'electricity' | 'water'>('electricity');

    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total_units: 0, total_cost: 0 });
    const [chartData, setChartData] = useState<any[]>([]);
    const [forecast, setForecast] = useState({
        nextMonth: 0,
        cost: 0,
        recommendation: '',
        currentWeather: { temp: 0, humidity: 0, desc: '' }
    });

    useEffect(() => {
        const fetchForecast = async () => {
            setLoading(true); // Reset loading state when billType changes
            try {
                const token = localStorage.getItem('token');
                console.log(`Fetching forecast for bill_type: ${billType}`); // Debug log
                const response = await fetch(`http://localhost:8001/api/v1/analysis/forecast?lang=${language}&bill_type=${billType}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();

                console.log(`Received data for ${billType}:`, data); // Debug log

                setStats({
                    total_units: data.stats?.total_units || 0,
                    total_cost: data.stats?.total_cost || 0
                });

                setChartData(data.chart_data || []);

                setForecast({
                    nextMonth: Math.round(data.forecast || 0),
                    cost: Math.round(data.forecast_cost || 0),
                    recommendation: data.recommendation || '',
                    currentWeather: data.current_weather || { temp: 0, humidity: 0, desc: '' }
                });
            } catch (error) {
                console.error('Error fetching forecast:', error);
                setForecast(prev => ({
                    ...prev,
                    recommendation: language === 'en'
                        ? "Unable to fetch live forecast. Please check connection."
                        : "ప్రత్యక్ష అంచనాను పొందడం సాధ్యం కాదు. దయచేసి కనెక్షన్‌ని తనిఖీ చేయండి."
                }));
            } finally {
                setLoading(false);
            }
        };

        fetchForecast();
    }, [language, billType]); // Refetch when language or bill type changes

    const speak = (text: string) => {
        if ('speechSynthesis' in window) {
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();

            setIsSpeaking(true);
            const utterance = new SpeechSynthesisUtterance(text);

            // 1. Load Voices
            let voices = window.speechSynthesis.getVoices();

            // Handle async voice loading (Chrome/Safari quirk)
            if (voices.length === 0) {
                window.speechSynthesis.onvoiceschanged = () => {
                    voices = window.speechSynthesis.getVoices();
                    setVoiceAndSpeak(utterance, voices);
                };
            } else {
                setVoiceAndSpeak(utterance, voices);
            }
        } else {
            alert(language === 'en' ? "Browser does not support text-to-speech" : "బ్రౌజర్ టెక్స్ట్-టు-స్పీచ్‌కు మద్దతు ఇవ్వదు");
        }
    };

    const setVoiceAndSpeak = (utterance: SpeechSynthesisUtterance, voices: SpeechSynthesisVoice[]) => {
        utterance.lang = language === 'te' ? 'te-IN' : 'en-US';
        utterance.rate = 0.85; // Slower for better clarity

        // 2. Explicitly find a Telugu voice if needed
        if (language === 'te') {
            // Priority 1: Exact 'te-IN' match
            // Priority 2: 'te' language code
            // Priority 3: 'telugu' in name
            // Priority 4: ANY 'India' voice (Best effort fallback)
            const teluguVoice = voices.find(v => v.lang === 'te-IN') ||
                voices.find(v => v.lang.startsWith('te')) ||
                voices.find(v => v.name.toLowerCase().includes('telugu')) ||
                voices.find(v => v.name.toLowerCase().includes('india'));

            if (teluguVoice) {
                utterance.voice = teluguVoice;
                // Silent log for developers, no alert for users
                console.log("Using best match voice:", teluguVoice.name);
            } else {
                console.warn("No Indian/Telugu voice found. Using system default.");
            }
        }

        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = (e) => {
            setIsSpeaking(false);
            console.error("Speech synthesis error", e);
            // DEBUG: Alert the meaningful error code
            if (e.error !== 'interrupted') { // Ignore if user clicked Stop
                alert(`Speech Error: ${e.error}\n\nThis usually means:\n- 'not-allowed': User permission denied.\n- 'network': No internet for online voice.\n- 'synthesis-failed': Browser engine crashed.`);
            }
        };

        try {
            window.speechSynthesis.cancel(); // Cancel any previous speech
            window.speechSynthesis.speak(utterance);
        } catch (err) {
            console.error("Speak call failed:", err);
            alert("Critical Error: Browser refused to speak.");
        }
    };

    // Helper to convert numbers to Telugu words
    const numToTelugu = (n: number): string => {
        const units = ['', 'ఒకటి', 'రెండు', 'మూడు', 'నాలుగు', 'ఐదు', 'ఆరు', 'ఏడు', 'ఎనిమిది', 'తొమ్మిది'];
        const teens = ['పది', 'పదకొండు', 'పన్నెండు', 'పదమూడు', 'పద్నాలుగు', 'పదిహేను', 'పదహారు', 'పదిహేడు', 'పద్దెనిమిది', 'పంతొమ్మిది'];
        const tens = ['', '', 'ఇరవై', 'ముప్పై', 'నలభై', 'యాభై', 'అరవై', 'డెబ్బై', 'ఎనభై', 'తొంభై'];

        if (n === 0) return 'సున్నా';
        if (n < 10) return units[n];
        if (n < 20) return teens[n - 10];
        if (n < 100) return tens[Math.floor(n / 10)] + (n % 10 !== 0 ? ' ' + units[n % 10] : '');
        if (n < 1000) return units[Math.floor(n / 100)] + ' వందల ' + (n % 100 !== 0 ? numToTelugu(n % 100) : '');
        return n.toString();
    };

    const handleVoiceSummary = () => {
        if (loading) return;

        let summary = '';
        if (language === 'en') {
            summary = `Current weather in Hyderabad is ${forecast.currentWeather.temp} degrees Celsius with ${forecast.currentWeather.humidity} percent humidity. Your forecasted electricity consumption for next month is ${forecast.nextMonth} units. Recommendation: ${forecast.recommendation}`;
        } else {
            // Convert numbers to Telugu words
            const temp = Math.round(forecast.currentWeather.temp);
            const hum = Math.round(forecast.currentWeather.humidity);
            const units = Math.round(forecast.nextMonth);

            const tempTe = numToTelugu(temp);
            const humTe = numToTelugu(hum);
            const unitsTe = numToTelugu(units);

            summary = `హైదరాబాద్‌లో ప్రస్తుత వాతావరణం ${tempTe} డిగ్రీల సెల్సియస్, తేమ ${humTe} శాతం. వచ్చే నెల మీ విద్యుత్ వినియోగ అంచనా ${unitsTe} యూనిట్లు. సూచన: ${forecast.recommendation}`;
        }
        speak(summary);
    };

    const stopSpeech = () => {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
    };

    const Card = ({ title, value, icon: Icon, color, delay }: any) => (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay }}
            className={`glass-card p-6 border-l-4 ${color}`}
        >
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="text-gray-600 font-bold text-sm uppercase tracking-wide">{title}</h3>
                    <p className="text-3xl font-heading font-bold mt-2 text-gray-900">{value}</p>
                </div>
                <div className={`p-3 rounded-full ${color.replace('border-', 'bg-').replace('500', '100')}`}>
                    <Icon className={`w-6 h-6 ${color.replace('border-', 'text-')}`} />
                </div>
            </div>
        </motion.div>
    );

    return (
        <div className="space-y-8 p-4">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                <div>
                    <h1 className="text-4xl font-heading font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                        {t('dashboard')}
                    </h1>
                    <p className="text-gray-600 mt-1 text-lg">
                        {language === 'en' ? `Welcome back, ${localStorage.getItem('username') || 'User'}` : `స్వాగతం, ${localStorage.getItem('username') || 'వినియోగదారు'}`}
                    </p>
                </div>

                <div className="flex gap-3 flex-wrap items-center">
                    {/* Utility Type Tabs */}
                    <div className="flex gap-2 bg-white/70 p-1.5 rounded-2xl border border-gray-200">
                        <button
                            onClick={() => setBillType('electricity')}
                            className={`px-4 py-2 rounded-xl font-semibold transition-all text-sm ${billType === 'electricity'
                                ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-md'
                                : 'text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            ⚡ Electricity
                        </button>
                        <button
                            onClick={() => setBillType('water')}
                            className={`px-4 py-2 rounded-xl font-semibold transition-all text-sm ${billType === 'water'
                                ? 'bg-gradient-to-r from-blue-500 to-cyan-600 text-white shadow-md'
                                : 'text-gray-600 hover:bg-gray-100'
                                }`}
                        >
                            💧 Water
                        </button>
                    </div>

                    {/* Voice Summary Button */}
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleVoiceSummary}
                        disabled={isSpeaking}
                        className={`flex items-center space-x-3 px-6 py-3 rounded-2xl font-bold shadow-xl transition-all ${isSpeaking
                            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white animate-pulse'
                            : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:shadow-2xl'
                            }`}
                    >
                        <Volume2 className="w-6 h-6" />
                        <span className="text-lg">
                            {isSpeaking
                                ? (language === 'en' ? 'Playing...' : 'ప్లే అవుతోంది...')
                                : (language === 'en' ? 'Play Summary' : 'సారాంశం వినండి')
                            }
                        </span>
                    </motion.button>

                    {isSpeaking && (
                        <motion.button
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            onClick={stopSpeech}
                            className="flex items-center space-x-2 bg-red-500 text-white px-4 py-3 rounded-2xl font-bold shadow-lg hover:bg-red-600"
                        >
                            <VolumeX className="w-5 h-5" />
                            <span>{language === 'en' ? 'Stop' : 'ఆపండి'}</span>
                        </motion.button>
                    )}
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card
                    title={`${t('units')} (Total)`}
                    value={`${Math.round(stats.total_units)} ${billType === 'water' ? 'KL' : 'kWh'}`}
                    icon={Zap}
                    color="border-emerald-500"
                    delay={0.1}
                />
                <Card title={`${t('amount')} (Total)`} value={`₹ ${Math.round(stats.total_cost)}`} icon={Droplets} color="border-orange-500" delay={0.2} />
                <Card
                    title={t('forecast')}
                    value={`₹ ${forecast.cost} (${forecast.nextMonth} ${billType === 'water' ? 'KL' : 'kWh'})`}
                    icon={Sun}
                    color="border-blue-500"
                    delay={0.3}
                />
            </div >

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card p-6 bg-white/50"
                >
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                        📊 {language === 'en'
                            ? `${billType === 'water' ? 'Water' : 'Electricity'} Consumption Trend`
                            : `${billType === 'water' ? 'నీటి' : 'విద్యుత్'} వినియోగ ధోరణి`}
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={chartData.length > 0 ? chartData : [{ month: 'No Data', consumption: 0 }]}>
                            <defs>
                                <linearGradient id="colorConsumption" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis dataKey="month" stroke="#6b7280" />
                            <YAxis stroke="#6b7280" label={{ value: billType === 'water' ? 'KL' : 'kWh', angle: -90, position: 'insideLeft' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                                formatter={(value: any) => [`${value} ${billType === 'water' ? 'KL' : 'kWh'}`, 'Consumption']}
                            />
                            <Area type="monotone" dataKey="consumption" stroke="#10b981" fillOpacity={1} fill="url(#colorConsumption)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="glass-card p-6 bg-white/50"
                >
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                        💰 {language === 'en'
                            ? `${billType === 'water' ? 'Water' : 'Electricity'} Cost Analysis`
                            : `${billType === 'water' ? 'నీటి' : 'విద్యుత్'} ఖర్చు విశ్లేషణ`}
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={chartData.length > 0 ? chartData : [{ month: 'No Data', cost: 0 }]}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis dataKey="month" stroke="#6b7280" />
                            <YAxis stroke="#6b7280" label={{ value: '₹', angle: -90, position: 'insideLeft' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                                formatter={(value: any) => [`₹${value}`, 'Cost']}
                            />
                            <Bar dataKey="cost" fill="#d84315" radius={[8, 8, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </motion.div>
            </div >

            {/* Recommendations */}
            < motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="glass-card p-6 border border-emerald-200 bg-gradient-to-r from-emerald-50 to-teal-50"
            >
                <div className="flex items-start space-x-4">
                    <div className="bg-emerald-500 p-3 rounded-full text-white mt-1 shadow-lg">
                        <Sun className="w-7 h-7" />
                    </div>
                    <div>
                        <h3 className="text-2xl font-heading font-bold text-emerald-700 mb-2">{t('recommendation')}</h3>
                        <p className="text-lg text-gray-800 leading-relaxed font-medium">
                            {forecast.recommendation || (language === 'en' ? "Loading recommendation..." : "సిఫార్సు లోడ్ అవుతోంది...")}
                        </p>
                    </div>
                </div>
            </motion.div >
        </div >
    );
};

export default Dashboard;
