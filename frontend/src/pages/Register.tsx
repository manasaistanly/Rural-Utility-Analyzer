import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { Lock, User, Zap, ArrowRight, Loader2, Mail } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';
import API_BASE_URL from '../config';

const Register = () => {
    const { language, setLanguage } = useLanguage();
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    const handleRegister = async (e: FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError(language === 'en' ? 'Passwords do not match' : 'పాస్‌వర్డ్‌లు సరిపోలడం లేదు');
            return;
        }

        if (password.length < 6) {
            setError(language === 'en' ? 'Password must be at least 6 characters' : 'పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి');
            return;
        }

        setLoading(true);

        try {
            await axios.post(`${API_BASE_URL}/auth/register`, {
                username,
                email: email || null,
                password,
                language_pref: language,
            });

            setSuccess(language === 'en'
                ? 'Registration successful! Redirecting to login...'
                : 'నమోదు విజయవంతమైంది! లాగిన్‌కు మళ్లిస్తోంది...');

            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err: any) {
            console.error('Registration error:', err);
            if (err.response?.status === 400) {
                setError(language === 'en' ? 'Username already exists' : 'వినియోగదారు పేరు ఇప్పటికే ఉంది');
            } else {
                setError(language === 'en' ? 'Registration failed. Please try again.' : 'నమోదు విఫలమైంది. దయచేసి మళ్లీ ప్రయత్నించండి.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 p-4">
            {/* Animated Background Blobs */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-0 w-96 h-96 bg-emerald-300 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
                <div className="absolute top-0 right-0 w-96 h-96 bg-teal-300 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
                <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-cyan-300 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="relative z-10 w-full max-w-md bg-white/90 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white"
            >
                <div className="flex flex-col items-center mb-6">
                    <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                        <Zap className="w-9 h-9 text-white" />
                    </div>
                    <h2 className="text-3xl font-heading font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent text-center">
                        {language === 'en' ? 'Create Account' : 'ఖాతా సృష్టించండి'}
                    </h2>
                    <p className="text-gray-600 mt-2 text-center font-medium">
                        {language === 'en' ? 'Join Smart Rural Utility' : 'స్మార్ట్ గ్రామీణ యుటిలిటీలో చేరండి'}
                    </p>
                </div>

                <div className="flex justify-center mb-6 bg-gray-100 p-1.5 rounded-full w-fit mx-auto">
                    <button
                        onClick={() => setLanguage('en')}
                        className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${language === 'en' ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800'}`}
                    >
                        English
                    </button>
                    <button
                        onClick={() => setLanguage('te')}
                        className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${language === 'te' ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-md' : 'text-gray-600 hover:text-gray-800'}`}
                    >
                        తెలుగు
                    </button>
                </div>

                <form onSubmit={handleRegister} className="space-y-4">
                    <div>
                        <label className="block text-gray-800 text-sm font-bold mb-2">
                            {language === 'en' ? 'Username' : 'వినియోగదారు పేరు'}
                        </label>
                        <div className="flex items-center border-2 border-gray-300 rounded-xl px-4 py-3 bg-white focus-within:border-emerald-500 transition-all">
                            <User className="text-emerald-600 w-5 h-5 mr-3" />
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-transparent outline-none text-gray-900 font-medium placeholder-gray-400"
                                placeholder={language === 'en' ? 'Choose a username' : 'వినియోగదారు పేరు ఎంచుకోండి'}
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-gray-800 text-sm font-bold mb-2">
                            {language === 'en' ? 'Email (optional)' : 'ఇమెయిల్ (ఐచ్ఛికం)'}
                        </label>
                        <div className="flex items-center border-2 border-gray-300 rounded-xl px-4 py-3 bg-white focus-within:border-emerald-500 transition-all">
                            <Mail className="text-emerald-600 w-5 h-5 mr-3" />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-transparent outline-none text-gray-900 font-medium placeholder-gray-400"
                                placeholder={language === 'en' ? 'yourname@example.com' : 'మీపేరు@example.com'}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-gray-800 text-sm font-bold mb-2">
                            {language === 'en' ? 'Password' : 'పాస్‌వర్డ్'}
                        </label>
                        <div className="flex items-center border-2 border-gray-300 rounded-xl px-4 py-3 bg-white focus-within:border-emerald-500 transition-all">
                            <Lock className="text-emerald-600 w-5 h-5 mr-3" />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-transparent outline-none text-gray-900 font-medium placeholder-gray-400"
                                placeholder="••••••"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-gray-800 text-sm font-bold mb-2">
                            {language === 'en' ? 'Confirm Password' : 'పాస్‌వర్డ్ నిర్ధారించండి'}
                        </label>
                        <div className="flex items-center border-2 border-gray-300 rounded-xl px-4 py-3 bg-white focus-within:border-emerald-500 transition-all">
                            <Lock className="text-emerald-600 w-5 h-5 mr-3" />
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="w-full bg-transparent outline-none text-gray-900 font-medium placeholder-gray-400"
                                placeholder="••••••"
                                required
                            />
                        </div>
                    </div>

                    {error && <p className="text-red-600 text-sm text-center font-semibold bg-red-50 p-3 rounded-xl">{error}</p>}
                    {success && <p className="text-green-600 text-sm text-center font-semibold bg-green-50 p-3 rounded-xl">{success}</p>}

                    <motion.button
                        whileHover={{ scale: loading ? 1 : 1.02 }}
                        whileTap={{ scale: loading ? 1 : 0.98 }}
                        type="submit"
                        disabled={loading}
                        className={`w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold py-4 text-lg rounded-xl shadow-lg hover:shadow-2xl transition-all flex items-center justify-center space-x-2 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-6 h-6 animate-spin" />
                                <span>{language === 'en' ? 'Creating Account...' : 'ఖాతా సృష్టిస్తోంది...'}</span>
                            </>
                        ) : (
                            <>
                                <span>{language === 'en' ? 'Create Account' : 'ఖాతా సృష్టించండి'}</span>
                                <ArrowRight className="w-6 h-6" />
                            </>
                        )}
                    </motion.button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-gray-600">
                        {language === 'en' ? 'Already have an account?' : 'ఇప్పటికే ఖాతా ఉందా?'}{' '}
                        <Link to="/login" className="text-emerald-600 font-bold hover:text-emerald-700">
                            {language === 'en' ? 'Login here' : 'ఇక్కడ లాగిన్ చేయండి'}
                        </Link>
                    </p>
                </div>
            </motion.div>

            <div className="absolute bottom-4 text-gray-600 text-sm font-medium">
                © 2026 Smart Rural Utility Project
            </div>

            <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
        </div>
    );
};

export default Register;
