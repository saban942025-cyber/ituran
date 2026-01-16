'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function Dashboard() {
  const [stats, setStats] = useState({ idle: 0, pto: 0, exceptions: 0 });

  useEffect(() => {
    async function fetchStats() {
      // משיכת נתונים בזמן אמת מהמאגר שהקמנו
      const { data } = await supabase.from('fleet_events').select('*');
      if (data) {
        // לוגיקה פשוטה לסיכום המדדים
        const ptoCount = data.filter(e => e.event_type?.includes('PTO')).length;
        setStats(prev => ({ ...prev, pto: ptoCount }));
      }
    }
    fetchStats();
  }, []);

  return (
    <main className="min-h-screen bg-black text-white p-8" dir="rtl">
      <h1 className="text-4xl font-bold mb-8">ח.סבן - ניהול צי חכם</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 p-6 rounded-xl border border-red-500/50">
          <h2 className="text-xl text-gray-400">אנרגיה סרק (היום)</h2>
          <p className="text-3xl font-bold text-red-500">{stats.idle} ליטר</p>
        </div>
        
        <div className="bg-gray-900 p-6 rounded-xl border border-blue-500/50">
          <h2 className="text-xl text-gray-400">שימוש ב-PTO</h2>
          <p className="text-3xl font-bold text-blue-500">{stats.pto} פתיחות</p>
        </div>

        <div className="bg-gray-900 p-6 rounded-xl border border-yellow-500/50">
          <h2 className="text-xl text-gray-400">חריגות שעות</h2>
          <p className="text-3xl font-bold text-yellow-500">{stats.exceptions} אירועים</p>
        </div>
      </div>

      <div className="mt-10 bg-blue-900/20 p-6 rounded-2xl border border-blue-400">
        <h3 className="text-xl font-bold mb-4">🧠 תובנות מוח Gemini:</h3>
        <p className="text-blue-100">המערכת מזהה דפוסי עבודה... ניתוח נתונים בביצוע.</p>
      </div>
    </main>
  );
}
