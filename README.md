#  index_documents.py – יצירת Embeddings ושמירה ב-PostgreSQL

הפרויקט הזה כולל סקריפט פייתון שמקבל קובץ PDF או DOCX, מחלץ ממנו טקסט, מחלק אותו למקטעים בגודל קבוע עם חפיפה, מפיק Embeddings באמצעות Google Gemini, ושומר את כל התוצאות במסד PostgreSQL.
אם הטבלה במסד לא קיימת – הסקריפט יוצר אותה אוטומטית.

##  מה המערכת עושה 
✔ קוראת קובץ PDF / DOCX  
✔ מנקה ומסדרת את הטקסט  
✔ מחלקת את הטקסט למקטעים בגודל 600 תווים עם חפיפה 120  
✔ מפיקה Embeddings לכל מקטע דרך Gemini  
✔ שומרת את הכול לטבלה `embeddings` ב-PostgreSQL


##  קבצי הפרוקיט
 `index_documents.py` | הסקריפט הראשי – קורא את הקובץ, מפיק Embeddings ושומר למסד
 
 `requirements.txt` | כל הספריות שצריך להתקין עם pip
 
 `.env` | קובץ משתנים סודיים – מפתחות Gemini ו-POSTGRES_URL *(לא נכנס לגיט)* 



##  מה צריך כדי שזה יעבוד
✔ Python מותקן  
✔ חיבור למסד PostgreSQL
✔ מפתח API של Google Gemini  
✔ קובץ `.env` תקין

---

##  התקנת הספריות
pip install -r requirements.txt

##  השלמת נתונים  בקובץ.env
הקובץ .env כבר נמצא בפרויקט - פשוט לפתוח אותו ולהוסיף את הערכים האישיים

GEMINI_API_KEY=your_gemini_key_here
POSTGRES_URL=your_postgres_connection_string

## איך מריצים את הסקריפט
python index_documents.py --file test1.docx

## פלט צפוי בהרצה תקינה
[INFO] created 12 chunks (fixed, size=600, overlap=120).
[OK] saved 12 embeddings into table 'embeddings'.

## מבנה הטבלה במסד הנתונים

| עמודה          | סוג                |
| -------------- | ------------------ |
| id             | UUID               |
| chunk_text     | TEXT               |
| embedding      | DOUBLE PRECISION[] |
| filename       | TEXT               |
| strategy_split | TEXT               |
| created_at     | TIMESTAMPTZ        |

## הדגמה


