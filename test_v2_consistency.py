"""
V2 Flattened API Consistency Verification Script
=================================================
Compares v1 nested API responses with v2 flattened API responses for every
employee (EMP001~EMP100) to ensure data consistency.

Usage:
    cd D:/dev/06_CopilotStudio/MockHRServer && python test_v2_consistency.py
"""

import sys
from fastapi.testclient import TestClient
from mock_hr_api import app

client = TestClient(app)

# ── Counters ─────────────────────────────────────────────────
total_employees_checked = 0
total_evals_checked = 0
total_fields_compared = 0
mismatches: list[dict] = []


def record_mismatch(emp_id: str, field: str, expected, actual):
    mismatches.append({
        "employeeId": emp_id,
        "field": field,
        "expected": expected,
        "actual": actual,
    })


def compare(emp_id: str, field: str, expected, actual):
    global total_fields_compared
    total_fields_compared += 1
    if expected != actual:
        record_mismatch(emp_id, field, expected, actual)


# ── Build expected summary strings from v1 data ─────────────

SEPARATOR = " / "


def build_education_summary(educations: list) -> str:
    if not educations:
        return ""
    parts = []
    for e in educations:
        parts.append(f"{e['school']} {e['major']} {e['degree']} ({e['gradYear']}년 졸업)")
    return SEPARATOR.join(parts)


def build_career_summary(careers: list) -> str:
    if not careers:
        return ""
    parts = []
    for c in careers:
        end = c["endDate"] if c.get("endDate") else "재직중"
        region_part = f", {c['region']}" if c.get("region") else ""
        desc_part = f" - {c['description']}" if c.get("description") else ""
        parts.append(
            f"{c['company']} {c['department']} {c['role']}{region_part} ({c['startDate']}~{end}){desc_part}"
        )
    return SEPARATOR.join(parts)


def build_overseas_summary(overseas: list) -> str:
    if not overseas:
        return ""
    parts = []
    for o in overseas:
        parts.append(f"{o['country']} {o['purpose']} ({o['startDate']}~{o['endDate']})")
    return SEPARATOR.join(parts)


def build_family_summary(family: list) -> str:
    if not family:
        return ""
    parts = []
    for f in family:
        birth = f"{f['birthYear']}년생" if f.get("birthYear") else ""
        details = ", ".join(
            d for d in [birth, f.get("education", ""), f.get("occupation", "")] if d
        )
        parts.append(f"{f['relation']} {f['name']} ({details})")
    return SEPARATOR.join(parts)


def build_certification_summary(certifications: list) -> str:
    if not certifications:
        return ""
    parts = []
    for c in certifications:
        expiry = f", 만료: {c['expiryDate']}" if c.get("expiryDate") else ""
        parts.append(
            f"{c['certName']} {c['scoreOrGrade']} (발급: {c['issuer']}/{c['country']}, 발급일: {c['issuedDate']}{expiry})"
        )
    return SEPARATOR.join(parts)


# ── Build expected evaluation fields from v1 data ────────────

def build_supervisor_review(eval_year: dict) -> str:
    comment = eval_year.get("comment")
    if comment:
        return f"{comment['text']} ({comment['commenter']})"
    return ""


def get_leadership_by_type(eval_year: dict, evaluator_type: str):
    for s in eval_year.get("leadershipSurveys", []):
        if s["evaluatorType"] == evaluator_type:
            return s
    return None


def get_leadership_score(eval_year: dict, evaluator_type: str) -> str:
    s = get_leadership_by_type(eval_year, evaluator_type)
    if s is None:
        return ""
    return str(s["score"])


def get_leadership_comment(eval_year: dict, evaluator_type: str) -> str:
    s = get_leadership_by_type(eval_year, evaluator_type)
    if s is None:
        return ""
    parts = [p for p in [s.get("strengthComment", ""), s.get("developmentComment", "")] if p]
    return " / ".join(parts) if parts else ""


# ── Main verification logic ──────────────────────────────────

def verify_employee(emp_id: str):
    global total_employees_checked

    # Fetch v1 data
    v1_resp = client.get(f"/api/v1/inhr/employees/{emp_id}")
    assert v1_resp.status_code == 200, f"v1 employee API failed for {emp_id}: {v1_resp.status_code}"
    v1_data = v1_resp.json().get("data")
    if v1_data is None:
        print(f"  [SKIP] {emp_id}: v1 returned no data (error: {v1_resp.json().get('error')})")
        return

    # Fetch v2 data
    v2_resp = client.get(f"/api/v2/inhr/employees/{emp_id}")
    assert v2_resp.status_code == 200, f"v2 employee API failed for {emp_id}: {v2_resp.status_code}"
    v2_data = v2_resp.json().get("data")
    if v2_data is None:
        record_mismatch(emp_id, "v2_employee_data", "should exist", "null/missing")
        return

    total_employees_checked += 1

    # (a) Basic fields
    basic_fields = [
        ("employeeId", "employeeId"),
        ("name", "name"),
        ("birthDate", "birthDate"),
        ("department", "department"),
        ("position", "position"),
        ("grade", "grade"),
        ("tenure", "tenure"),
        ("promotionDate", "promotionDate"),
        ("photoUrl", "photoUrl"),
        ("managerId", "managerId"),
        ("lastModified", "lastModified"),
    ]
    for v1_key, v2_key in basic_fields:
        compare(emp_id, f"basic.{v2_key}", v1_data.get(v1_key), v2_data.get(v2_key))

    # (b) educationSummary
    expected_edu = build_education_summary(v1_data.get("educations", []))
    compare(emp_id, "educationSummary", expected_edu, v2_data.get("educationSummary", ""))

    # (c) careerSummary
    expected_career = build_career_summary(v1_data.get("careers", []))
    compare(emp_id, "careerSummary", expected_career, v2_data.get("careerSummary", ""))

    # (d) overseasSummary
    expected_overseas = build_overseas_summary(v1_data.get("overseasExperiences", []))
    compare(emp_id, "overseasSummary", expected_overseas, v2_data.get("overseasSummary", ""))

    # (e) familySummary
    expected_family = build_family_summary(v1_data.get("family", []))
    compare(emp_id, "familySummary", expected_family, v2_data.get("familySummary", ""))

    # (f) certificationSummary
    expected_cert = build_certification_summary(v1_data.get("certifications", []))
    compare(emp_id, "certificationSummary", expected_cert, v2_data.get("certificationSummary", ""))


def verify_evaluation(emp_id: str):
    global total_evals_checked

    # Fetch v1 evaluation data
    v1_resp = client.get(f"/api/v1/myhr/evaluations/{emp_id}")
    assert v1_resp.status_code == 200, f"v1 eval API failed for {emp_id}: {v1_resp.status_code}"
    v1_body = v1_resp.json()
    v1_data = v1_body.get("data")

    # Fetch v2 evaluation data
    v2_resp = client.get(f"/api/v2/myhr/evaluations/{emp_id}")
    assert v2_resp.status_code == 200, f"v2 eval API failed for {emp_id}: {v2_resp.status_code}"
    v2_body = v2_resp.json()
    v2_data = v2_body.get("data")

    # Both missing → OK (no eval data for this employee)
    if v1_data is None and v2_data is None:
        return
    # One missing but not the other → mismatch
    if v1_data is None and v2_data is not None:
        record_mismatch(emp_id, "eval_existence", "v1=None", "v2=exists")
        return
    if v1_data is not None and v2_data is None:
        record_mismatch(emp_id, "eval_existence", "v1=exists", "v2=None")
        return

    total_evals_checked += 1

    # Basic eval fields
    compare(emp_id, "eval.employeeId", v1_data["employeeId"], v2_data["employeeId"])
    compare(emp_id, "eval.lastModified", v1_data["lastModified"], v2_data["lastModified"])

    # Sort v1 evaluations by year desc, take top 3
    v1_evals = sorted(v1_data.get("evaluations", []), key=lambda e: e["year"], reverse=True)
    slots = v1_evals[:3]

    # Reference years
    ref_years = v2_data.get("referenceYears", {})
    expected_N = slots[0]["year"] if len(slots) > 0 else 0
    expected_N1 = slots[1]["year"] if len(slots) > 1 else 0
    expected_N2 = slots[2]["year"] if len(slots) > 2 else 0
    compare(emp_id, "eval.referenceYears.N", expected_N, ref_years.get("N", 0))
    compare(emp_id, "eval.referenceYears.N1", expected_N1, ref_years.get("N1", 0))
    compare(emp_id, "eval.referenceYears.N2", expected_N2, ref_years.get("N2", 0))

    # For each slot (N, N1, N2), compare flattened fields
    suffixes = ["N", "N1", "N2"]
    for i, suffix in enumerate(suffixes):
        if i < len(slots):
            ev = slots[i]
            expected_perf = ev["performanceGrade"]
            expected_comp = ev["competencyGrade"]
            expected_review = build_supervisor_review(ev)
            expected_sup_score = get_leadership_score(ev, "상사")
            expected_peer_score = get_leadership_score(ev, "동료")
            expected_sub_score = get_leadership_score(ev, "부하")
            expected_sup_comment = get_leadership_comment(ev, "상사")
            expected_peer_comment = get_leadership_comment(ev, "동료")
            expected_sub_comment = get_leadership_comment(ev, "부하")
        else:
            expected_perf = ""
            expected_comp = ""
            expected_review = ""
            expected_sup_score = ""
            expected_peer_score = ""
            expected_sub_score = ""
            expected_sup_comment = ""
            expected_peer_comment = ""
            expected_sub_comment = ""

        compare(emp_id, f"eval.performance_{suffix}", expected_perf, v2_data.get(f"performance_{suffix}", ""))
        compare(emp_id, f"eval.competency_{suffix}", expected_comp, v2_data.get(f"competency_{suffix}", ""))
        compare(emp_id, f"eval.supervisorReview_{suffix}", expected_review, v2_data.get(f"supervisorReview_{suffix}", ""))
        compare(emp_id, f"eval.supervisorScore_{suffix}", expected_sup_score, v2_data.get(f"supervisorScore_{suffix}", ""))
        compare(emp_id, f"eval.peerScore_{suffix}", expected_peer_score, v2_data.get(f"peerScore_{suffix}", ""))
        compare(emp_id, f"eval.subordinateScore_{suffix}", expected_sub_score, v2_data.get(f"subordinateScore_{suffix}", ""))
        compare(emp_id, f"eval.supervisorComment_{suffix}", expected_sup_comment, v2_data.get(f"supervisorComment_{suffix}", ""))
        compare(emp_id, f"eval.peerComment_{suffix}", expected_peer_comment, v2_data.get(f"peerComment_{suffix}", ""))
        compare(emp_id, f"eval.subordinateComment_{suffix}", expected_sub_comment, v2_data.get(f"subordinateComment_{suffix}", ""))


# ── Run ──────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  V2 Flattened API Consistency Verification")
    print("  Comparing v1 nested vs v2 flattened for EMP001~EMP100")
    print("=" * 70)
    print()

    for i in range(1, 101):
        emp_id = f"EMP{i:03d}"
        verify_employee(emp_id)
        verify_evaluation(emp_id)
        # Progress indicator every 10 employees
        if i % 10 == 0:
            print(f"  ... checked {i}/100 employees")

    # ── Summary ──────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  VERIFICATION RESULTS")
    print("=" * 70)
    print(f"  Employees checked (employee data): {total_employees_checked}")
    print(f"  Employees checked (evaluation data): {total_evals_checked}")
    print(f"  Total fields compared: {total_fields_compared}")
    print(f"  Mismatches found: {len(mismatches)}")
    print()

    if mismatches:
        print("  MISMATCHES:")
        print("-" * 70)
        for m in mismatches:
            print(f"  Employee: {m['employeeId']}")
            print(f"  Field:    {m['field']}")
            print(f"  Expected: {repr(m['expected'])}")
            print(f"  Actual:   {repr(m['actual'])}")
            print("-" * 70)
        print()
        print(f"  RESULT: FAIL -- {len(mismatches)} mismatch(es) detected")
        sys.exit(1)
    else:
        print("  RESULT: PASS -- All v2 flattened data is consistent with v1 nested data")
        sys.exit(0)


if __name__ == "__main__":
    main()
