'use client';
import { useState, useEffect } from 'react';
import { db } from '@/supabase'; // או firebase לפי מה שמוגדר ב-ituran/supabase.ts
import { collection, addDoc, getDocs } from 'firebase/firestore';

export default function RulesPage() {
  const [rules, setRules] = useState([]);
  const [item, setItem] = useState('');
  const [required, setRequired] = useState('');

  return (
    <div className="p-6 max-w-md mx-auto bg-white rounded-3xl shadow-lg mt-10" dir="rtl">
      <h1 className="text-xl font-bold mb-4 text-blue-600">🧠 הגדרות המוח - ח.סבן</h1>
      <div className="space-y-4">
        <input className="w-full p-2 border rounded" placeholder="מוצר (למשל: טיט שק גדול)" onChange={(e)=>setItem(e.target.value)} />
        <input className="w-full p-2 border rounded" placeholder="דרישה (למשל: בלה)" onChange={(e)=>setRequired(e.target.value)} />
        <button className="w-full bg-blue-600 text-white p-2 rounded-xl font-bold">שמור חוק</button>
      </div>
    </div>
  );
}
