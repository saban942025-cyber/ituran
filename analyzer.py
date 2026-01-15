import pandas as pd
import json

def analyze_ituran_report(file_path):
    # קריאת הקובץ וניקוי כותרות
    df = pd.read_csv(file_path, skiprows=6)
    df.columns = ['time', 'tag', 'dir', 'dist', 'odo', 'driver', 'addr', 'speed', 'status', 'alert', 'orig_geo', 'curr_geo']
    df = df[df['time'] != 'זמן הודעה'].dropna(subset=['time', 'tag'])
    df['time'] = pd.to_datetime(df['time'], format='%d/%m/%Y %H:%M:%S')
    df = df.sort_values(['tag', 'time'])

    analysis = {}
    for tag, group in df.groupby('tag'):
        group = group.reset_index(drop=True)
        events = []
        current_event = {"engine": None, "pto": None, "idle": None, "drive": None}
        
        for i, row in group.iterrows():
            st, t, addr = str(row['status']), row['time'].isoformat(), str(row['addr'])
            
            # לוגיקה לזיהוי אירועים (מנוף, נסיעה, סרק)
            if '.פתיחת PTO' in st: current_event["pto"] = {"type": "מנוף", "start": t, "addr": addr}
            elif '.סגירת PTO' in st and current_event["pto"]:
                current_event["pto"]["end"] = t
                events.append(current_event["pto"])
                current_event["pto"] = None
                
            if '.עומד מונע' in st: current_event["idle"] = {"type": "סרק", "start": t, "addr": addr}
            elif current_event["idle"] and ('.רכב בתנועה' in st or '.מנוע כבוי' in st):
                current_event["idle"]["end"] = t
                events.append(current_event["idle"])
                current_event["idle"] = None

            if '.רכב בתנועה' in st: current_event["drive"] = {"type": "נסיעה", "start": t, "addr": addr}
            elif current_event["drive"] and ('.רכב בעצירה' in st or '.מנוע כבוי' in st):
                current_event["drive"]["end"] = t
                events.append(current_event["drive"])
                current_event["drive"] = None

        analysis[tag] = {"timeline": events}

    with open('fleet_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=4, ensure_ascii=False)

analyze_ituran_report('your_ituran_file.csv')
