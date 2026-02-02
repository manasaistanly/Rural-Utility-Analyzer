import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { Lock, User, Zap, ArrowRight, Loader2, UserPlus } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';
import API_BASE_URL from '../config';

const Login = () => {
    const { t, language, setLanguage } = useLanguage();
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post(`${API_BASE_URL}/auth/token`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            localStorage.setItem('token', response.data.access_token);
            localStorage.setItem('username', username);
            navigate('/dashboard');
        } catch (err: any) {
            console.error('Login error:', err);
            if (err.response?.status === 401) {
                setError(language === 'en' ? 'Invalid username or password' : 'తప్పు వినియోగదారు పేరు లేదా పాస్‌వర్డ్');
            } else {
                setError(language === 'en' ? 'Login failed. Please try again.' : 'లాగిన్ విఫలమైంది. దయచేసి మళ్లీ ప్రయత్నించండి.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 p-4 relative overflow-hidden">
            {/* Decorative Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -left-40 w-[800px] h-[800px] bg-emerald-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
                <div className="absolute top-0 -right-40 w-[600px] h-[600px] bg-teal-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
                <div className="absolute -bottom-40 left-1/2 transform -translate-x-1/2 w-[800px] h-[800px] bg-cyan-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6 }}
                className="relative z-10 w-full max-w-lg bg-white/80 backdrop-blur-xl p-10 rounded-[2.5rem] shadow-2xl border border-white/60"
            >
                <div className="flex flex-col items-center mb-10">
                    <motion.div
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl flex items-center justify-center mb-6 shadow-xl shadow-emerald-500/20"
                    >
                        <Zap className="w-10 h-10 text-white" />
                    </motion.div>
                    <h2 className="text-4xl font-heading font-bold bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text text-transparent text-center mb-2">
                        {t('app.title')}
                    </h2>
                    <p className="text-gray-600 text-center font-medium text-lg">
                        {language === 'en' ? 'Empowering Rural India' : 'గ్రామీణ సాధికారత'}
                    </p>
                </div>

                <div className="flex justify-center mb-10">
                    <div className="bg-gray-100/80 p-1.5 rounded-full flex shadow-inner">
                        <button
                            onClick={() => setLanguage('en')}
                            className={`px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-300 ${language === 'en' ? 'bg-white text-emerald-700 shadow-md' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                            English
                        </button>
                        <button
                            onClick={() => setLanguage('te')}
                            className={`px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-300 ${language === 'te' ? 'bg-white text-emerald-700 shadow-md' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                            తెలుగు
                        </button>
                    </div>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div className="space-y-2">
                        <label className="block text-gray-700 text-sm font-bold ml-1">
                            {language === 'en' ? 'Username' : 'వినియోగదారు పేరు'}
                        </label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <User className="h-5 w-5 text-emerald-500 group-focus-within:text-emerald-600 transition-colors" />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="block w-full pl-11 pr-4 py-4 bg-white border-2 border-gray-100 rounded-2xl text-gray-900 placeholder-gray-400 focus:outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all font-medium"
                                placeholder={language === 'en' ? 'Enter your username' : 'మీ వినియోగదారు పేరు'}
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="block text-gray-700 text-sm font-bold ml-1">
                            {language === 'en' ? 'Password' : 'పాస్‌వర్డ్'}
                        </label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <Lock className="h-5 w-5 text-emerald-500 group-focus-within:text-emerald-600 transition-colors" />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="block w-full pl-11 pr-4 py-4 bg-white border-2 border-gray-100 rounded-2xl text-gray-900 placeholder-gray-400 focus:outline-none focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all font-medium"
                                placeholder="••••••••"
                                required
                            />
                        </div>
                    </div>

                    {error && <p className="text-red-600 text-sm text-center font-bold bg-red-50 py-3 rounded-xl border border-red-100">{error}</p>}

                    <div className="space-y-4 pt-2">
                        <motion.button
                            whileHover={{ scale: 1.01 }}
                            whileTap={{ scale: 0.99 }}
                            type="submit"
                            disabled={loading}
                            className={`w-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold py-4 rounded-2xl shadow-lg shadow-emerald-600/20 hover:shadow-emerald-600/30 transition-all flex items-center justify-center space-x-2 text-lg ${loading ? 'opacity-80' : ''}`}
                        >
                            {loading ? (
                                <Loader2 className="w-6 h-6 animate-spin" />
                            ) : (
                                <>
                                    <span>{language === 'en' ? 'Login' : 'లాగిన్'}</span>
                                    <ArrowRight className="w-5 h-5" />
                                </>
                            )}
                        </motion.button>

                        <div className="relative flex py-2 items-center">
                            <div className="flex-grow border-t border-gray-200"></div>
                            <span className="flex-shrink-0 mx-4 text-gray-400 text-sm font-medium">
                                {language === 'en' ? 'New User?' : 'కొత్త వినియోగదారా?'}
                            </span>
                            <div className="flex-grow border-t border-gray-200"></div>
                        </div>

                        <Link to="/register">
                            <motion.button
                                whileHover={{ scale: 1.01, backgroundColor: '#f0fdf4' }}
                                whileTap={{ scale: 0.99 }}
                                type="button"
                                className="w-full bg-white border-2 border-emerald-100 text-emerald-700 font-bold py-4 rounded-2xl hover:border-emerald-200 hover:shadow-lg hover:shadow-emerald-500/5 transition-all flex items-center justify-center space-x-2"
                            >
                                <UserPlus className="w-5 h-5" />
                                <span>{language === 'en' ? 'Create New Account' : 'కొత్త ఖాతాను సృష్టించండి'}</span>
                            </motion.button>
                        </Link>
                    </div>
                </form>
            </motion.div>

            <div className="absolute bottom-6 text-emerald-800/60 text-sm font-medium text-center w-full">
                © 2026 Smart Rural Utility Project • Designed for Impact
            </div>

            <style>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
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

export default Login;
