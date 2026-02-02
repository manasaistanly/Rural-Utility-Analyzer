import { useEffect, useState } from 'react';
import API_BASE_URL from '../config';
import { useLanguage } from '../context/LanguageContext';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Volume2, Sun, Droplets, Zap, Eye, FileText, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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

    // New State for Bill History
    const [bills, setBills] = useState<any[]>([]);
    const [selectedBill, setSelectedBill] = useState<any | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const token = localStorage.getItem('token');
                if (!token) return;

                const headers = { 'Authorization': `Bearer ${token}` };

                // 1. Fetch Forecast & Stats
                const forecastRes = await fetch(`${API_BASE_URL}/analysis/forecast?lang=${language}&bill_type=${billType}`, { headers });
                const forecastData = await forecastRes.json();

                setStats({
                    total_units: forecastData.stats?.total_units || 0,
                    total_cost: forecastData.stats?.total_cost || 0
                });
                setChartData(forecastData.chart_data || []);
                setForecast({
                    nextMonth: Math.round(forecastData.forecast || 0),
                    cost: Math.round(forecastData.forecast_cost || 0),
                    recommendation: forecastData.recommendation || '',
                    currentWeather: forecastData.current_weather || { temp: 0, humidity: 0, desc: '' }
                });

                // 2. Fetch Bill History
                // Note: The /bills endpoint returns ALL bills. We filter client-side or could add backend filter.
                // Assuming /bills returns all for user.
                const billsRes = await fetch(`${API_BASE_URL}/bills/`, { headers });
                const billsData = await billsRes.json();

                // Validate billsData is an array before filtering
                if (Array.isArray(billsData)) {
                    // Filter bills by current type and sort by date descending
                    const filteredBills = billsData
                        .filter((b: any) => b.bill_type === billType)
                        .sort((a: any, b: any) => new Date(b.bill_date).getTime() - new Date(a.bill_date).getTime());

                    setBills(filteredBills);
                } else {
                    console.error('Bills API did not return an array:', billsData);
                    setBills([]);
                }

            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [language, billType]);

    const speak = (text: string) => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            setIsSpeaking(true);
            const utterance = new SpeechSynthesisUtterance(text);

            const loadAndSpeak = () => {
                const voices = window.speechSynthesis.getVoices();
                if (voices.length > 0) {
                    setVoiceAndSpeak(utterance, voices);
                } else {
                    // Wait for voices
                    const voiceHandler = () => {
                        const updatedVoices = window.speechSynthesis.getVoices();
                        if (updatedVoices.length > 0) {
                            setVoiceAndSpeak(utterance, updatedVoices);
                            window.speechSynthesis.removeEventListener('voiceschanged', voiceHandler);
                        }
                    };
                    window.speechSynthesis.addEventListener('voiceschanged', voiceHandler);

                    // Fallback if voices never load
                    setTimeout(() => {
                        window.speechSynthesis.removeEventListener('voiceschanged', voiceHandler);
                        const fallbackVoices = window.speechSynthesis.getVoices();
                        if (fallbackVoices.length === 0) {
                            console.warn("Voices timed out, attempting default voice");
                            setVoiceAndSpeak(utterance, []);
                        }
                    }, 3000);
                }
            };

            loadAndSpeak();

        } else {
            alert(language === 'en' ? "Browser does not support text-to-speech" : "బ్రౌజర్ టెక్స్ట్-టు-స్పీచ్‌కు మద్దతు ఇవ్వదు");
        }
    };

    const setVoiceAndSpeak = (utterance: SpeechSynthesisUtterance, voices: SpeechSynthesisVoice[]) => {
        utterance.lang = language === 'te' ? 'te-IN' : 'en-US';
        utterance.rate = 0.85;

        // Try to find a native Telugu voice
        let teluguVoice = null;
        if (language === 'te') {
            teluguVoice = voices.find(v => v.name.includes('Google') && v.lang === 'te-IN') ||
                voices.find(v => v.lang === 'te-IN') ||
                voices.find(v => v.lang.startsWith('te')) ||
                voices.find(v => v.name.toLowerCase().includes('telugu'));
        }

        // If native voice found, use it
        if (teluguVoice || language === 'en') {
            if (teluguVoice) {
                utterance.voice = teluguVoice;
                console.log("Using native Telugu voice:", teluguVoice.name);
            }
            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = (e) => {
                console.error("Speech synthesis error:", e);
                setIsSpeaking(false);
            };
            window.speechSynthesis.speak(utterance);
        } else {
            // FALLBACK: Use Backend TTS Proxy (gTTS)
            console.warn("No native Telugu voice found. Using Backend TTS Fallback.");
            // Cancel any pending speech
            window.speechSynthesis.cancel();

            try {
                const text = utterance.text;
                const encodedText = encodeURIComponent(text);
                // Use backend endpoint
                const audio = new Audio(`${API_BASE_URL}/tts/speak?text=${encodedText}&lang=${language === 'te' ? 'te' : 'en'}`);

                audio.onended = () => setIsSpeaking(false);
                audio.onerror = (e) => {
                    console.error("Audio fallback error:", e);
                    setIsSpeaking(false);
                };

                audio.play();
            } catch (err) {
                console.error("Fallback failed:", err);
                setIsSpeaking(false);
            }
        }
    };

    const handleVoiceSummary = () => {
        if (loading) return;
        let summary = '';
        if (language === 'en') {
            summary = `Current weather is ${forecast.currentWeather.temp} degrees. Your forecasted ${billType} consumption is ${forecast.nextMonth} units. ${forecast.recommendation}`;
        } else {
            // Telugu summary construction (Simplified)
            summary = `ప్రస్తుత వాతావరణం ${Math.round(forecast.currentWeather.temp)} డిగ్రీలు. మీ ${billType === 'water' ? 'నీటి' : 'విద్యుత్'} వినియోగం ${forecast.nextMonth} యూనిట్లు. ${forecast.recommendation}`;
        }
        speak(summary);
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

    // Helper to get image URL
    const getImageUrl = (path: string) => {
        if (!path) return '';
        // Path might be "data/uploads/filename.jpg". We need "filename.jpg"
        const filename = path.split('/').pop()?.split('\\').pop(); // Handle both / and \
        // Construct the full URL using API_BASE_URL. 
        // Note: API_BASE_URL is usually .../api/v1. We need to go up to root to access /static if it's mounted at root.
        // Assuming API_BASE_URL is http://localhost:8000/api/v1
        const baseUrl = API_BASE_URL.replace('/api/v1', '');
        return `${baseUrl}/static/${filename}`;
    };

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
                    <div className="flex gap-2 bg-white/70 p-1.5 rounded-2xl border border-gray-200">
                        <button onClick={() => setBillType('electricity')} className={`px-4 py-2 rounded-xl font-semibold transition-all text-sm ${billType === 'electricity' ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-md' : 'text-gray-600 hover:bg-gray-100'}`}>⚡ Electricity</button>
                        <button onClick={() => setBillType('water')} className={`px-4 py-2 rounded-xl font-semibold transition-all text-sm ${billType === 'water' ? 'bg-gradient-to-r from-blue-500 to-cyan-600 text-white shadow-md' : 'text-gray-600 hover:bg-gray-100'}`}>💧 Water</button>
                    </div>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card title={`${t('units')} (Total)`} value={`${Math.round(stats.total_units)} ${billType === 'water' ? 'KL' : 'kWh'}`} icon={Zap} color="border-emerald-500" delay={0.1} />
                <Card title={`${t('amount')} (Total)`} value={`₹ ${Math.round(stats.total_cost)}`} icon={Droplets} color="border-orange-500" delay={0.2} />
                <Card title={t('forecast')} value={`₹ ${forecast.cost} (${forecast.nextMonth} ${billType === 'water' ? 'KL' : 'kWh'})`} icon={Sun} color="border-blue-500" delay={0.3} />
            </div>

            {/* Recommendations */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-card p-6 border border-emerald-200 bg-gradient-to-r from-emerald-50 to-teal-50">
                <div className="flex items-start space-x-4">
                    <div className="bg-emerald-500 p-3 rounded-full text-white mt-1 shadow-lg"><Sun className="w-7 h-7" /></div>
                    <div>
                        <h3 className="text-2xl font-heading font-bold text-emerald-700 mb-2">{t('recommendation')}</h3>
                        <p className="text-lg text-gray-800 leading-relaxed font-medium">
                            {forecast.recommendation || (language === 'en' ? "Loading recommendation..." : "సిఫార్సు లోడ్ అవుతోంది...")}
                        </p>
                    </div>
                    <button onClick={handleVoiceSummary} disabled={isSpeaking} className="mt-2 text-emerald-600 font-bold flex items-center gap-2 hover:text-emerald-800"><Volume2 className="w-5 h-5" /> {isSpeaking ? 'Listening...' : 'Listen'}</button>
                </div>
            </motion.div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} className="glass-card p-6 bg-white/50">
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">📊 {language === 'en' ? 'Consumption Trend' : 'వినియోగ ధోరణి'}</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={chartData}>
                            <defs><linearGradient id="colorConsumption" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#10b981" stopOpacity={0.8} /><stop offset="95%" stopColor="#10b981" stopOpacity={0} /></linearGradient></defs>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Area type="monotone" dataKey="consumption" stroke="#10b981" fillOpacity={1} fill="url(#colorConsumption)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </motion.div>
                <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} className="glass-card p-6 bg-white/50">
                    <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">💰 {language === 'en' ? 'Cost Analysis' : 'ఖర్చు విశ్లేషణ'}</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="cost" fill="#d84315" radius={[8, 8, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </motion.div>
            </div>

            {/* NEW: Bill History Section */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="glass-card p-6">
                <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                    <FileText className="w-6 h-6 text-indigo-600" />
                    {language === 'en' ? 'Recent Bills' : 'నా బిల్లులు'}
                </h3>

                {bills.length === 0 ? (
                    <p className="text-gray-500 italic text-center py-8">{language === 'en' ? 'No bills uploaded yet.' : 'ఇంకా ఎలాంటి బిల్లులు అప్‌లోడ్ చేయలేదు.'}</p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-gray-200 text-gray-600 text-sm uppercase">
                                    <th className="py-3 px-4">{language === 'en' ? 'Date' : 'తేదీ'}</th>
                                    <th className="py-3 px-4">{language === 'en' ? 'Units' : 'యూనిట్లు'}</th>
                                    <th className="py-3 px-4">{language === 'en' ? 'Amount' : 'మొత్తం'}</th>
                                    <th className="py-3 px-4 text-center">{language === 'en' ? 'Action' : 'చర్య'}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {bills.map((bill) => (
                                    <tr key={bill.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                        <td className="py-3 px-4 font-medium text-gray-800">{bill.bill_date}</td>
                                        <td className="py-3 px-4 text-gray-600 font-bold">{bill.units_consumed} {bill.bill_type === 'water' ? 'KL' : 'kWh'}</td>
                                        <td className="py-3 px-4 text-emerald-600 font-bold">₹{bill.total_amount}</td>
                                        <td className="py-3 px-4 text-center">
                                            <button
                                                onClick={() => setSelectedBill(bill)}
                                                className="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-lg hover:bg-indigo-100 transition-colors text-sm font-semibold"
                                            >
                                                <Eye className="w-4 h-4" /> {language === 'en' ? 'View' : 'చూడండి'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </motion.div>

            {/* Bill Image Modal */}
            <AnimatePresence>
                {selectedBill && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setSelectedBill(null)}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking content
                            className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
                        >
                            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                                <h3 className="font-bold text-lg text-gray-800">
                                    {language === 'en' ? 'Bill Details' : 'బిల్లు వివరాలు'} - {selectedBill.bill_date}
                                </h3>
                                <button onClick={() => setSelectedBill(null)} className="p-2 hover:bg-gray-200 rounded-full transition-colors"><X className="w-5 h-5 text-gray-500" /></button>
                            </div>

                            <div className="p-6 overflow-y-auto flex flex-col md:flex-row gap-8">
                                <div className="flex-1 bg-gray-100 rounded-xl overflow-hidden border border-gray-200 flex items-center justify-center min-h-[300px]">
                                    <img
                                        src={getImageUrl(selectedBill.image_path)}
                                        alt="Bill"
                                        className="max-w-full max-h-[600px] object-contain"
                                        onError={(e: any) => { e.target.src = 'https://via.placeholder.com/400?text=Image+Not+Found'; }}
                                    />
                                </div>

                                <div className="w-full md:w-80 space-y-6">
                                    <div className="space-y-4">
                                        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                                            <p className="text-xs uppercase text-blue-600 font-bold mb-1">Consumption</p>
                                            <p className="text-2xl font-bold text-gray-900">{selectedBill.units_consumed} <span className="text-sm text-gray-500">{selectedBill.bill_type === 'water' ? 'KL' : 'kWh'}</span></p>
                                        </div>
                                        <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100">
                                            <p className="text-xs uppercase text-emerald-600 font-bold mb-1">Total Cost</p>
                                            <p className="text-2xl font-bold text-gray-900">₹{selectedBill.total_amount}</p>
                                        </div>
                                    </div>

                                    <div className="pt-4 border-t border-gray-100">
                                        <p className="text-sm text-gray-500 mb-2">Verified Status:</p>
                                        <div className="flex items-center gap-2 text-emerald-600 font-semibold bg-emerald-50 px-3 py-1 rounded-full w-fit">
                                            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                                            Verified by AI
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Dashboard;
