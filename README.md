.

## פרויקט אינדוקס מסמכים חכם
מטרה: להפוך מסמכי PDF ו-DOCX לוקטורים,ולשמור אותם במסד נתונים.

## מה זה עושה בפועל?
הסקריפט מבצע אינדוקס מלא: הוא מחלץ טקסט נקי מקובצי PDF/DOCX, משתמש באסטרטגיית חלוקה של גודל קבוע וחפיפה (600 תווים ו120 חפיפה), ולאחר מכן מפעיל את Gemini API ליצירת Embeddings. לבסוף, הוא שומר את כל המקטעים יחד עם הוקטורים שלהם במסד הנתונים PostgreSQL

## שלב ראשון: הכנות
### 1. דברים שצריך לפני שמתחילים:

א. Python: מותקן (גרסה 3.8 ומעלה).

ב. PostgreSQL: מסד נתונים פעיל ונגיש.

ג. מפתח API: מפתח GEMINI_API_KEY מגוגל


## 2. התקנת החבילות
פתחו את הטרמינל והתקינו את כל מה שצריך:

pip install -r requirements.txt
## 3. קובץ הסודות (.env) 🔑
כדי לשמור על אבטחה, יש להוריד את קובץ .env הריק מהגיט ולמלא אותו בפרטי החיבור שלכם.
ודאו שהקובץ מכיל את שני המשתנים הנדרשים:

GEMINI_API_KEY="<מפתח_ה-API_של_גוגל_כאן>"

Example: postgresql://user:password@host:port/database

POSTGRES_URL= "<כתובת_החיבור_המלאה_ל-PostgreSQL_כאן>"

## שלב שני:הרצת הסקריפט.
מריצים את הסקריפט, נותנים לו את שם הקובץ (PDF או DOCX), והוא עושה את השאר


# דוגמה לקובץ PDF
python index_documents.py --file Annual_Report_2024.pdf

# דוגמה לקובץ DOCX
python index_documents.py --file Technical_Specification.docx

אם הכול עבר בהצלחה, תראו הודעת [OK] עם מספר הווקטורים שנוספו.

## מבנה טבלת הנתונים (PostgreSQL)
הסקריפט יוצר טבלה בשם embeddings ששומרת את המידע בצורה מאורגנת:
id: מזהה ייחודי לכל חתיכת טקסט.

chunk_text: הטקסט הנקי והמוכן לשימוש.

embedding: הווקטור! מערך המספרים שמייצג את המשמעות של הטקסט.

filename: שם הקובץ המקורי שממנו הגיע המידע.

strategy_split: שיטת החיתוך שבה השתמשנו- בסקריפט הזה תמיד יופיע fixed.

created_at: מתי המקטע נוסף למסד.


