"""
v2 평탄화 로직
기존 v1 Pydantic 모델 객체를 입력받아 v2 flat 모델로 변환
"""

from models import Employee, EmployeeEvaluation
from v2_models import EmployeeFlatV2, EvaluationFlatV2, ReferenceYears


SEPARATOR = " / "


# ── 인사정보 평탄화 ──────────────────────────────────────────

def _flatten_educations(employee: Employee) -> str:
    """교육: {school} {major} {degree} ({gradYear}년 졸업)"""
    if not employee.educations:
        return ""
    parts = []
    for e in employee.educations:
        parts.append(f"{e.school} {e.major} {e.degree} ({e.grad_year}년 졸업)")
    return SEPARATOR.join(parts)


def _flatten_careers(employee: Employee) -> str:
    """경력: {company} {department} {role}, {region} ({startDate}~{endDate|재직중}) - {description}"""
    if not employee.careers:
        return ""
    parts = []
    for c in employee.careers:
        end = c.end_date if c.end_date else "재직중"
        region_part = f", {c.region}" if c.region else ""
        desc_part = f" - {c.description}" if c.description else ""
        parts.append(
            f"{c.company} {c.department} {c.role}{region_part} ({c.start_date}~{end}){desc_part}"
        )
    return SEPARATOR.join(parts)


def _flatten_overseas(employee: Employee) -> str:
    """해외경험: {country} {purpose} ({startDate}~{endDate})"""
    if not employee.overseas_experiences:
        return ""
    parts = []
    for o in employee.overseas_experiences:
        parts.append(f"{o.country} {o.purpose} ({o.start_date}~{o.end_date})")
    return SEPARATOR.join(parts)


def _flatten_family(employee: Employee) -> str:
    """가족: {relation} {name} ({birthYear}년생, {education}, {occupation})"""
    if not employee.family:
        return ""
    parts = []
    for f in employee.family:
        birth = f"{f.birth_year}년생" if f.birth_year else ""
        details = ", ".join(d for d in [birth, f.education, f.occupation] if d)
        parts.append(f"{f.relation} {f.name} ({details})")
    return SEPARATOR.join(parts)


def _flatten_certifications(employee: Employee) -> str:
    """자격증: {certName} {scoreOrGrade} (발급: {issuer}/{country}, 발급일: {issuedDate}, 만료: {expiryDate})"""
    if not employee.certifications:
        return ""
    parts = []
    for c in employee.certifications:
        expiry = f", 만료: {c.expiry_date}" if c.expiry_date else ""
        parts.append(
            f"{c.cert_name} {c.score_or_grade} (발급: {c.issuer}/{c.country}, 발급일: {c.issued_date}{expiry})"
        )
    return SEPARATOR.join(parts)


def flatten_employee(employee: Employee) -> EmployeeFlatV2:
    """v1 Employee → v2 EmployeeFlatV2"""
    return EmployeeFlatV2(
        employee_id=employee.employee_id,
        name=employee.name,
        birth_date=employee.birth_date,
        department=employee.department,
        position=employee.position,
        grade=employee.grade,
        tenure=employee.tenure,
        promotion_date=employee.promotion_date,
        photo_url=employee.photo_url,
        manager_id=employee.manager_id,
        last_modified=employee.last_modified,
        education_summary=_flatten_educations(employee),
        career_summary=_flatten_careers(employee),
        overseas_summary=_flatten_overseas(employee),
        family_summary=_flatten_family(employee),
        certification_summary=_flatten_certifications(employee),
    )


# ── 평가정보 평탄화 ──────────────────────────────────────────

def _get_supervisor_review(eval_year) -> str:
    """supervisorReview: {text} ({commenter})"""
    if eval_year.comment:
        return f"{eval_year.comment.text} ({eval_year.comment.commenter})"
    return ""


def _get_leadership_by_type(eval_year, evaluator_type: str):
    """특정 evaluator_type의 리더십 서베이 데이터 반환"""
    for s in eval_year.leadership_surveys:
        if s.evaluator_type == evaluator_type:
            return s
    return None


def _get_score(eval_year, evaluator_type: str) -> str:
    """점수를 문자열로 반환"""
    s = _get_leadership_by_type(eval_year, evaluator_type)
    if s is None:
        return ""
    return str(s.score)


def _get_comment(eval_year, evaluator_type: str) -> str:
    """리더십 코멘트: {strengthComment} / {developmentComment}"""
    s = _get_leadership_by_type(eval_year, evaluator_type)
    if s is None:
        return ""
    parts = [p for p in [s.strength_comment, s.development_comment] if p]
    return " / ".join(parts) if parts else ""


def _flatten_eval_year(eval_year) -> dict:
    """단일 연도 평가 → 접미사 없는 필드 dict"""
    return {
        "performance": eval_year.performance_grade,
        "competency": eval_year.competency_grade,
        "supervisor_review": _get_supervisor_review(eval_year),
        "supervisor_score": _get_score(eval_year, "상사"),
        "peer_score": _get_score(eval_year, "동료"),
        "subordinate_score": _get_score(eval_year, "부하"),
        "supervisor_comment": _get_comment(eval_year, "상사"),
        "peer_comment": _get_comment(eval_year, "동료"),
        "subordinate_comment": _get_comment(eval_year, "부하"),
    }


def flatten_evaluation(evaluation: EmployeeEvaluation) -> EvaluationFlatV2:
    """v1 EmployeeEvaluation → v2 EvaluationFlatV2"""
    # year 내림차순 정렬 후 상위 3개
    sorted_evals = sorted(evaluation.evaluations, key=lambda e: e.year, reverse=True)
    slots = sorted_evals[:3]

    # 빈 슬롯 채우기
    empty = {
        "performance": "", "competency": "", "supervisor_review": "",
        "supervisor_score": "", "peer_score": "", "subordinate_score": "",
        "supervisor_comment": "", "peer_comment": "", "subordinate_comment": "",
    }

    n_data = _flatten_eval_year(slots[0]) if len(slots) > 0 else empty
    n1_data = _flatten_eval_year(slots[1]) if len(slots) > 1 else empty
    n2_data = _flatten_eval_year(slots[2]) if len(slots) > 2 else empty

    n_year = slots[0].year if len(slots) > 0 else 0
    n1_year = slots[1].year if len(slots) > 1 else 0
    n2_year = slots[2].year if len(slots) > 2 else 0

    return EvaluationFlatV2(
        employee_id=evaluation.employee_id,
        last_modified=evaluation.last_modified,
        reference_years=ReferenceYears(N=n_year, N1=n1_year, N2=n2_year),
        # N
        performance_N=n_data["performance"],
        competency_N=n_data["competency"],
        supervisor_review_N=n_data["supervisor_review"],
        supervisor_score_N=n_data["supervisor_score"],
        peer_score_N=n_data["peer_score"],
        subordinate_score_N=n_data["subordinate_score"],
        supervisor_comment_N=n_data["supervisor_comment"],
        peer_comment_N=n_data["peer_comment"],
        subordinate_comment_N=n_data["subordinate_comment"],
        # N1
        performance_N1=n1_data["performance"],
        competency_N1=n1_data["competency"],
        supervisor_review_N1=n1_data["supervisor_review"],
        supervisor_score_N1=n1_data["supervisor_score"],
        peer_score_N1=n1_data["peer_score"],
        subordinate_score_N1=n1_data["subordinate_score"],
        supervisor_comment_N1=n1_data["supervisor_comment"],
        peer_comment_N1=n1_data["peer_comment"],
        subordinate_comment_N1=n1_data["subordinate_comment"],
        # N2
        performance_N2=n2_data["performance"],
        competency_N2=n2_data["competency"],
        supervisor_review_N2=n2_data["supervisor_review"],
        supervisor_score_N2=n2_data["supervisor_score"],
        peer_score_N2=n2_data["peer_score"],
        subordinate_score_N2=n2_data["subordinate_score"],
        supervisor_comment_N2=n2_data["supervisor_comment"],
        peer_comment_N2=n2_data["peer_comment"],
        subordinate_comment_N2=n2_data["subordinate_comment"],
    )
