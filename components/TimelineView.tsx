'use client';
import { useEffect, useState } from 'react';

export default function TimelineView() {
  return (
    <div className="mt-8 p-6 bg-slate-800 rounded-xl border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 text-sky-300">ציר זמן פעילות</h2>
      <div className="text-center py-10 text-slate-400">
        <p>כאן יוצגו נתוני הנהגים לאחר העלאת הקובץ.</p>
        <p className="text-sm mt-2">(הנתונים נמשכים אוטומטית מ-Supabase)</p>
      </div>
    </div>
  );
}
