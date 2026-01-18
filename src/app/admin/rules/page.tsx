'use client';
import { useState, useEffect } from 'react';
import { db } from '@/firebase'; 
import { collection, addDoc, getDocs, deleteDoc, doc } from 'firebase/firestore';

export default function RulesPage() {
  const [rules, setRules] = useState([]);
  const [newRule, setNewRule] = useState({ item: '', required: '', ratio: 1 });

  const fetchRules = async () => {
    const querySnapshot = await getDocs(collection(db, "business_rules"));
    setRules(querySnapshot.docs.map(d => ({ id: d.id, ...d.data() })));
  };

  useEffect(() => { fetchRules(); }, []);

  const handleAdd = async () => {
    if (!newRule.item || !newRule.required) return;
    await addDoc(collection(db, "business_rules"), newRule);
    setNewRule({ item: '', required: '', ratio: 1 });
    fetchRules();
  };

  return (
    <div className="max-w-md mx-auto p-4 bg-gray-50 min-h-screen rtl" dir="rtl">
      <div className="bg-white rounded-[30px] shadow-xl p-6 border-t-8 border-blue-600">
        <h1 className="text-xl font-bold text-blue-900 mb-4">🧠 הגדרות המוח - ח.סבן</h1>
        <div className="space-y-3 mb-6">
          <input className="w-full p-3 rounded-xl border" placeholder="שם פריט (למשל: טיט שק גדול)" 
                 value={newRule.item} onChange={e => setNewRule({...newRule, item: e.target.value})} />
          <input className="w-full p-3 rounded-xl border" placeholder="חיוב חובה (למשל: פיקדון בלה)" 
                 value={newRule.required} onChange={e => setNewRule({...newRule, required: e.target.value})} />
          <button onClick={handleAdd} className="w-full bg-blue-600 text-white p-3 rounded-xl font-bold">שמור חוק</button>
        </div>
        <div className="space-y-2">
          {rules.map(rule => (
            <div key={rule.id} className="flex justify-between p-3 bg-gray-50 rounded-lg border">
              <span>{rule.item} ⬅️ {rule.required}</span>
              <button onClick={async () => { await deleteDoc(doc(db, "business_rules", rule.id)); fetchRules(); }} className="text-red-500 text-xs">מחק</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
