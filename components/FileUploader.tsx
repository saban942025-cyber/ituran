'use client';
import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';

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
        window.location.reload(); // רענון הנתונים ב-Dashboard
      } else {
        setStatus('error');
      }
    } catch (err) {
      setStatus('error');
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto p-8 border-2 border-dashed border-slate-700 rounded-2xl bg-slate-800/50 hover:border-blue-500 transition-all text-center">
      <input type="file" id="ituran-file" className="hidden" onChange={handleUpload} accept=".csv,.xlsx" />
      <label htmlFor="ituran-file" className="cursor-pointer flex flex-col items-center">
        {status === 'idle' && (
          <>
            <Upload size={48} className="text-blue-400 mb-4" />
            <h3 className="text-xl font-semibold">לחץ או גרור דוח איתורן</h3>
          </>
        )}
        {status === 'loading' && <p className="text-blue-400 animate-pulse text-lg">מעבד נתונים... המתן</p>}
        {status === 'success' && (
          <>
            <CheckCircle size={48} className="text-green-500 mb-4" />
            <p className="text-green-400 font-bold">הדוח הועלה בהצלחה!</p>
          </>
        )}
        {status === 'error' && (
          <>
            <AlertCircle size={48} className="text-red-500 mb-4" />
            <p className="text-red-400">שגיאה בהעלאה, נסה שוב</p>
          </>
        )}
      </label>
    </div>
  );
}
