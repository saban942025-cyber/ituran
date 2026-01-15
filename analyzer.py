import pandas as pd
import json
import glob

def run_analysis():
    # מחפש את קובץ האקסל שהעלית
    files = glob.glob("*.csv")
    if not files: 
        print("No CSV file found")
        return
    
    # טעינת הנתונים (דילוג על כותרות איתורן)
    df = pd.read_csv(files[0], skiprows=6)
    df.columns = ['time', 'tag', 'dir', 'dist', 'odo', 'driver', 'addr', 'speed', 'status', 'alert', 'orig_geo', 'curr_geo']
    
    # ניקוי והמרת זמנים
    df = df[df['time'] != 'זמן הודעה'].dropna(subset=['time', 'tag'])
    df['time'] = pd.to_datetime(df['time'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['time']).sort_values(['tag', 'time'])

    result = {}
    for tag, group in df.groupby('tag'):
        timeline = []
        for _, row in group.iterrows():
            st = str(row['status'])
            # מחפש אירועים קריטיים: מנוף, נסיעה, סרק
            if any(word in st for word in ['PTO', 'תנועה', 'מונע']):
                timeline.append({
                    "start": row['time'].isoformat(),
                    "content": st.replace('.', ''),
                    "addr": str(row['addr'])
                })
        result[tag] = {"timeline": timeline}

    # יצירת הקובץ שחסר לך (fleet_detailed.json)
    with open('fleet_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print("✅ Created fleet_detailed.json")

if __name__ == "__main__":
    run_analysis()
