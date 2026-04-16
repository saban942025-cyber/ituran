import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Truck, 
  FileSearch, 
  Settings, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  TrendingUp,
  Search
} from 'lucide-react';

// קומפוננטת כרטיס סטטיסטיקה
const StatCard = ({ title, value, icon: Icon, color }: any) => (
  <div className="bg-[#1a1c1e] p-6 rounded-2xl border border-gray-800 hover:border-blue-500/50 transition-all duration-300 shadow-xl">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-gray-400 text-sm font-medium">{title}</p>
        <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
      </div>
      <div className={`p-3 rounded-xl ${color} bg-opacity-10`}>
        <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
      </div>
    </div>
    <div className="mt-4 flex items-center text-xs text-green-400">
      <TrendingUp className="w-3 h-3 mr-1" />
      <span>12% מהשבוע שעבר</span>
    </div>
  </div>
);

export default function LogisticsDashboard() {
  return (
    <div className="min-h-screen bg-[#0f1113] text-gray-100 font-sans" dir="rtl">
      {/* Sidebar */}
      <aside className="fixed right-0 top-0 h-full w-64 bg-[#16181a] border-l border-gray-800 p-6 hidden lg:block">
        <div className="flex items-center gap-3 mb-10">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <Truck className="text-white w-6 h-6" />
          </div>
          <span className="text-xl font-bold tracking-tight">SabanOS</span>
        </div>
        
        <nav className="space-y-2">
          {[
            { name: 'דאשבורד', icon: LayoutDashboard, active: true },
            { name: 'ניהול צי', icon: Truck, active: false },
            { name: 'ניתוח מסמכים', icon: FileSearch, active: false },
            { name: 'היסטוריית סבבים', icon: Clock, active: false },
            { name: 'הגדרות מערכת', icon: Settings, active: false },
          ].map((item) => (
            <a
              key={item.name}
              href="#"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                item.active 
                ? 'bg-blue-600/10 text-blue-500 border border-blue-500/20' 
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </a>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="lg:mr-64 p-8">
        {/* Header */}
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-bold text-white">בוקר טוב, רמי</h1>
            <p className="text-gray-400 mt-1">מרכז הבקרה של ח. סבן חומרי בניין</p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative hidden md:block">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input 
                type="text" 
                placeholder="חיפוש משלוח או רכב..."
                className="bg-[#1a1c1e] border border-gray-800 rounded-full py-2 pr-10 pl-4 w-64 focus:outline-none focus:border-blue-500 transition-all text-sm"
              />
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center font-bold">
              RM
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <StatCard title="סבבים פעילים" value="14" icon={Truck} color="bg-blue-500" />
          <StatCard title="מסמכים שנותחו" value="128" icon={FileSearch} color="bg-purple-500" />
          <StatCard title="ממתינים לאישור" value="3" icon={AlertCircle} color="bg-orange-500" />
          <StatCard title="הושלמו היום" value="42" icon={CheckCircle2} color="bg-green-500" />
        </div>

        {/* Recent Activity & Map Placeholder */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Timeline View Placeholder */}
          <div className="xl:col-span-2 bg-[#16181a] rounded-2xl border border-gray-800 p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold">מעקב צי בזמן אמת</h3>
              <button className="text-sm text-blue-500 hover:underline">צפה במפה מלאה</button>
            </div>
            <div className="aspect-video bg-[#0f1113] rounded-xl border border-gray-800 flex items-center justify-center relative overflow-hidden">
               {/* כאן תבוא קומפוננטת ה-Map או ה-TimelineView שלך */}
               <div className="text-gray-600 flex flex-col items-center">
                 <Truck className="w-12 h-12 mb-2 opacity-20" />
                 <p>תצוגת ציר זמן ומיקומי משאיות</p>
               </div>
               {/* דוגמה לאנימציית 'נקודה חיה' */}
               <div className="absolute top-1/4 left-1/3 w-3 h-3 bg-blue-500 rounded-full animate-pulse shadow-[0_0_15px_rgba(59,130,246,0.5)]"></div>
            </div>
          </div>

          {/* Analysis Rules */}
          <div className="bg-[#16181a] rounded-2xl border border-gray-800 p-6">
            <h3 className="text-xl font-semibold mb-6">ניתוח AI אחרון</h3>
            <div className="space-y-4">
              {[
                { id: '6710529', status: 'תקין', time: 'לפני 5 דק', info: 'אושר ע"י PTO' },
                { id: '6710530', status: 'אזהרה', time: 'לפני 12 דק', info: 'חריגה בזמן פריקה' },
                { id: '6710531', status: 'תקין', time: 'לפני 20 דק', info: 'חתימה דיגיטלית זוהתה' },
              ].map((item) => (
                <div key={item.id} className="p-4 bg-[#1a1c1e] rounded-xl border border-gray-800 flex justify-between items-center">
                  <div>
                    <p className="font-bold text-sm">תעודה #{item.id}</p>
                    <p className="text-xs text-gray-500">{item.time} • {item.info}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                    item.status === 'תקין' ? 'bg-green-500/10 text-green-500' : 'bg-orange-500/10 text-orange-500'
                  }`}>
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
            <button className="w-full mt-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-xl text-sm font-medium transition-colors">
              לכל הניתוחים
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
