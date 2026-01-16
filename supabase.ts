-- 1. טבלת נהגים (הזיכרון המצטבר)
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_name TEXT UNIQUE NOT NULL,
    total_km FLOAT DEFAULT 0,
    idle_minutes FLOAT DEFAULT 0,
    pto_events_count INTEGER DEFAULT 0,
    last_seen TIMESTAMP WITH TIME ZONE
);

-- 2. טבלת אירועים (לניתוח PTO ושעות חריגות)
CREATE TABLE fleet_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_name TEXT NOT NULL,
    event_type TEXT, -- 'PTO_OPEN', 'PTO_CLOSE', 'IDLE', 'OFF_HOURS'
    event_timestamp TIMESTAMP WITH TIME ZONE,
    location TEXT,
    speed TEXT,
    raw_data JSONB -- שומר את כל השורה לגיבוי
);

-- 3. טבלת סיכומי דוחות (עבור ראמי)
CREATE TABLE daily_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_date DATE DEFAULT CURRENT_DATE,
    total_vehicles INTEGER,
    total_fuel_waste_est FLOAT,
    ai_insight TEXT -- כאן נשמור את מה שג'ימיני אמר על היום הזה
);
