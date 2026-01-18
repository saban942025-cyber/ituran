'use client';
import { useState } from 'react';

export default function AnalysisPage() {
  // כאן נמשוך את הנתונים מה-API שבנינו למעלה
  return (
    <div className="max-w-md mx-auto p-4 bg-gray-900 min-h-screen rtl" dir="rtl">
      <div className="bg-white rounded-[40px] p-6 shadow-2xl border-[6px] border-gray-800">
        <div className="w-20 h-1.5 bg-gray-800 mx-auto rounded-full mb-6"></div>
        <h1 className="text-2xl font-black text-center mb-6">מרכז בקרה - ח.סבן</h1>
        
        {/* דוגמה לכרטיס חריגה */}
        <div className="bg-red-50 border-r-8 border-red-500 p-4 rounded-2xl mb-4">
          <div className="flex justify-between font-bold">
            <span>חכמת (שארק 087)</span>
            <span className="text-red-600">⛔ חריגה</span>
          </div>
          <p className="text-sm text-gray-600">רחוב הפסנתר 1, הוד השרון</p>
          <div className="mt-2 text-xs font-bold text-red-700">
            ⚠️ פער של 40 דק' בין דיוח לאיתורן!
          </div>
        </div>

        <div className="mt-10 p-4 bg-blue-600 rounded-2xl text-white text-center">
          <p className="text-sm opacity-80">חיסכון יומי מזוהה:</p>
          <p className="text-3xl font-black">₪ 450</p>
        </div>
      </div>
    </div>
  );
}
