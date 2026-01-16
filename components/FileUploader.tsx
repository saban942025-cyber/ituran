'use client';
import React, { useState } from 'react';

export default function FileUploader() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error', msg: string } | null>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setStatus(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', { method: 'POST', body: formData });
      const result = await response.json();

      if (response.ok) {
        setStatus({ type: 'success', msg: `הקובץ עובד! ${result.count} שורות עודכנו.` });
      } else {
        throw new Error(result.error || 'שגיאה בעיבוד');
      }
    } catch (err: any) {
      setStatus({ type: 'error', msg: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-10 border-2 border-dashed border-sky-500/30 rounded-2xl bg-slate-800/50 backdrop-blur-sm text-center">
      <div className="mb-4">
        <svg className="mx-auto h-12 w-12 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>
      <h3 className="text-2xl font-bold mb-2 text-white">ייבוא נתונים מאיתורן</h3>
      <p className="text-slate-400 mb-6">גרור לכאן את קובץ האקסל או לחץ על הכפתור</p>
      
      <input type="file" id="ituran-file" className="hidden" onChange={handleUpload} accept=".xlsx, .xls" />
      
      <label htmlFor="ituran-file" className={`cursor-pointer inline-flex items-center px-8 py-3 rounded-full font-bold text-white transition-all transform hover:scale-105 ${
          loading ? 'bg-slate-600 animate-pulse' : 'bg-gradient-to-r from-sky-600 to-blue-700 shadow-lg shadow-sky-900/20'
        }`}>
        {loading ? 'מנתח נתונים...' : 'בחירת קובץ Excel'}
      </label>

      {status && (
        <div className={`mt-6 p-4 rounded-xl text-sm font-medium ${
          status.type === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
        }`}>
          {status.msg}
        </div>
      )}
    </div>
  );
}
