import pandas as pd
import json
import glob
import os

def analyze():
    # מוצא את קובץ ה-CSV שהעלית (האחרון שהתעדכן)
    files = glob.glob("*.csv")
    if not files: return
    
    df = pd.read_csv(files[0], skiprows=6)
    df.columns = ['time', 'tag', 'dir', 'dist', 'odo', 'driver', 'addr', 'speed', 'status', 'alert', 'orig_geo', 'curr_geo']
    df = df[df['time'] != 'זמן הודעה'].dropna(subset=['time', 'tag'])
    df['time'] = pd.to_datetime(df['time'], format='%d/%m/%Y %H:%M:%S')
    df = df.sort_values(['tag', 'time'])

    analysis = {}
    for tag, group in df.groupby('tag'):
        events = []
        # זיהוי אירועי PTO (מנוף) וסרק לפי עמודת הסטטוס
        for i, row in group.iterrows():
            st = str(row['status'])
            if '.פתיחת PTO' in st or '.סגירת PTO' in st or '.עומד מונע' in st or '.רכב בתנועה' in st:
                events.append({
                    "time": row['time'].isoformat(),
                    "status": st,
                    "addr": str(row['addr'])
                })
        analysis[tag] = events

    with open('fleet_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    analyze()
