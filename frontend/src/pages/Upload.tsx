import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { Upload as UploadIcon, CheckCircle, FileText, Camera, Image as ImageIcon } from 'lucide-react';
import { motion } from 'framer-motion';

const UploadPage = () => {
    const { t } = useLanguage();
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [billType, setBillType] = useState<'electricity' | 'water'>('electricity');
    const [loading, setLoading] = useState(false);
    const [uploadComplete, setUploadComplete] = useState(false);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selected = e.target.files[0];
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setUploadComplete(false);
            setErrorMsg(null); // Clear previous errors
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setErrorMsg(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('bill_type', billType);

            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:8001/api/v1/bills/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                setUploadComplete(true);
                // Success toast or minimal feedback could go here if needed
            } else {
                const errData = await response.text();
                let message = `Upload failed: ${response.statusText}`;
                try {
                    // Try to parse JSON error from backend if possible
                    const jsonErr = JSON.parse(errData);
                    if (jsonErr.detail) message = jsonErr.detail;
                } catch {
                    // Fallback to substring if not JSON
                    message = errData.substring(0, 150);
                }
                setErrorMsg(message);
            }
        } catch (error: any) {
            console.error("Error uploading file:", error);
            setErrorMsg(`Network Error: ${error.message || "Unknown error"}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center"
            >
                <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent mb-2">
                    {t('upload')}
                </h1>
                <p className="text-gray-600">Upload your utility bill for instant OCR analysis</p>
            </motion.div>

            {/* Bill Type Selector */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="flex justify-center gap-4"
            >
                <button
                    onClick={() => setBillType('electricity')}
                    className={`px-8 py-3 rounded-2xl font-semibold transition-all ${billType === 'electricity'
                            ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg scale-105'
                            : 'bg-white/70 text-gray-600 hover:bg-white border border-gray-200'
                        }`}
                >
                    ⚡ Electricity Bill
                </button>
                <button
                    onClick={() => setBillType('water')}
                    className={`px-8 py-3 rounded-2xl font-semibold transition-all ${billType === 'water'
                            ? 'bg-gradient-to-r from-blue-500 to-cyan-600 text-white shadow-lg scale-105'
                            : 'bg-white/70 text-gray-600 hover:bg-white border border-gray-200'
                        }`}
                >
                    💧 Water Bill
                </button>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="bg-white/70 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-white/50"
            >
                <label className="relative block">
                    <div className={`flex flex-col items-center justify-center w-full h-80 border-2 border-dashed rounded-2xl cursor-pointer transition-all ${preview ? 'border-emerald-400 bg-emerald-50/50' : 'border-gray-300 hover:border-emerald-400 hover:bg-emerald-50/30'
                        }`}>
                        {preview ? (
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="relative w-full h-full p-4"
                            >
                                <img src={preview} alt="Bill Preview" className="w-full h-full object-contain rounded-xl" />
                                <div className="absolute top-6 right-6 bg-green-500 text-white p-2 rounded-full shadow-lg">
                                    <CheckCircle className="w-6 h-6" />
                                </div>
                            </motion.div>
                        ) : (
                            <div className="flex flex-col items-center justify-center space-y-4">
                                <div className="relative">
                                    <div className="w-24 h-24 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl flex items-center justify-center shadow-xl">
                                        <UploadIcon className="w-12 h-12 text-white" />
                                    </div>
                                    <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg">
                                        <Camera className="w-6 h-6 text-white" />
                                    </div>
                                </div>
                                <div className="text-center">
                                    <p className="text-lg font-semibold text-gray-700">{t('upload_instruction')}</p>
                                    <p className="text-sm text-gray-500 mt-2">Click to browse or drag and drop</p>
                                    <p className="text-xs text-gray-400 mt-1">PNG, JPG, PDF (MAX. 10MB)</p>
                                </div>
                            </div>
                        )}
                    </div>
                    <input type="file" className="hidden" accept="image/*,.pdf" onChange={handleFileChange} />
                </label>

                {file && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-6 space-y-4"
                    >
                        {errorMsg && (
                            <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-start space-x-3 text-red-700">
                                <div className="mt-0.5">⚠️</div>
                                <div className="text-sm font-medium">{errorMsg}</div>
                            </div>
                        )}

                        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-2xl border border-emerald-200">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-white rounded-xl shadow">
                                    <FileText className="w-6 h-6 text-emerald-600" />
                                </div>
                                <div>
                                    <p className="font-medium text-gray-800 truncate max-w-xs">{file.name}</p>
                                    <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(2)} KB</p>
                                </div>
                            </div>
                            {uploadComplete && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    className="flex items-center space-x-2 text-green-600"
                                >
                                    <CheckCircle className="w-6 h-6" />
                                    <span className="font-medium">Processed</span>
                                </motion.div>
                            )}
                        </div>

                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={handleUpload}
                            disabled={loading || uploadComplete}
                            className={`w-full py-4 rounded-2xl font-bold text-white text-lg shadow-xl transition-all ${loading || uploadComplete
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-2xl hover:shadow-emerald-500/50'
                                }`}
                        >
                            {loading ? (
                                <div className="flex items-center justify-center space-x-2">
                                    <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                                    <span>Processing OCR...</span>
                                </div>
                            ) : uploadComplete ? (
                                'Upload Complete ✓'
                            ) : (
                                t('submit')
                            )}
                        </motion.button>
                    </motion.div>
                )}
            </motion.div>

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                    { icon: Camera, title: 'Take Photo', desc: 'Capture bill directly' },
                    { icon: UploadIcon, title: 'Upload File', desc: 'From your device' },
                    { icon: CheckCircle, title: 'Auto Extract', desc: 'AI-powered OCR' }
                ].map((item, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 + i * 0.1 }}
                        className="bg-white/60 backdrop-blur-sm p-6 rounded-2xl border border-white/50 text-center"
                    >
                        <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center mx-auto mb-3 shadow-lg">
                            <item.icon className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-bold text-gray-800">{item.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">{item.desc}</p>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default UploadPage;
