# -*- coding: utf-8 -*-
"""전체 API 엔드포인트 검증 스크립트"""

import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from mock_hr_api import app

client = TestClient(app)
passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")


def section(title):
    print()
    print("=" * 55)
    print(f"  {title}")
    print("=" * 55)


# ═══════════════════════════════════════════════════════
section("0-1. GET /api/v1/inhr/employees/basic (기본 인적정보 전체)")
r = client.get("/api/v1/inhr/employees/basic")
d = r.json()
check("status 200", r.status_code == 200)
check("count=10", d["count"] == 10)
e0 = d["data"][0]
check("has employeeId", "employeeId" in e0)
check("has name", "name" in e0)
check("has department", "department" in e0)
check("has grade", "grade" in e0)
check("has tenure", "tenure" in e0)
check("has lastModified", "lastModified" in e0)
check("NO educations", "educations" not in e0)
check("NO careers", "careers" not in e0)
check("NO overseasExperiences", "overseasExperiences" not in e0)
check("NO family", "family" not in e0)
check("NO certifications", "certifications" not in e0)
for e in d["data"]:
    print(f'  {e["employeeId"]} {e["name"]:6s} dept={e["department"]:16s} grade={e["grade"]} tenure={e["tenure"]}')

# ═══════════════════════════════════════════════════════
section("0-2. GET /api/v1/inhr/employees/basic/EMP001")
r = client.get("/api/v1/inhr/employees/basic/EMP001")
d = r.json()
e = d["data"]
check("status 200", r.status_code == 200)
check("employeeId=EMP001", e["employeeId"] == "EMP001")
check("name=김철수", e["name"] == "김철수")
check("department", e["department"] == "People Development팀")
check("grade=M2", e["grade"] == "M2")
check("tenure=12", e["tenure"] == 12)
check("managerId=EMP010", e["managerId"] == "EMP010")
check("NO nested keys", "educations" not in e and "careers" not in e)
print(json.dumps(d, indent=2, ensure_ascii=False))

# ═══════════════════════════════════════════════════════
section("0-3. GET /api/v1/inhr/employees/basic/EMP999 (not found)")
r = client.get("/api/v1/inhr/employees/basic/EMP999")
d = r.json()
check("status 200", r.status_code == 200)
check("data=null", d["data"] is None)
check("error present", "EMP999" in d.get("error", ""))

# ═══════════════════════════════════════════════════════
section("1. GET /api/v1/health")
r = client.get("/api/v1/health")
d = r.json()
check("status 200", r.status_code == 200)
check("status=healthy", d["status"] == "healthy")
check("employeeCount=10", d["employeeCount"] == 10)
check("dbExists=true", d["dbExists"] is True)
print(json.dumps(d, indent=2, ensure_ascii=False))

# ═══════════════════════════════════════════════════════
section("2. GET /api/v1/stats")
r = client.get("/api/v1/stats")
d = r.json()
check("status 200", r.status_code == 200)
check("employees=10", d["employees"] == 10)
check("educations=19", d["educations"] == 19)
check("careers=23", d["careers"] == 23)
check("overseasExperiences=7", d["overseasExperiences"] == 7)
check("family=20", d["family"] == 20)
check("certifications=21", d["certifications"] == 21)
check("evaluations=30", d["evaluations"] == 30)
check("evalComments=30", d["evalComments"] == 30)
check("leadershipSurveys=60", d["leadershipSurveys"] == 60)
print(json.dumps(d, indent=2, ensure_ascii=False))

# ═══════════════════════════════════════════════════════
section("3. GET /api/v1/inhr/employees (전체, nested)")
r = client.get("/api/v1/inhr/employees")
d = r.json()
check("status 200", r.status_code == 200)
check("count=10", d["count"] == 10)
check("data is list of 10", len(d["data"]) == 10)
check("deltaFrom=null", d["deltaFrom"] is None)

e0 = d["data"][0]
camel_keys = [
    "employeeId", "name", "birthDate", "department", "position", "grade",
    "tenure", "promotionDate", "photoUrl", "managerId", "lastModified",
    "educations", "careers", "overseasExperiences", "family", "certifications",
]
missing = [k for k in camel_keys if k not in e0]
check("camelCase keys present", len(missing) == 0, f"missing: {missing}")

for e in d["data"]:
    edu = len(e["educations"])
    car = len(e["careers"])
    ovs = len(e["overseasExperiences"])
    fam = len(e["family"])
    cert = len(e["certifications"])
    print(f'  {e["employeeId"]} {e["name"]:6s}  dept={e["department"]:16s} edu={edu} career={car} overseas={ovs} family={fam} cert={cert}')

# ═══════════════════════════════════════════════════════
section("4. GET /api/v1/inhr/employees/EMP001 (상세)")
r = client.get("/api/v1/inhr/employees/EMP001")
d = r.json()
e = d["data"]
check("status 200", r.status_code == 200)
check("employeeId=EMP001", e["employeeId"] == "EMP001")
check("name=김철수", e["name"] == "김철수")
check("educations=2", len(e["educations"]) == 2)
check("careers=3", len(e["careers"]) == 3)
check("career[0].isCurrent=false", e["careers"][0]["isCurrent"] is False)
check("career[-1].isCurrent=true", e["careers"][-1]["isCurrent"] is True)
check("overseasExperiences=1", len(e["overseasExperiences"]) == 1)
check("family=3", len(e["family"]) == 3)
check("family has education key", "education" in e["family"][0])
check("certifications=2", len(e["certifications"]) == 2)

# ═══════════════════════════════════════════════════════
section("5. GET /api/v1/inhr/employees/EMP999 (not found)")
r = client.get("/api/v1/inhr/employees/EMP999")
d = r.json()
check("status 200", r.status_code == 200)
check("data=null", d["data"] is None)
check("error message present", "EMP999" in d.get("error", ""))

# ═══════════════════════════════════════════════════════
section("6. GET /api/v1/inhr/educations (전체 학력)")
r = client.get("/api/v1/inhr/educations")
d = r.json()
check("status 200", r.status_code == 200)
check("count=19", d["count"] == 19)
check("has employeeId", "employeeId" in d["data"][0])
check("has gradYear", "gradYear" in d["data"][0])
emp_ids = set(x["employeeId"] for x in d["data"])
print(f'  {d["count"]} records, employees: {sorted(emp_ids)}')

# ═══════════════════════════════════════════════════════
section("7. GET /api/v1/inhr/educations/EMP001 (EMP001 학력)")
r = client.get("/api/v1/inhr/educations/EMP001")
d = r.json()
check("status 200", r.status_code == 200)
check("count=2", d["count"] == 2)
check("all employeeId=EMP001", all(x["employeeId"] == "EMP001" for x in d["data"]))
for x in d["data"]:
    print(f'  {x["school"]} {x["degree"]} {x["major"]} ({x["gradYear"]})')

# ═══════════════════════════════════════════════════════
section("8. GET /api/v1/inhr/educations/EMP999 (빈 결과)")
r = client.get("/api/v1/inhr/educations/EMP999")
d = r.json()
check("status 200", r.status_code == 200)
check("count=0", d["count"] == 0)
check("data=[]", d["data"] == [])

# ═══════════════════════════════════════════════════════
section("9. GET /api/v1/inhr/careers (전체 경력)")
r = client.get("/api/v1/inhr/careers")
d = r.json()
check("status 200", r.status_code == 200)
check("count=23", d["count"] == 23)
check("has isCurrent", "isCurrent" in d["data"][0])
current = [x for x in d["data"] if x["isCurrent"]]
past = [x for x in d["data"] if not x["isCurrent"]]
print(f'  {d["count"]} records (current={len(current)}, past={len(past)})')

# ═══════════════════════════════════════════════════════
section("10. GET /api/v1/inhr/careers/EMP001 (EMP001 경력)")
r = client.get("/api/v1/inhr/careers/EMP001")
d = r.json()
check("status 200", r.status_code == 200)
check("count=3", d["count"] == 3)
check("isCurrent correct", d["data"][-1]["isCurrent"] is True and d["data"][0]["isCurrent"] is False)
for x in d["data"]:
    cur = "★" if x["isCurrent"] else " "
    print(f'  {cur} {x["company"]} {x["department"]} {x["role"]} ({x["startDate"]}~{x["endDate"] or "현재"})')

# ═══════════════════════════════════════════════════════
section("11. GET /api/v1/inhr/overseas (전체 해외경험)")
r = client.get("/api/v1/inhr/overseas")
d = r.json()
check("status 200", r.status_code == 200)
check("count=7", d["count"] == 7)
check("has country", "country" in d["data"][0])
for x in d["data"]:
    print(f'  {x["employeeId"]} {x["country"]} {x["purpose"][:30]}')

# ═══════════════════════════════════════════════════════
section("12. GET /api/v1/inhr/overseas/EMP003 (EMP003 해외경험)")
r = client.get("/api/v1/inhr/overseas/EMP003")
d = r.json()
check("status 200", r.status_code == 200)
check("count=2", d["count"] == 2)
check("all employeeId=EMP003", all(x["employeeId"] == "EMP003" for x in d["data"]))

# ═══════════════════════════════════════════════════════
section("13. GET /api/v1/inhr/family (전체 가족사항)")
r = client.get("/api/v1/inhr/family")
d = r.json()
check("status 200", r.status_code == 200)
check("count=20", d["count"] == 20)
check("has education key (not finalEducation)", "education" in d["data"][0] and "finalEducation" not in d["data"][0])
for x in d["data"][:5]:
    print(f'  {x["employeeId"]} {x["relation"]} {x["name"]} edu={x["education"][:20]}')
print(f"  ... ({d['count']} total)")

# ═══════════════════════════════════════════════════════
section("14. GET /api/v1/inhr/family/EMP001 (EMP001 가족사항)")
r = client.get("/api/v1/inhr/family/EMP001")
d = r.json()
check("status 200", r.status_code == 200)
check("count=3", d["count"] == 3)
for x in d["data"]:
    print(f'  {x["relation"]} {x["name"]} ({x["birthYear"]}) edu={x["education"]}')

# ═══════════════════════════════════════════════════════
section("15. GET /api/v1/inhr/certifications (전체 자격/어학)")
r = client.get("/api/v1/inhr/certifications")
d = r.json()
check("status 200", r.status_code == 200)
check("count=21", d["count"] == 21)
check("has certName", "certName" in d["data"][0])
check("has scoreOrGrade", "scoreOrGrade" in d["data"][0])
for x in d["data"][:5]:
    print(f'  {x["employeeId"]} {x["certName"]} {x["scoreOrGrade"]} ({x["issuedDate"]})')
print(f"  ... ({d['count']} total)")

# ═══════════════════════════════════════════════════════
section("16. GET /api/v1/inhr/certifications/EMP001 (EMP001 자격)")
r = client.get("/api/v1/inhr/certifications/EMP001")
d = r.json()
check("status 200", r.status_code == 200)
check("count=2", d["count"] == 2)
for x in d["data"]:
    print(f'  {x["certName"]} ({x["issuer"]}) {x["scoreOrGrade"]}')

# ═══════════════════════════════════════════════════════
section("17. GET /api/v1/myhr/evaluations (전체 평가)")
r = client.get("/api/v1/myhr/evaluations")
d = r.json()
check("status 200", r.status_code == 200)
check("count=10", d["count"] == 10)
check("deltaFrom=null", d["deltaFrom"] is None)
for ev in d["data"]:
    yrs = ",".join(str(y["year"]) for y in ev["evaluations"])
    print(f'  {ev["employeeId"]} years={yrs}')

# ═══════════════════════════════════════════════════════
section("18. GET /api/v1/myhr/evaluations/EMP001 (상세)")
r = client.get("/api/v1/myhr/evaluations/EMP001")
d = r.json()
ev = d["data"]
check("status 200", r.status_code == 200)
check("employeeId=EMP001", ev["employeeId"] == "EMP001")
check("3 years of eval", len(ev["evaluations"]) == 3)
y0 = ev["evaluations"][0]
check("comment.type=상사평가", y0["comment"]["type"] == "상사평가")
check("leadershipSurveys=2", len(y0["leadershipSurveys"]) == 2)
check("survey score is float", isinstance(y0["leadershipSurveys"][0]["score"], float))
for y in ev["evaluations"]:
    print(f'  {y["year"]}: perf={y["performanceGrade"]} comp={y["competencyGrade"]} surveys={len(y["leadershipSurveys"])}')

# ═══════════════════════════════════════════════════════
section("19. GET /api/v1/myhr/evaluations/EMP999 (not found)")
r = client.get("/api/v1/myhr/evaluations/EMP999")
d = r.json()
check("data=null", d["data"] is None)
check("error message", "EMP999" in d.get("error", ""))

# ═══════════════════════════════════════════════════════
section("20. Delta Sync -- modifiedAfter 테스트")
r = client.get("/api/v1/inhr/employees?modifiedAfter=2099-01-01T00:00:00Z")
d = r.json()
check("future date -> count=0", d["count"] == 0)
check("deltaFrom set", d["deltaFrom"] == "2099-01-01T00:00:00Z")

r = client.get("/api/v1/inhr/employees?modifiedAfter=2000-01-01T00:00:00Z")
d = r.json()
check("past date -> count=10", d["count"] == 10)

r = client.get("/api/v1/myhr/evaluations?modifiedAfter=2099-01-01T00:00:00Z")
d = r.json()
check("eval future date -> count=0", d["count"] == 0)

r = client.get("/api/v1/myhr/evaluations?modifiedAfter=2000-01-01T00:00:00Z")
d = r.json()
check("eval past date -> count=10", d["count"] == 10)


# ═══════════════════════════════════════════════════════
print()
print("=" * 55)
if failed == 0:
    print(f"  ALL PASSED: {passed} tests")
else:
    print(f"  RESULT: {passed} passed, {failed} FAILED")
print("=" * 55)

sys.exit(0 if failed == 0 else 1)
