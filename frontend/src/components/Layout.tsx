import { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { Menu, X, Home, Upload, LogOut, Zap, Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Layout = () => {
    const { t, language, setLanguage } = useLanguage();
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();

    const navItems = [
        { path: '/dashboard', label: 'dashboard', icon: Home },
        { path: '/upload', label: 'upload', icon: Upload },
    ];

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 overflow-hidden">
            {/* Animated Background Pattern */}
            <div className="fixed inset-0 opacity-30 pointer-events-none">
                <div className="absolute top-0 left-0 w-96 h-96 bg-emerald-300 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
                <div className="absolute top-0 right-0 w-96 h-96 bg-teal-300 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
                <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-cyan-300 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
            </div>

            {/* Desktop Sidebar */}
            <motion.aside
                initial={{ x: -300 }}
                animate={{ x: 0 }}
                className="hidden md:flex flex-col w-72 bg-white/80 backdrop-blur-xl shadow-2xl border-r border-white/50 relative z-10"
            >
                <div className="p-6 border-b border-emerald-100">
                    <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg">
                            <Zap className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-800">Smart Utility</h1>
                            <p className="text-xs text-gray-500">Rural Analytics</p>
                        </div>
                    </div>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className="group"
                        >
                            <motion.div
                                whileHover={{ scale: 1.02, x: 4 }}
                                whileTap={{ scale: 0.98 }}
                                className={`flex items-center space-x-3 p-4 rounded-2xl transition-all ${location.pathname === item.path
                                    ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/50'
                                    : 'text-gray-700 hover:bg-white/60'
                                    }`}
                            >
                                <item.icon className="w-5 h-5" />
                                <span className="font-medium">{t(item.label)}</span>
                            </motion.div>
                        </Link>
                    ))}
                </nav>

                <div className="p-4 border-t border-emerald-100 space-y-3">
                    <button
                        onClick={() => setLanguage(language === 'en' ? 'te' : 'en')}
                        className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl hover:shadow-lg transition-all font-medium"
                    >
                        <Globe className="w-4 h-4" />
                        <span>{language === 'en' ? 'తెలుగు' : 'English'}</span>
                    </button>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-red-500 text-white rounded-2xl hover:bg-red-600 transition-all font-medium"
                    >
                        <LogOut className="w-4 h-4" />
                        <span>{t('logout')}</span>
                    </motion.button>
                </div>
            </motion.aside>

            {/* Mobile Header */}
            <div className="flex-1 flex flex-col overflow-hidden relative z-10">
                <header className="md:hidden flex items-center justify-between p-4 bg-white/80 backdrop-blur-xl shadow-lg">
                    <div className="flex items-center space-x-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
                            <Zap className="w-6 h-6 text-white" />
                        </div>
                        <span className="font-bold text-lg text-gray-800">Smart Utility</span>
                    </div>
                    <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-2 rounded-xl hover:bg-gray-100">
                        {isSidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </button>
                </header>

                {/* Mobile Sidebar */}
                <AnimatePresence>
                    {isSidebarOpen && (
                        <>
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden"
                                onClick={() => setSidebarOpen(false)}
                            />
                            <motion.div
                                initial={{ x: -300 }}
                                animate={{ x: 0 }}
                                exit={{ x: -300 }}
                                transition={{ type: 'spring', damping: 25 }}
                                className="fixed left-0 top-0 bottom-0 w-72 bg-white/95 backdrop-blur-xl shadow-2xl z-50 md:hidden p-4"
                            >
                                <div className="flex items-center justify-between mb-8">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
                                            <Zap className="w-6 h-6 text-white" />
                                        </div>
                                        <span className="font-bold text-lg">Smart Utility</span>
                                    </div>
                                    <button onClick={() => setSidebarOpen(false)} className="p-2">
                                        <X className="w-6 h-6" />
                                    </button>
                                </div>

                                <nav className="space-y-2">
                                    {navItems.map((item) => (
                                        <Link
                                            key={item.path}
                                            to={item.path}
                                            onClick={() => setSidebarOpen(false)}
                                            className={`flex items-center space-x-3 p-4 rounded-2xl transition-all ${location.pathname === item.path
                                                ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white'
                                                : 'text-gray-700 hover:bg-gray-100'
                                                }`}
                                        >
                                            <item.icon />
                                            <span className="font-medium">{t(item.label)}</span>
                                        </Link>
                                    ))}
                                </nav>

                                <div className="mt-8 space-y-3">
                                    <button
                                        onClick={() => {
                                            setLanguage(language === 'en' ? 'te' : 'en');
                                            setSidebarOpen(false);
                                        }}
                                        className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl font-medium"
                                    >
                                        {language === 'en' ? 'తెలుగు' : 'English'}
                                    </button>
                                    <button
                                        onClick={handleLogout}
                                        className="w-full py-3 bg-red-500 text-white rounded-2xl font-medium"
                                    >
                                        {t('logout')}
                                    </button>
                                </div>
                            </motion.div>
                        </>
                    )}
                </AnimatePresence>

                {/* Main Content */}
                <main className="flex-1 overflow-auto p-4 md:p-8">
                    <Outlet />
                </main>
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

export default Layout;
