# 📌 index_documents_fixed – הפקת Embeddings ושמירה ב-PostgreSQL

הפרויקט מכיל סקריפט פייתון שמקבל קובץ PDF או DOCX, מחלק אותו למקטעים בגודל קבוע עם חפיפה, מפיק Embeddings בעזרת Google Gemini, ושומר את התוצאות במסד נתונים PostgreSQL.

---

## ✅ מה המערכת עושה?
1. קוראת קובץ PDF / DOCX  
2. מחלצת ומנקה את הטקסט  
3. מחלקת למקטעים בגודל קבוע (600 תווים) עם חפיפה (120 תווים)  
4. מפיקה Embeddings לכל מקטע באמצעות Gemini  
5. שומרת למסד PostgreSQL בטבלה `embeddings`  
6. אם הטבלה לא קיימת – נוצרת אוטומטית

---

## ✅ התקנה
התקנת כל הספריות:
```bash
pip install -r requirements.txt


יש ליצור קובץ בשם .env בתיקיית הפרויקט עם הערכים הבאים:
GEMINI_API_KEY=your_gemini_key_here
POSTGRES_URL=your_postgres_connection_string

דוגמה להרצת הסקריפט על קובץ DOCX או PDF:
python index_documents_fixed.py --file test1.docx

מבנה טבלה שנשמר במסד (נוצר אוטומטית)
עמודה	סוג
id	UUID
chunk_text	TEXT
embedding	DOUBLE PRECISION[]
filename	TEXT
strategy_split	TEXT
created_at	TIMESTAMPTZ

