import { createClient } from '@supabase/supabase-js'

// הכתובת הייחודית של הפרויקט שלך ב-Supabase
const supabaseUrl = 'https://dmdqfjivkmxrudwzwnao.supabase.co'

// המפתח הציבורי - וודא שהוא מוגדר ב-Environment Variables ב-Vercel
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

export const supabase = createClient(supabaseUrl, supabaseKey)
