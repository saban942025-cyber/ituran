export async function getAiInsight(fleetSummary: any) {
  const apiKey = process.env.GEMINI_API_KEY;
  const prompt = `נתח את נתוני צי הרכב הבאים עבור חברת ח.סבן. זהה נהגים שמבזבזים דלק בסרק או משתמשים ב-PTO בצורה לא יעילה: ${JSON.stringify(fleetSummary)}`;

  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }]
    })
  });

  const data = await response.json();
  return data.candidates[0].content.parts[0].text;
}
