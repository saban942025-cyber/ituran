import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { parseIturanData } from '@/lib/ituran-parser';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json({ error: 'לא נמצא קובץ' }, { status: 400 });
    }

    // קריאת תוכן הקובץ
    const text = await file.text();
    // כאן נשתמש ב-Parser שבנית ב-lib/ituran-parser.ts
    // הערה: יש להתאים את ה-Parser לקריאת CSV/Excel גולמי
    const rawData = JSON.parse(text); 
    const analyzedData = parseIturanData(rawData);

    // שמירה לטבלת fleet_events ב-Supabase
    const { error } = await supabase
      .from('fleet_events')
      .insert(analyzedData.map(d => ({
        driver_name: d.driver,
        event_type: d.status,
        event_timestamp: d.time,
        location: d.location
      })));

    if (error) throw error;

    return NextResponse.json({ message: 'הנתונים עובדו ונשמרו בהצלחה' });
  } catch (err) {
    return NextResponse.json({ error: 'שגיאה בעיבוד הנתונים' }, { status: 500 });
  }
}
