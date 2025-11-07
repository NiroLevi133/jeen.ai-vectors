#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pipeline: קריאת DOCX/PDF → ניקוי טקסט → חלוקה בגודל קבוע עם חפיפה (fixed+overlap) → Embeddings ב-Gemini → שמירה ל-PostgreSQL.
קלט יחיד: --file  (כל ההגדרות האחרות קבועות בקוד).
"""

import os
import sys
import re
import uuid
from datetime import datetime
from typing import List, Tuple, Iterable

import pdfplumber
from docx import Document
from dotenv import load_dotenv
import google.generativeai as genai
import psycopg2
from psycopg2.extras import execute_values

# =========================
# קבועים ניתנים לשינוי במקום אחד
# =========================
CHUNK_SIZE: int = 600            # גודל מקטע
CHUNK_OVERLAP: int = 120         # חפיפה בין מקטעים
EMBEDDING_MODEL: str = "models/text-embedding-004"
TABLE_NAME: str = "embeddings"

# --- קריאת PDF: מחלץ טקסט מכל הדפים ומחזיר כמחרוזת אחת ---
def read_pdf_text(path: str) -> str:
    texts: List[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            if txt:
                texts.append(txt)
    return "\n".join(texts).strip()

# --- קריאת DOCX: מאחד את כל הפסקאות הלא-ריקות למחרוזת אחת ---
def read_docx_text(path: str) -> str:
    doc = Document(path)
    paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(paras).strip()

# --- ניקוי טקסט: החלפת NBSP, כיווץ רווחים וריווחי שורות ---
def clean_text(text: str) -> str:
    text = text.replace("\u00A0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# --- חלוקה בגודל קבוע עם חפיפה: יוצר מקטעים חופפים באורך קבוע ---
def chunk_fixed(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if size <= 0:
        raise ValueError("chunk size must be > 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and < size")
    chunks: List[str] = []
    i = 0
    while i < len(text):
        end = min(i + size, len(text))
        chunks.append(text[i:end].strip())
        if end == len(text):
            break
        i = end - overlap
    return [c for c in chunks if c]

# --- הגדרת מפתח ל-Gemini: מכין את הספרייה לקריאות embedding ---
def init_gemini(api_key: str) -> None:
    genai.configure(api_key=api_key)

# --- הפקת Embeddings: יוצר וקטור לכל מקטע טקסט ---
def embed_texts(texts: Iterable[str], model: str = EMBEDDING_MODEL) -> List[List[float]]:
    vectors: List[List[float]] = []
    for t in texts:
        resp = genai.embed_content(model=model, content=t)
        vec = resp.get("embedding") or resp.get("data", [{}])[0].get("embedding")
        if not vec:
            raise RuntimeError("Failed to get embedding from Gemini response")
        vectors.append(vec)
    return vectors

# --- יצירת טבלה במידה אין---
def ensure_table(conn) -> None:
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id UUID PRIMARY KEY,
        chunk_text TEXT NOT NULL,
        embedding DOUBLE PRECISION[] NOT NULL,
        filename TEXT NOT NULL,
        strategy_split TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(ddl)
        conn.commit()

# --- מכינה רשימת שורות מוכנות להכנסה למסד הנתונים---
def build_rows(chunks: List[str], embeddings: List[List[float]], filename: str) -> List[Tuple]:
    now = datetime.utcnow()
    rows: List[Tuple] = []
    for ch, vec in zip(chunks, embeddings):
        rows.append((str(uuid.uuid4()), ch, vec, filename, "fixed", now))
    return rows

# --- מכניסה את כל הרשומות לטבלה במסד הנתונים בפעולה אחת. ---
def insert_rows(conn, rows: List[Tuple]) -> None:
    sql = f"""
    INSERT INTO {TABLE_NAME} (id, chunk_text, embedding, filename, strategy_split, created_at)
    VALUES %s
    """
    template = "(%s, %s, %s::double precision[], %s, %s, %s)"
    with conn.cursor() as cur:
        execute_values(cur, sql, rows, template=template)
    conn.commit()

# --- קריאת קובץ לפי סיומת: DOCX/PDF בלבד ---
def read_file_text(file_path: str) -> str:
    ext = os.path.splitext(file_path.lower())[1]
    if ext == ".pdf":
        return read_pdf_text(file_path)
    if ext == ".docx":
        return read_docx_text(file_path)
    raise ValueError("Only .pdf or .docx are supported")

# --- מריצה מקצה-לקצה: קוראת את הקובץ, מחלקת למקטעים, מפיקה Embeddings ושומרת הכל ל-PostgreSQL. ---
def main() -> None:
    if "--file" not in sys.argv or len(sys.argv) < 3:
        print("Usage: python index_documents_fixed.py --file <path_to_pdf_or_docx>")
        sys.exit(1)

    file_path = sys.argv[sys.argv.index("--file") + 1]
    if not os.path.exists(file_path):
        print(f"ERROR: file not found: {file_path}")
        sys.exit(1)

    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    pg_url = os.getenv("POSTGRES_URL")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY missing in .env")
        sys.exit(1)
    if not pg_url:
        print("ERROR: POSTGRES_URL missing in .env")
        sys.exit(1)

    try:
        raw = read_file_text(file_path)
    except Exception as e:
        print(f"ERROR: failed reading file: {e}")
        sys.exit(1)

    text = clean_text(raw)
    if not text:
        print("ERROR: empty text after cleaning")
        sys.exit(1)

    chunks = chunk_fixed(text, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"[INFO] created {len(chunks)} chunks (fixed, size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}).")

    try:
        init_gemini(gemini_key)
        vectors = embed_texts(chunks, model=EMBEDDING_MODEL)
    except Exception as e:
        print(f"ERROR: embedding failed: {e}")
        sys.exit(1)

    rows = build_rows(chunks, vectors, os.path.basename(file_path))

    try:
        conn = psycopg2.connect(pg_url)
    except Exception as e:
        print("\n[ERROR] לא ניתן להתחבר ל-PostgreSQL.")
        print("בדקו את POSTGRES_URL ב-.env (למשל: postgresql://postgres:YOUR_PASSWORD@localhost:5432/postgres)")
        print(f"Details: {e}\n")
        sys.exit(1)

    try:
        ensure_table(conn)
        insert_rows(conn, rows)
    finally:
        conn.close()

    print(f"[OK] saved {len(rows)} embeddings into table '{TABLE_NAME}'.")

if __name__ == "__main__":
    main()
