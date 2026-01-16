import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

export default function Dashboard() {
  return (
    <main className="min-h-screen bg-black text-white p-8">
      <h1 className="text-4xl font-bold mb-8">ח.סבן - ניהול צי חכם</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* כרטיס בזבוז סרק */}
        <div className="bg-gray-900 p-6 rounded-xl border border-red-500/50">
          <h2 className="text-xl text-gray-400">אנרגיה סרק (היום)</h2>
          <p className="text-3xl font-bold text-red-500">18.4 ליטר</p>
        </div>
        
        {/* כרטיס PTO */}
        <div className="bg-gray-900 p-6 rounded-xl border border-blue-500/50">
          <h2 className="text-xl text-gray-400">שימוש ב-PTO</h2>
          <p className="text-3xl font-bold text-blue-500">12 פתיחות</p>
        </div>

        {/* כרטיס חריגות שעות */}
        <div className="bg-gray-900 p-6 rounded-xl border border-yellow-500/50">
          <h2 className="text-xl text-gray-400">חריגות שעות</h2>
          <p className="text-3xl font-bold text-yellow-500">3 נהגים</p>
        </div>
      </div>

      {/* אזור הניתוח של Gemini */}
      <div className="mt-10 bg-blue-900/20 p-6 rounded-2xl border border-blue-400">
        <h3 className="text-xl font-bold mb-4">🧠 ניתוח מוח Gemini:</h3>
        <p className="text-blue-100">טוען תובנות מהדוח האחרון...</p>
      </div>
    </main>
  );
}
