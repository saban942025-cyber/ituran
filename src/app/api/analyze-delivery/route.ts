import { NextResponse } from 'next/server';
import { analyzeIturanCSV } from '@/lib/ituran-parser';
import { analyzePDFWithGemini } from '@/lib/gemini';

export async function POST(req: Request) {
  // הלוגיקה שתחבר את ה-CSV של איתורן עם ה-PDF של התעודות
  return NextResponse.json({ status: 'success' });
}
  try {
    const { csvContent, pdfBuffer } = await req.json();
    const ituranData = await analyzeIturanCSV(csvContent);
    const pdfResults = await analyzePDFWithGemini(pdfBuffer);

    // לוגיקה שמצליבה בין השניים לפי הכתובת והנהג
    const report = pdfResults.map(ticket => {
      const actualPto = ituranData.find(e => e.address.includes(ticket.address));
      return {
        ticketId: ticket.id,
        driver: ticket.driver,
        isAnomaly: actualPto ? (ticket.manualTime - actualPto.duration > 15) : true,
      };
    });

    return NextResponse.json({ report });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
