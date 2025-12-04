import sqlite3

DB_FILE = "mno-data.db"


# ---------- DB 유틸 ----------

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 요금제 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        monthly_fee INTEGER NOT NULL,
        data_gb REAL NOT NULL,
        voice_minutes INTEGER NOT NULL,
        sms_count INTEGER NOT NULL,
        is_unlimited_data BOOLEAN NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # 요금제 혜택 테이블
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plan_benefits (
        benefit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER NOT NULL,
        benefit_name TEXT NOT NULL,
        benefit_desc TEXT,
        priority INTEGER,
        FOREIGN KEY (plan_id) REFERENCES plans (plan_id)
    );
    """)

    conn.commit()
    conn.close()


# ---------- 요금제 및 요금제 혜택 등록 ----------

def create_plan(name, monthly_fee, data_gb, voice_minutes, sms_count, is_unlimited_data=False):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO plans (name, monthly_fee, data_gb, voice_minutes, sms_count, is_unlimited_data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, monthly_fee, data_gb, voice_minutes, sms_count, int(is_unlimited_data)))

    conn.commit()
    plan_id = cur.lastrowid
    conn.close()
    return plan_id


def create_plan_benefit(plan_id, benefit_name, benefit_desc=None, priority=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO plan_benefits (plan_id, benefit_name, benefit_desc, priority)
        VALUES (?, ?, ?, ?)
    """, (plan_id, benefit_name, benefit_desc, priority))

    conn.commit()
    benefit_id = cur.lastrowid
    conn.close()
    return benefit_id


# ---------- 요금제 조회 (단건/전체/조인) ----------

def get_plan(plan_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM plans WHERE plan_id = ?", (plan_id,))
    row = cur.fetchone()

    conn.close()
    return row


def get_all_plans():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM plans ORDER BY plan_id")
    rows = cur.fetchall()

    conn.close()
    return rows


def get_plan_with_benefits(plan_id):
    """요금제 + 해당 요금제의 혜택 목록을 함께 조회"""
    conn = get_connection()
    cur = conn.cursor()

    # 요금제 기본정보
    cur.execute("SELECT * FROM plans WHERE plan_id = ?", (plan_id,))
    plan = cur.fetchone()

    # 혜택 목록
    cur.execute("""
        SELECT benefit_id, benefit_name, benefit_desc, priority
        FROM plan_benefits
        WHERE plan_id = ?
        ORDER BY COALESCE(priority, 9999)
    """, (plan_id,))
    benefits = cur.fetchall()

    conn.close()
    return plan, benefits


# ---------- 요금제 정보 수정 ----------

def update_plan_fee(plan_id, new_monthly_fee):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE plans
        SET monthly_fee = ?
        WHERE plan_id = ?
    """, (new_monthly_fee, plan_id))

    conn.commit()
    changed = cur.rowcount  # 변경된 row 수
    conn.close()
    return changed > 0


# ---------- 요금제 정보 삭제 - FK 순서 주의 ----------

def delete_plan(plan_id):
    """요금제 삭제 전에 해당 요금제의 혜택도 같이 삭제(ON DELETE CASCADE가 없다면 직접 삭제)"""
    conn = get_connection()
    cur = conn.cursor()

    # 1) 혜택 먼저 삭제
    cur.execute("DELETE FROM plan_benefits WHERE plan_id = ?", (plan_id,))
    # 2) 요금제 삭제
    cur.execute("DELETE FROM plans WHERE plan_id = ?", (plan_id,))

    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0


def delete_plan_benefit(benefit_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM plan_benefits WHERE benefit_id = ?", (benefit_id,))

    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0
