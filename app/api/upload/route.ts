import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';
import { parseIturanData } from '@/lib/ituran-parser';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const text = await file.text();
    
    // עיבוד הקובץ באמצעות ה-Parser הייעודי לאיתורן
    const rawData = JSON.parse(text); 
    const analyzed = parseIturanData(rawData);

    // שמירה היסטורית למאגר הנתונים ב-Supabase
    const { error } = await supabase.from('fleet_events').insert(
      analyzed.map(ev => ({
        driver_name: ev.driver,
        event_type: ev.status,
        event_timestamp: ev.time,
        location: ev.location
      }))
    );

    if (error) throw error;
    return NextResponse.json({ success: true });
  } catch (err) {
    return NextResponse.json({ error: 'Failed to process fleet report' }, { status: 500 });
  }
}
