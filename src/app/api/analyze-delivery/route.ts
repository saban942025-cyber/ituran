import { NextResponse } from 'next/server';
import { analyzeIturanCSV } from '@/lib/ituran-parser';
import { analyzePDFWithGemini } from '@/lib/gemini';

export async function POST(req: Request) {
  try {
    const { csvContent, pdfBuffer } = await req.json();
    const ituranData = await analyzeIturanCSV(csvContent);
    const pdfResults = await analyzePDFWithGemini(pdfBuffer);

    const report = pdfResults.map(ticket => {
      const actualPto = ituranData.find(e => e.address.includes(ticket.address));
      const gearError = (ticket.items.includes('שק גדול') && ticket.gear_quantity < ticket.item_quantity);
      
      return {
        ticketId: ticket.id,
        driver: ticket.driver,
        isAnomaly: actualPto ? (ticket.manualTime - actualPto.duration > 15) : true,
        missingGear: gearError ? 'חסר פיקדון בלה' : null
      };
    });

    return NextResponse.json({ report });
  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
