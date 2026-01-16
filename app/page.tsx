'use client';
import FileUploader from '@/components/FileUploader';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function Dashboard() {
  const [stats, setStats] = useState({ idle: 0, pto: 0, exceptions: 0 });

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8" dir="rtl">
      <header className="mb-12">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-l from-blue-400 to-white">
          ח.סבן 1994 - Fleet Intelligence
        </h1>
        <p className="text-slate-400 mt-2">מערכת ניתוח וניהול יעילות נהגים מבוססת AI</p>
      </header>

      {/* אזור העלאת קבצים */}
      <section className="mb-12">
        <FileUploader />
      </section>

      {/* כרטיסי מדדים */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-slate-900 p-8 rounded-2xl border border-red-500/20 shadow-2xl shadow-red-500/5">
          <h2 className="text-sm uppercase tracking-wider text-slate-400 mb-2">אנרגיה סרק (ליטרים)</h2>
          <p className="text-4xl font-black text-red-500">18.4</p>
        </div>
        
        <div className="bg-slate-900 p-8 rounded-2xl border border-blue-500/20 shadow-2xl shadow-blue-500/5">
          <h2 className="text-sm uppercase tracking-wider text-slate-400 mb-2">אירועי PTO</h2>
          <p className="text-4xl font-black text-blue-500">12</p>
        </div>

        <div className="bg-slate-900 p-8 rounded-2xl border border-yellow-500/20 shadow-2xl shadow-yellow-500/5">
          <h2 className="text-sm uppercase tracking-wider text-slate-400 mb-2">חריגות עבודה</h2>
          <p className="text-4xl font-black text-yellow-500">3</p>
        </div>
      </div>

      {/* ניתוח ג'ימיני */}
      <div className="mt-12 bg-gradient-to-br from-blue-900/30 to-slate-900 p-8 rounded-3xl border border-blue-400/30">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-2xl">🧠</span>
          <h3 className="text-2xl font-bold">הניתוח החכם של Gemini</h3>
        </div>
        <p className="text-blue-100/80 leading-relaxed text-lg italic">
          "המערכת מזהה כי נהג בשם בורהאן השלים 4 פתיחות PTO בטייבה עם אפס תזוזה בין פתיחה לסגירה. מומלץ לוודא יעילות מול ה-CRM."
        </p>
      </div>
    </main>
  );
}
