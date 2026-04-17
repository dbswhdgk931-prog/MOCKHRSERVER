"""
Excel → SQLite import 스크립트
사용법: python import_data.py
실행할 때마다 DB를 삭제 후 재생성 (clean re-import)
"""

import os
import sqlite3
from datetime import datetime, date, timezone

import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "hr_data.db")

# ── 헬퍼 ──────────────────────────────────────────────────────

def _cell_to_str(value) -> str:
    """셀 값을 문자열로 변환. 날짜 → ISO 8601, None → ''"""
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _cell_to_str_or_none(value):
    """None은 그대로, 나머지는 문자열 변환"""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    return str(value)


def read_excel(filename: str) -> list[dict]:
    """엑셀 파일을 읽어 list[dict] 반환 (헤더 기반)"""
    path = os.path.join(DATA_DIR, filename)
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not rows:
        return []
    headers = rows[0]
    return [dict(zip(headers, row)) for row in rows[1:]]


# ── DDL ───────────────────────────────────────────────────────

DDL = """
CREATE TABLE employee (
    employee_id   TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    birth_date    TEXT,
    department    TEXT,
    position      TEXT,
    grade         TEXT,
    tenure        INTEGER,
    promotion_date TEXT,
    photo_url     TEXT,
    manager_id    TEXT,
    last_modified TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE education (
    education_id  INTEGER PRIMARY KEY,
    employee_id   TEXT NOT NULL REFERENCES employee(employee_id),
    school        TEXT,
    degree        TEXT,
    major         TEXT,
    grad_year     INTEGER
);

CREATE TABLE career (
    career_id     INTEGER PRIMARY KEY,
    employee_id   TEXT NOT NULL REFERENCES employee(employee_id),
    company       TEXT,
    department    TEXT,
    role          TEXT,
    start_date    TEXT,
    end_date      TEXT,
    region        TEXT,
    description   TEXT
);

CREATE TABLE overseas_exp (
    overseas_id   INTEGER PRIMARY KEY,
    employee_id   TEXT NOT NULL REFERENCES employee(employee_id),
    country       TEXT,
    purpose       TEXT,
    start_date    TEXT,
    end_date      TEXT
);

CREATE TABLE family (
    family_id       INTEGER PRIMARY KEY,
    employee_id     TEXT NOT NULL REFERENCES employee(employee_id),
    relation        TEXT,
    name            TEXT,
    birth_year      INTEGER,
    final_education TEXT,
    occupation      TEXT
);

CREATE TABLE certification (
    cert_id       INTEGER PRIMARY KEY,
    employee_id   TEXT NOT NULL REFERENCES employee(employee_id),
    cert_name     TEXT,
    issuer        TEXT,
    country       TEXT,
    score_or_grade TEXT,
    issued_date   TEXT,
    expiry_date   TEXT
);

CREATE TABLE evaluation (
    eval_id          INTEGER PRIMARY KEY,
    employee_id      TEXT NOT NULL REFERENCES employee(employee_id),
    year             INTEGER NOT NULL,
    performance_grade TEXT,
    competency_grade  TEXT
);

CREATE TABLE eval_comment (
    comment_id   INTEGER PRIMARY KEY,
    employee_id  TEXT NOT NULL REFERENCES employee(employee_id),
    year         INTEGER NOT NULL,
    comment_type TEXT,
    comment_text TEXT
);

CREATE TABLE leadership_survey (
    survey_id          INTEGER PRIMARY KEY,
    employee_id        TEXT NOT NULL REFERENCES employee(employee_id),
    year               INTEGER NOT NULL,
    evaluator_type     TEXT,
    score              REAL,
    comment_strength   TEXT,
    comment_development TEXT
);

CREATE TABLE import_metadata (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

# ── Import 로직 ───────────────────────────────────────────────

def create_db():
    """DB 파일 삭제 후 재생성"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"기존 DB 삭제: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("PRAGMA foreign_keys = ON;\n" + DDL)
    conn.commit()
    print("DB 및 테이블 생성 완료")
    return conn


def import_employees(conn: sqlite3.Connection):
    rows = read_excel("01_Employee.xlsx")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for r in rows:
        conn.execute(
            "INSERT INTO employee VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                r["EmployeeId"],
                r["Name"],
                _cell_to_str(r.get("BirthDate")),
                _cell_to_str(r.get("Department")),
                _cell_to_str(r.get("Position")),
                _cell_to_str(r.get("Grade")),
                r.get("Tenure"),
                _cell_to_str(r.get("PromotionDate")),
                _cell_to_str(r.get("PhotoUrl")),
                _cell_to_str(r.get("ManagerId")),
                now,
            ),
        )
    conn.commit()
    print(f"  employee: {len(rows)} rows")


def import_education(conn: sqlite3.Connection):
    rows = read_excel("02_Education.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO education VALUES (?,?,?,?,?,?)",
            (r["EducationId"], r["EmployeeId"], r.get("School"), r.get("Degree"), r.get("Major"), r.get("GradYear")),
        )
    conn.commit()
    print(f"  education: {len(rows)} rows")


def import_career(conn: sqlite3.Connection):
    rows = read_excel("03_Career.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO career VALUES (?,?,?,?,?,?,?,?,?)",
            (
                r["CareerId"], r["EmployeeId"],
                _cell_to_str(r.get("Company")),
                _cell_to_str(r.get("Department")),
                _cell_to_str(r.get("Role")),
                _cell_to_str(r.get("StartDate")),
                _cell_to_str_or_none(r.get("EndDate")),
                _cell_to_str(r.get("Region")),
                _cell_to_str(r.get("Description")),
            ),
        )
    conn.commit()
    print(f"  career: {len(rows)} rows")


def import_overseas_exp(conn: sqlite3.Connection):
    rows = read_excel("04_OverseasExp.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO overseas_exp VALUES (?,?,?,?,?,?)",
            (
                r["OverseasId"], r["EmployeeId"],
                _cell_to_str(r.get("Country")),
                _cell_to_str(r.get("Purpose")),
                _cell_to_str(r.get("StartDate")),
                _cell_to_str(r.get("EndDate")),
            ),
        )
    conn.commit()
    print(f"  overseas_exp: {len(rows)} rows")


def import_family(conn: sqlite3.Connection):
    rows = read_excel("05_Family.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO family VALUES (?,?,?,?,?,?,?)",
            (
                r["FamilyId"], r["EmployeeId"],
                _cell_to_str(r.get("Relation")),
                _cell_to_str(r.get("Name")),
                r.get("BirthYear"),
                _cell_to_str(r.get("FinalEducation")),
                _cell_to_str(r.get("Occupation")),
            ),
        )
    conn.commit()
    print(f"  family: {len(rows)} rows")


def import_certification(conn: sqlite3.Connection):
    rows = read_excel("06_Certification.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO certification VALUES (?,?,?,?,?,?,?,?)",
            (
                r["CertId"], r["EmployeeId"],
                _cell_to_str(r.get("CertName")),
                _cell_to_str(r.get("Issuer")),
                _cell_to_str(r.get("Country")),
                _cell_to_str(r.get("ScoreOrGrade")),
                _cell_to_str(r.get("IssuedDate")),
                _cell_to_str(r.get("ExpiryDate")),
            ),
        )
    conn.commit()
    print(f"  certification: {len(rows)} rows")


def import_evaluation(conn: sqlite3.Connection):
    rows = read_excel("07_Evaluation.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO evaluation VALUES (?,?,?,?,?)",
            (r["EvalId"], r["EmployeeId"], r.get("Year"), r.get("PerformanceGrade"), r.get("CompetencyGrade")),
        )
    conn.commit()
    print(f"  evaluation: {len(rows)} rows")


def import_eval_comment(conn: sqlite3.Connection):
    rows = read_excel("08_EvalComment.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO eval_comment VALUES (?,?,?,?,?)",
            (r["CommentId"], r["EmployeeId"], r.get("Year"), r.get("CommentType"), r.get("CommentText")),
        )
    conn.commit()
    print(f"  eval_comment: {len(rows)} rows")


def import_leadership_survey(conn: sqlite3.Connection):
    rows = read_excel("09_LeadershipSurvey.xlsx")
    for r in rows:
        conn.execute(
            "INSERT INTO leadership_survey VALUES (?,?,?,?,?,?,?)",
            (
                r["SurveyId"], r["EmployeeId"], r.get("Year"),
                _cell_to_str(r.get("EvaluatorType")),
                r.get("Score"),
                _cell_to_str(r.get("CommentStrength")),
                _cell_to_str(r.get("CommentDevelopment")),
            ),
        )
    conn.commit()
    print(f"  leadership_survey: {len(rows)} rows")


def main():
    print("=" * 50)
    print("  Excel → SQLite Import")
    print("=" * 50)

    conn = create_db()

    print("\nImporting...")
    import_employees(conn)
    import_education(conn)
    import_career(conn)
    import_overseas_exp(conn)
    import_family(conn)
    import_certification(conn)
    import_evaluation(conn)
    import_eval_comment(conn)
    import_leadership_survey(conn)

    # 메타데이터 기록
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn.execute("INSERT INTO import_metadata VALUES (?, ?)", ("last_import", now))
    conn.commit()

    # 최종 확인
    print("\n--- Row Counts ---")
    for table in [
        "employee", "education", "career", "overseas_exp", "family",
        "certification", "evaluation", "eval_comment", "leadership_survey",
    ]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count}")

    conn.close()
    print(f"\nDB 저장 완료: {DB_PATH}")


if __name__ == "__main__":
    main()
