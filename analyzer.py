import pandas as pd
import json
import glob
import os

def analyze_report():
    # מוצא את קובץ ה-CSV האחרון שהעלית
    csv_files = glob.glob("*.csv")
    if not csv_files:
        print("❌ No CSV files found!")
        return
    
    # קריאת הקובץ (דילוג על 6 שורות כותרת של איתורן)
    df = pd.read_csv(csv_files[0], skiprows=6)
    df.columns = ['time', 'tag', 'dir', 'dist', 'odo', 'driver', 'addr', 'speed', 'status', 'alert', 'orig_geo', 'curr_geo']
    
    # ניקוי נתונים
    df = df[df['time'] != 'זמן הודעה'].dropna(subset=['time', 'tag'])
    df['time'] = pd.to_datetime(df['time'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['time']).sort_values(['tag', 'time'])

    fleet_analysis = {}
    for tag, group in df.groupby('tag'):
        events = []
        for _, row in group.iterrows():
            st = str(row['status'])
            # פילטור אירועים שמעניינים אותנו לציר הזמן
            if any(word in st for word in ['PTO', 'מונע', 'תנועה', 'עצירה', 'סוויץ']):
                events.append({
                    "start": row['time'].isoformat(),
                    "content": st.replace('.', ''), # ניקוי נקודות מהטקסט
                    "addr": str(row['addr'])
                })
        fleet_analysis[tag] = {"timeline": events}

    with open('fleet_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(fleet_analysis, f, indent=4, ensure_ascii=False)
    print(f"✅ Created fleet_detailed.json with {len(fleet_analysis)} drivers")

if __name__ == "__main__":
    analyze_report()
