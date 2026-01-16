export const parseIturanData = (rawData: any[]) => {
  return rawData.map(row => ({
    time: row['זמן הודעה'],
    driver: row['תג זיהוי'],
    status: row['שם מצב'], // כאן נחפש את ה-PTO
    location: row['כתובת'],
    isOffHours: checkIfOffHours(row['זמן הודעה'])
  }));
};

const checkIfOffHours = (timeStr: string) => {
  const hour = new Date(timeStr).getHours();
  return hour > 18 || hour < 6; // שעות עבודה מוגדרות 06:00-18:00
};
