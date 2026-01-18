'use client';
import { useState } from 'react';

export default function AnalysisPage() {
  return (
    <div className="max-w-md mx-auto p-4 bg-gray-900 min-h-screen rtl" dir="rtl">
      <div className="bg-white rounded-[45px] p-6 shadow-2xl border-[8px] border-gray-800 min-h-[700px]">
        <div className="w-24 h-6 bg-gray-800 mx-auto rounded-b-2xl mb-8"></div>
        <h1 className="text-2xl font-black text-center mb-6 text-gray-800">מרכז בקרה - ח.סבן</h1>
        
        {/* כרטיס חריגת זמן */}
        <div className="bg-red-50 border-r-8 border-red-500 p-4 rounded-3xl mb-5 shadow-sm">
          <div className="flex justify-between font-bold mb-1">
            <span className="text-gray-800">חכמת (שארק 087)</span>
            <span className="text-red-600">⛔ חריגה</span>
          </div>
          <p className="text-xs text-gray-500 mb-3">זאב ז'בוטינסקי 67, הוד השרון</p>
          <div className="text-sm bg-white p-2 rounded-xl border border-red-100 text-red-700 font-bold">
            ⚠️ פער של 34 דק' בין דיווח ידני לאיתורן!
          </div>
        </div>

        {/* כרטיס חוסר בחיוב */}
        <div className="bg-orange-50 border-r-8 border-orange-500 p-4 rounded-3xl mb-5 shadow-sm">
          <div className="flex justify-between font-bold mb-1">
            <span className="text-gray-800">תעודה 6710096</span>
            <span className="text-orange-600">💸 אובדן כסף</span>
          </div>
          <p className="text-xs text-gray-500 mb-3">שבתאי גני | נווה ימין</p>
          <div className="text-sm bg-white p-2 rounded-xl border border-orange-100 text-orange-700 font-bold">
            ⚠️ חוסר: 1 בלה לא חויבה (סופקו 4 שקי ענק).
          </div>
        </div>

        <div className="mt-12 p-5 bg-gradient-to-br from-blue-600 to-blue-800 rounded-3xl text-white text-center shadow-xl">
          <p className="text-sm opacity-90 mb-1">חיסכון יומי מזוהה (משוער):</p>
          <p className="text-4xl font-black">₪ 450</p>
        </div>
      </div>
    </div>
  );
}
