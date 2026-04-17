"""
DB 연결 및 쿼리 함수
요청마다 새 연결을 생성하므로, import_data.py 재실행 시 서버 재시작 불필요
"""

import os
import sqlite3
from datetime import datetime

from models import (
    Employee, Education, Career, OverseasExperience, Family, Certification,
    EmployeeEvaluation, EvaluationYear, EvalComment, LeadershipSurvey,
    EducationWithEmployee, CareerWithEmployee, OverseasExpWithEmployee,
    FamilyWithEmployee, CertificationWithEmployee,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "hr_data.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def db_exists() -> bool:
    return os.path.exists(DB_PATH)


# ── Employee 관련 ─────────────────────────────────────────────

def _build_employee(row: sqlite3.Row, conn: sqlite3.Connection) -> Employee:
    eid = row["employee_id"]

    educations = [
        Education(school=r["school"], degree=r["degree"], major=r["major"], grad_year=r["grad_year"])
        for r in conn.execute("SELECT * FROM education WHERE employee_id = ?", (eid,))
    ]

    careers = [
        Career(
            company=r["company"], department=r["department"], role=r["role"],
            start_date=r["start_date"], end_date=r["end_date"],
            region=r["region"] or "", description=r["description"] or "",
            is_current=r["end_date"] is None,
        )
        for r in conn.execute("SELECT * FROM career WHERE employee_id = ?", (eid,))
    ]

    overseas = [
        OverseasExperience(
            country=r["country"], purpose=r["purpose"],
            start_date=r["start_date"], end_date=r["end_date"],
        )
        for r in conn.execute("SELECT * FROM overseas_exp WHERE employee_id = ?", (eid,))
    ]

    family = [
        Family(
            relation=r["relation"], name=r["name"], birth_year=r["birth_year"],
            education=r["final_education"] or "", occupation=r["occupation"] or "",
        )
        for r in conn.execute("SELECT * FROM family WHERE employee_id = ?", (eid,))
    ]

    certs = [
        Certification(
            cert_name=r["cert_name"], issuer=r["issuer"], country=r["country"],
            score_or_grade=r["score_or_grade"], issued_date=r["issued_date"],
            expiry_date=r["expiry_date"] or "",
        )
        for r in conn.execute("SELECT * FROM certification WHERE employee_id = ?", (eid,))
    ]

    return Employee(
        employee_id=row["employee_id"],
        name=row["name"],
        birth_date=row["birth_date"] or "",
        department=row["department"] or "",
        position=row["position"] or "",
        grade=row["grade"] or "",
        tenure=row["tenure"] or 0,
        promotion_date=row["promotion_date"] or "",
        photo_url=row["photo_url"] or "",
        manager_id=row["manager_id"] or "",
        last_modified=row["last_modified"],
        educations=educations,
        careers=careers,
        overseas_experiences=overseas,
        family=family,
        certifications=certs,
    )


def get_all_employees(modified_after: str | None = None) -> list[Employee]:
    conn = get_connection()
    try:
        if modified_after:
            rows = conn.execute(
                "SELECT * FROM employee WHERE last_modified >= ? ORDER BY employee_id",
                (modified_after,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM employee ORDER BY employee_id").fetchall()
        return [_build_employee(r, conn) for r in rows]
    finally:
        conn.close()


def get_employee_by_id(employee_id: str) -> Employee | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM employee WHERE employee_id = ?", (employee_id,)).fetchone()
        if row is None:
            return None
        return _build_employee(row, conn)
    finally:
        conn.close()


# ── 개별 하위 리소스 조회 ──────────────────────────────────────

def _edu_query(where: str = "", params: tuple = ()) -> list[EducationWithEmployee]:
    conn = get_connection()
    try:
        sql = f"SELECT * FROM education {where} ORDER BY employee_id, education_id"
        return [
            EducationWithEmployee(
                employee_id=r["employee_id"], school=r["school"],
                degree=r["degree"], major=r["major"], grad_year=r["grad_year"],
            )
            for r in conn.execute(sql, params)
        ]
    finally:
        conn.close()


def get_all_educations() -> list[EducationWithEmployee]:
    return _edu_query()


def get_educations_by_employee(employee_id: str) -> list[EducationWithEmployee]:
    return _edu_query("WHERE employee_id = ?", (employee_id,))


def _career_query(where: str = "", params: tuple = ()) -> list[CareerWithEmployee]:
    conn = get_connection()
    try:
        sql = f"SELECT * FROM career {where} ORDER BY employee_id, career_id"
        return [
            CareerWithEmployee(
                employee_id=r["employee_id"], company=r["company"],
                department=r["department"], role=r["role"],
                start_date=r["start_date"], end_date=r["end_date"],
                region=r["region"] or "", description=r["description"] or "",
                is_current=r["end_date"] is None,
            )
            for r in conn.execute(sql, params)
        ]
    finally:
        conn.close()


def get_all_careers() -> list[CareerWithEmployee]:
    return _career_query()


def get_careers_by_employee(employee_id: str) -> list[CareerWithEmployee]:
    return _career_query("WHERE employee_id = ?", (employee_id,))


def _overseas_query(where: str = "", params: tuple = ()) -> list[OverseasExpWithEmployee]:
    conn = get_connection()
    try:
        sql = f"SELECT * FROM overseas_exp {where} ORDER BY employee_id, overseas_id"
        return [
            OverseasExpWithEmployee(
                employee_id=r["employee_id"], country=r["country"],
                purpose=r["purpose"], start_date=r["start_date"], end_date=r["end_date"],
            )
            for r in conn.execute(sql, params)
        ]
    finally:
        conn.close()


def get_all_overseas() -> list[OverseasExpWithEmployee]:
    return _overseas_query()


def get_overseas_by_employee(employee_id: str) -> list[OverseasExpWithEmployee]:
    return _overseas_query("WHERE employee_id = ?", (employee_id,))


def _family_query(where: str = "", params: tuple = ()) -> list[FamilyWithEmployee]:
    conn = get_connection()
    try:
        sql = f"SELECT * FROM family {where} ORDER BY employee_id, family_id"
        return [
            FamilyWithEmployee(
                employee_id=r["employee_id"], relation=r["relation"],
                name=r["name"], birth_year=r["birth_year"],
                education=r["final_education"] or "", occupation=r["occupation"] or "",
            )
            for r in conn.execute(sql, params)
        ]
    finally:
        conn.close()


def get_all_family() -> list[FamilyWithEmployee]:
    return _family_query()


def get_family_by_employee(employee_id: str) -> list[FamilyWithEmployee]:
    return _family_query("WHERE employee_id = ?", (employee_id,))


def _cert_query(where: str = "", params: tuple = ()) -> list[CertificationWithEmployee]:
    conn = get_connection()
    try:
        sql = f"SELECT * FROM certification {where} ORDER BY employee_id, cert_id"
        return [
            CertificationWithEmployee(
                employee_id=r["employee_id"], cert_name=r["cert_name"],
                issuer=r["issuer"], country=r["country"],
                score_or_grade=r["score_or_grade"], issued_date=r["issued_date"],
                expiry_date=r["expiry_date"] or "",
            )
            for r in conn.execute(sql, params)
        ]
    finally:
        conn.close()


def get_all_certifications() -> list[CertificationWithEmployee]:
    return _cert_query()


def get_certifications_by_employee(employee_id: str) -> list[CertificationWithEmployee]:
    return _cert_query("WHERE employee_id = ?", (employee_id,))


# ── Evaluation 관련 ───────────────────────────────────────────

def _build_evaluation(employee_id: str, conn: sqlite3.Connection) -> EmployeeEvaluation | None:
    evals = conn.execute(
        "SELECT * FROM evaluation WHERE employee_id = ? ORDER BY year", (employee_id,)
    ).fetchall()
    if not evals:
        return None

    # last_modified는 해당 employee의 것을 사용
    emp_row = conn.execute(
        "SELECT last_modified FROM employee WHERE employee_id = ?", (employee_id,)
    ).fetchone()
    last_modified = emp_row["last_modified"] if emp_row else ""

    years = []
    for ev in evals:
        year = ev["year"]

        # comment (1개)
        c = conn.execute(
            "SELECT * FROM eval_comment WHERE employee_id = ? AND year = ?",
            (employee_id, year),
        ).fetchone()
        comment = None
        if c:
            comment = EvalComment(type=c["comment_type"], text=c["comment_text"])

        # leadership surveys
        surveys = [
            LeadershipSurvey(
                evaluator_type=s["evaluator_type"],
                score=s["score"],
                strength_comment=s["comment_strength"] or "",
                development_comment=s["comment_development"] or "",
            )
            for s in conn.execute(
                "SELECT * FROM leadership_survey WHERE employee_id = ? AND year = ?",
                (employee_id, year),
            )
        ]

        years.append(EvaluationYear(
            year=year,
            performance_grade=ev["performance_grade"],
            competency_grade=ev["competency_grade"],
            comment=comment,
            leadership_surveys=surveys,
        ))

    return EmployeeEvaluation(
        employee_id=employee_id,
        last_modified=last_modified,
        evaluations=years,
    )


def get_all_evaluations(modified_after: str | None = None) -> list[EmployeeEvaluation]:
    conn = get_connection()
    try:
        if modified_after:
            emp_ids = [
                r["employee_id"] for r in conn.execute(
                    "SELECT DISTINCT e.employee_id FROM evaluation e "
                    "JOIN employee emp ON e.employee_id = emp.employee_id "
                    "WHERE emp.last_modified >= ? ORDER BY e.employee_id",
                    (modified_after,),
                )
            ]
        else:
            emp_ids = [
                r["employee_id"] for r in conn.execute(
                    "SELECT DISTINCT employee_id FROM evaluation ORDER BY employee_id"
                )
            ]
        results = []
        for eid in emp_ids:
            ev = _build_evaluation(eid, conn)
            if ev:
                results.append(ev)
        return results
    finally:
        conn.close()


def get_evaluation_by_employee(employee_id: str) -> EmployeeEvaluation | None:
    conn = get_connection()
    try:
        return _build_evaluation(employee_id, conn)
    finally:
        conn.close()


# ── 통계 ──────────────────────────────────────────────────────

def get_stats() -> dict:
    conn = get_connection()
    try:
        tables = {
            "employees": "employee",
            "educations": "education",
            "careers": "career",
            "overseasExperiences": "overseas_exp",
            "family": "family",
            "certifications": "certification",
            "evaluations": "evaluation",
            "evalComments": "eval_comment",
            "leadershipSurveys": "leadership_survey",
        }
        return {
            key: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for key, table in tables.items()
        }
    finally:
        conn.close()
