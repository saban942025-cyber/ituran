'use client';
import FileUploader from '@/components/FileUploader';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase'; // שימוש בחיבור שהגדרנו

export default function Dashboard() {
  const [stats, setStats] = useState({ idle: 0, pto: 0, offHours: 0 });

  return (
    <main className="min-h-screen bg-slate-950 text-white p-8 font-sans" dir="rtl">
      {/* כותרת מותג */}
      <header className="mb-12 text-center md:text-right">
        <h1 className="text-5xl font-black tracking-tighter text-blue-500">
          ח.סבן 1994 - <span className="text-white">FLEET AI</span>
        </h1>
        <p className="text-slate-400 text-lg mt-2 font-light">ניתוח יעילות וניצול אנרגיה בזמן אמת</p>
      </header>

      {/* העלאת קובץ דינמית */}
      <section className="mb-16">
        <FileUploader />
      </section>

      {/* לוח מדדים ויזואלי */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <div className="bg-slate-900 border border-red-500/20 p-8 rounded-3xl shadow-xl shadow-red-500/5">
          <h3 className="text-slate-400 text-sm font-bold uppercase mb-2">אנרגיה סרק (ליטרים)</h3>
          <p className="text-5xl font-black text-red-500">18.4</p>
          <div className="mt-4 h-1 bg-red-950 rounded-full overflow-hidden">
             <div className="w-3/4 h-full bg-red-500"></div>
          </div>
        </div>

        <div className="bg-slate-900 border border-blue-500/20 p-8 rounded-3xl shadow-xl shadow-blue-500/5">
          <h3 className="text-slate-400 text-sm font-bold uppercase mb-2">פתיחות PTO/מנוף</h3>
          <p className="text-5xl font-black text-blue-500">12</p>
          <div className="mt-4 h-1 bg-blue-950 rounded-full overflow-hidden">
             <div className="w-1/2 h-full bg-blue-500"></div>
          </div>
        </div>

        <div className="bg-slate-900 border border-yellow-500/20 p-8 rounded-3xl shadow-xl shadow-yellow-500/5">
          <h3 className="text-slate-400 text-sm font-bold uppercase mb-2">חריגות שעות עבודה</h3>
          <p className="text-5xl font-black text-yellow-500">3</p>
          <div className="mt-4 h-1 bg-yellow-950 rounded-full overflow-hidden">
             <div className="w-1/4 h-full bg-yellow-500"></div>
          </div>
        </div>
      </div>

      {/* חלונית התובנות של Gemini */}
      <div className="bg-gradient-to-l from-blue-900/40 to-slate-900 border border-blue-400/30 p-10 rounded-[2.5rem] relative overflow-hidden">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-blue-500 rounded-2xl">🧠</div>
          <h2 className="text-2xl font-bold">הניתוח של Gemini AI</h2>
        </div>
        <p className="text-blue-100/90 text-xl leading-relaxed italic">
          "המערכת זיהתה כי נהג בשם בורהאן השאיר PTO פתוח ללא תנועה בטייבה למשך 23 דקות. מומלץ לוודא יעילות מול הלקוח בכתובת זו."
        </p>
      </div>
    </main>
  );
}
