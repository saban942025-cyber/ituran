'use client';
import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export default function FileUploader() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setStatus('loading');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        setStatus('success');
        setTimeout(() => setStatus('idle'), 3000); // איפוס לאחר הצלחה
      } else {
        setStatus('error');
      }
    } catch (err) {
      setStatus('error');
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-10 border-2 border-dashed border-slate-700 rounded-3xl bg-slate-900/50 hover:border-blue-500 transition-all text-center">
      <input type="file" id="ituran-file" className="hidden" onChange={handleUpload} accept=".csv,.xlsx" />
      <label htmlFor="ituran-file" className="cursor-pointer flex flex-col items-center">
        {status === 'idle' && (
          <>
            <Upload size={50} className="text-blue-400 mb-4" />
            <h3 className="text-xl font-bold text-white">העלה דוח איתורן חדש</h3>
            <p className="text-slate-400 mt-2">גרור לכאן את קובץ האקסל או לחץ לבחירה</p>
          </>
        )}
        {status === 'loading' && (
          <div className="flex flex-col items-center">
            <Loader2 size={50} className="text-blue-400 animate-spin mb-4" />
            <p className="text-blue-400 font-bold">מעבד נתונים ומנתח יעילות...</p>
          </div>
        )}
        {status === 'success' && (
          <div className="flex flex-col items-center">
            <CheckCircle size={50} className="text-green-500 mb-4" />
            <p className="text-green-400 font-bold">הדוח עובד בהצלחה! הנתונים עודכנו.</p>
          </div>
        )}
        {status === 'error' && (
          <div className="flex flex-col items-center">
            <AlertCircle size={50} className="text-red-500 mb-4" />
            <p className="text-red-400 font-bold">שגיאה בעיבוד הקובץ. וודא שזהו פורמט איתורן תקין.</p>
          </div>
        )}
      </label>
    </div>
  );
}
