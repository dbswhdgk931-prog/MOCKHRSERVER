# -*- coding: utf-8 -*-
"""프로덕션 (Render) 전체 API 검증 스크립트"""

import json
import ssl
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://mockhrserver.onrender.com"
passed = 0
failed = 0

# 회사 네트워크 SSL 프록시 우회용
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def fetch(path):
    url = BASE + path
    resp = urllib.request.urlopen(url, timeout=30, context=_ctx)
    return json.loads(resp.read().decode("utf-8"))


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")


def section(title):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ═══════════════════════════════════════════════════════
section("1. GET /api/v1/health")
d = fetch("/api/v1/health")
check("status=healthy", d["status"] == "healthy")
check("employeeCount=10", d["employeeCount"] == 10)
check("dbExists=true", d["dbExists"] is True)
print(json.dumps(d, indent=2, ensure_ascii=False))

# ═══════════════════════════════════════════════════════
section("2. GET /api/v1/stats")
d = fetch("/api/v1/stats")
check("employees=10", d["employees"] == 10)
check("educations=19", d["educations"] == 19)
check("careers=23", d["careers"] == 23)
check("overseasExperiences=7", d["overseasExperiences"] == 7)
check("family=20", d["family"] == 20)
check("certifications=21", d["certifications"] == 21)
check("evaluations=30", d["evaluations"] == 30)
check("evalComments=30", d["evalComments"] == 30)
check("leadershipSurveys=60", d["leadershipSurveys"] == 60)

# ═══════════════════════════════════════════════════════
section("3. GET /api/v1/inhr/employees/basic (기본 인적정보)")
d = fetch("/api/v1/inhr/employees/basic")
check("count=10", d["count"] == 10)
e0 = d["data"][0]
check("has employeeId", "employeeId" in e0)
check("NO educations", "educations" not in e0)
check("NO careers", "careers" not in e0)
for e in d["data"]:
    print(f'  {e["employeeId"]} {e["name"]:6s} dept={e["department"]:16s} grade={e["grade"]} tenure={e["tenure"]}')

# ═══════════════════════════════════════════════════════
section("4. GET /api/v1/inhr/employees/basic/EMP001")
d = fetch("/api/v1/inhr/employees/basic/EMP001")
e = d["data"]
check("employeeId=EMP001", e["employeeId"] == "EMP001")
check("name=김철수", e["name"] == "김철수")
check("department", e["department"] == "People Development팀")
check("grade=M2", e["grade"] == "M2")
check("tenure=12", e["tenure"] == 12)
check("managerId=EMP010", e["managerId"] == "EMP010")
check("NO nested", "educations" not in e)

# ═══════════════════════════════════════════════════════
section("5. GET /api/v1/inhr/employees/basic/EMP999 (not found)")
d = fetch("/api/v1/inhr/employees/basic/EMP999")
check("data=null", d["data"] is None)
check("error present", "EMP999" in d.get("error", ""))

# ═══════════════════════════════════════════════════════
section("6. GET /api/v1/inhr/employees (전체인적정보, nested)")
d = fetch("/api/v1/inhr/employees")
check("count=10", d["count"] == 10)
check("deltaFrom=null", d["deltaFrom"] is None)
camel_keys = [
    "employeeId", "name", "birthDate", "department", "position", "grade",
    "tenure", "promotionDate", "photoUrl", "managerId", "lastModified",
    "educations", "careers", "overseasExperiences", "family", "certifications",
]
missing = [k for k in camel_keys if k not in d["data"][0]]
check("camelCase keys", len(missing) == 0, f"missing: {missing}")
for e in d["data"]:
    edu = len(e["educations"])
    car = len(e["careers"])
    ovs = len(e["overseasExperiences"])
    fam = len(e["family"])
    cert = len(e["certifications"])
    print(f'  {e["employeeId"]} {e["name"]:6s} edu={edu} career={car} overseas={ovs} family={fam} cert={cert}')

# ═══════════════════════════════════════════════════════
section("7. GET /api/v1/inhr/employees/EMP001 (상세)")
d = fetch("/api/v1/inhr/employees/EMP001")
e = d["data"]
check("employeeId=EMP001", e["employeeId"] == "EMP001")
check("educations=2", len(e["educations"]) == 2)
check("careers=3", len(e["careers"]) == 3)
check("career[0].isCurrent=false", e["careers"][0]["isCurrent"] is False)
check("career[-1].isCurrent=true", e["careers"][-1]["isCurrent"] is True)
check("overseasExperiences=1", len(e["overseasExperiences"]) == 1)
check("family=3", len(e["family"]) == 3)
check("family.education key", "education" in e["family"][0])
check("certifications=2", len(e["certifications"]) == 2)

# ═══════════════════════════════════════════════════════
section("8. GET /api/v1/inhr/employees/EMP999 (not found)")
d = fetch("/api/v1/inhr/employees/EMP999")
check("data=null", d["data"] is None)
check("error present", "EMP999" in d.get("error", ""))

# ═══════════════════════════════════════════════════════
section("9. GET /api/v1/inhr/educations")
d = fetch("/api/v1/inhr/educations")
check("count=19", d["count"] == 19)
check("has employeeId", "employeeId" in d["data"][0])
emp_ids = sorted(set(x["employeeId"] for x in d["data"]))
check("10 employees", len(emp_ids) == 10)

# ═══════════════════════════════════════════════════════
section("10. GET /api/v1/inhr/educations/EMP001")
d = fetch("/api/v1/inhr/educations/EMP001")
check("count=2", d["count"] == 2)
check("all EMP001", all(x["employeeId"] == "EMP001" for x in d["data"]))
for x in d["data"]:
    print(f'  {x["school"]} {x["degree"]} {x["major"]} ({x["gradYear"]})')

# ═══════════════════════════════════════════════════════
section("11. GET /api/v1/inhr/careers")
d = fetch("/api/v1/inhr/careers")
check("count=23", d["count"] == 23)
current = sum(1 for x in d["data"] if x["isCurrent"])
past = sum(1 for x in d["data"] if not x["isCurrent"])
check("current+past=23", current + past == 23)
print(f"  current={current}, past={past}")

# ═══════════════════════════════════════════════════════
section("12. GET /api/v1/inhr/careers/EMP001")
d = fetch("/api/v1/inhr/careers/EMP001")
check("count=3", d["count"] == 3)
check("last isCurrent=true", d["data"][-1]["isCurrent"] is True)
for x in d["data"]:
    cur = "NOW" if x["isCurrent"] else "   "
    end = x["endDate"] or "현재"
    print(f'  [{cur}] {x["company"]} {x["department"]} {x["role"]} ({x["startDate"]}~{end})')

# ═══════════════════════════════════════════════════════
section("13. GET /api/v1/inhr/overseas")
d = fetch("/api/v1/inhr/overseas")
check("count=7", d["count"] == 7)
for x in d["data"]:
    print(f'  {x["employeeId"]} {x["country"]} {x["purpose"][:35]}')

# ═══════════════════════════════════════════════════════
section("14. GET /api/v1/inhr/overseas/EMP003")
d = fetch("/api/v1/inhr/overseas/EMP003")
check("count=2", d["count"] == 2)
check("all EMP003", all(x["employeeId"] == "EMP003" for x in d["data"]))

# ═══════════════════════════════════════════════════════
section("15. GET /api/v1/inhr/family")
d = fetch("/api/v1/inhr/family")
check("count=20", d["count"] == 20)
check("education key (not finalEducation)", "education" in d["data"][0] and "finalEducation" not in d["data"][0])
for x in d["data"][:5]:
    print(f'  {x["employeeId"]} {x["relation"]} {x["name"]} edu={x["education"][:20]}')
print(f'  ... ({d["count"]} total)')

# ═══════════════════════════════════════════════════════
section("16. GET /api/v1/inhr/family/EMP001")
d = fetch("/api/v1/inhr/family/EMP001")
check("count=3", d["count"] == 3)
for x in d["data"]:
    print(f'  {x["relation"]} {x["name"]} ({x["birthYear"]}) edu={x["education"]}')

# ═══════════════════════════════════════════════════════
section("17. GET /api/v1/inhr/certifications")
d = fetch("/api/v1/inhr/certifications")
check("count=21", d["count"] == 21)
check("has certName", "certName" in d["data"][0])
for x in d["data"][:5]:
    print(f'  {x["employeeId"]} {x["certName"]} {x["scoreOrGrade"]} ({x["issuedDate"]})')
print(f'  ... ({d["count"]} total)')

# ═══════════════════════════════════════════════════════
section("18. GET /api/v1/inhr/certifications/EMP001")
d = fetch("/api/v1/inhr/certifications/EMP001")
check("count=2", d["count"] == 2)
for x in d["data"]:
    print(f'  {x["certName"]} ({x["issuer"]}) {x["scoreOrGrade"]}')

# ═══════════════════════════════════════════════════════
section("19. GET /api/v1/myhr/evaluations")
d = fetch("/api/v1/myhr/evaluations")
check("count=10", d["count"] == 10)
check("deltaFrom=null", d["deltaFrom"] is None)
for ev in d["data"]:
    yrs = ",".join(str(y["year"]) for y in ev["evaluations"])
    n_s = len(ev["evaluations"][0]["leadershipSurveys"])
    print(f'  {ev["employeeId"]} years={yrs} surveys/yr={n_s}')

# ═══════════════════════════════════════════════════════
section("20. GET /api/v1/myhr/evaluations/EMP001 (상세)")
d = fetch("/api/v1/myhr/evaluations/EMP001")
ev = d["data"]
check("employeeId=EMP001", ev["employeeId"] == "EMP001")
check("3 years", len(ev["evaluations"]) == 3)
y0 = ev["evaluations"][0]
check("year=2023", y0["year"] == 2023)
check("performanceGrade=A", y0["performanceGrade"] == "A")
check("competencyGrade=A", y0["competencyGrade"] == "A")
check("comment exists", y0["comment"] is not None)
check("comment.type=상사평가", y0["comment"]["type"] == "상사평가")
check("comment.text non-empty", len(y0["comment"]["text"]) > 10)
check("leadershipSurveys=2", len(y0["leadershipSurveys"]) == 2)
s0 = y0["leadershipSurveys"][0]
check("survey score is float", isinstance(s0["score"], float))
check("has strengthComment", len(s0["strengthComment"]) > 0)
check("has developmentComment", len(s0["developmentComment"]) > 0)
for y in ev["evaluations"]:
    c = y["comment"]
    ctype = c["type"] if c else "none"
    print(f'  {y["year"]}: perf={y["performanceGrade"]} comp={y["competencyGrade"]} comment={ctype} surveys={len(y["leadershipSurveys"])}')

# ═══════════════════════════════════════════════════════
section("21. GET /api/v1/myhr/evaluations/EMP999 (not found)")
d = fetch("/api/v1/myhr/evaluations/EMP999")
check("data=null", d["data"] is None)
check("error present", "EMP999" in d.get("error", ""))

# ═══════════════════════════════════════════════════════
section("22. Delta Sync")
d = fetch("/api/v1/inhr/employees?modifiedAfter=2099-01-01T00:00:00Z")
check("employees future -> count=0", d["count"] == 0)
check("deltaFrom set", d["deltaFrom"] == "2099-01-01T00:00:00Z")

d = fetch("/api/v1/inhr/employees?modifiedAfter=2000-01-01T00:00:00Z")
check("employees past -> count=10", d["count"] == 10)

d = fetch("/api/v1/myhr/evaluations?modifiedAfter=2099-01-01T00:00:00Z")
check("evaluations future -> count=0", d["count"] == 0)

d = fetch("/api/v1/myhr/evaluations?modifiedAfter=2000-01-01T00:00:00Z")
check("evaluations past -> count=10", d["count"] == 10)

# ═══════════════════════════════════════════════════════
section("23. 데이터 정합성 크로스체크")
stats = fetch("/api/v1/stats")
emps = fetch("/api/v1/inhr/employees")
edus = fetch("/api/v1/inhr/educations")
cars = fetch("/api/v1/inhr/careers")
ovs = fetch("/api/v1/inhr/overseas")
fam = fetch("/api/v1/inhr/family")
certs = fetch("/api/v1/inhr/certifications")
evals = fetch("/api/v1/myhr/evaluations")

nested_edu = sum(len(e["educations"]) for e in emps["data"])
nested_car = sum(len(e["careers"]) for e in emps["data"])
nested_ovs = sum(len(e["overseasExperiences"]) for e in emps["data"])
nested_fam = sum(len(e["family"]) for e in emps["data"])
nested_cert = sum(len(e["certifications"]) for e in emps["data"])
nested_eval = sum(len(ev["evaluations"]) for ev in evals["data"])

check(
    f"교육: stats({stats['educations']}) == individual({edus['count']}) == nested({nested_edu})",
    stats["educations"] == edus["count"] == nested_edu,
)
check(
    f"경력: stats({stats['careers']}) == individual({cars['count']}) == nested({nested_car})",
    stats["careers"] == cars["count"] == nested_car,
)
check(
    f"해외: stats({stats['overseasExperiences']}) == individual({ovs['count']}) == nested({nested_ovs})",
    stats["overseasExperiences"] == ovs["count"] == nested_ovs,
)
check(
    f"가족: stats({stats['family']}) == individual({fam['count']}) == nested({nested_fam})",
    stats["family"] == fam["count"] == nested_fam,
)
check(
    f"자격: stats({stats['certifications']}) == individual({certs['count']}) == nested({nested_cert})",
    stats["certifications"] == certs["count"] == nested_cert,
)
check(
    f"평가: stats({stats['evaluations']}) == nested({nested_eval})",
    stats["evaluations"] == nested_eval,
)

# ═══════════════════════════════════════════════════════
print()
print("=" * 60)
if failed == 0:
    print(f"  PRODUCTION ALL PASSED: {passed} tests")
else:
    print(f"  RESULT: {passed} passed, {failed} FAILED")
print(f"  Target: {BASE}")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
