"""
v2 Pydantic 모델 — 평탄화(Flattened) 응답용
Copilot Studio / Power Automate에서 전처리 없이 바로 사용 가능하도록
모든 nested 데이터를 문자열로 평탄화한 모델
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


# ── 인사정보 (Flat) ──────────────────────────────────────────

class EmployeeFlatV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    name: str = Field(serialization_alias="name")
    birth_date: str = Field(serialization_alias="birthDate")
    department: str = Field(serialization_alias="department")
    position: str = Field(serialization_alias="position")
    grade: str = Field(serialization_alias="grade")
    tenure: int = Field(serialization_alias="tenure")
    promotion_date: str = Field(serialization_alias="promotionDate")
    photo_url: str = Field(serialization_alias="photoUrl")
    manager_id: str = Field("", serialization_alias="managerId")
    last_modified: str = Field(serialization_alias="lastModified")

    # 평탄화된 요약 문자열
    education_summary: str = Field("", serialization_alias="educationSummary")
    career_summary: str = Field("", serialization_alias="careerSummary")
    overseas_summary: str = Field("", serialization_alias="overseasSummary")
    family_summary: str = Field("", serialization_alias="familySummary")
    certification_summary: str = Field("", serialization_alias="certificationSummary")


# ── 평가정보 (Flat) ──────────────────────────────────────────

class ReferenceYears(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    N: int = Field(serialization_alias="N")
    N1: int = Field(serialization_alias="N1")
    N2: int = Field(serialization_alias="N2")


class EvaluationFlatV2(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    last_modified: str = Field(serialization_alias="lastModified")

    reference_years: ReferenceYears = Field(serialization_alias="referenceYears")

    # N년도 (최신)
    performance_N: str = Field("", serialization_alias="performance_N")
    competency_N: str = Field("", serialization_alias="competency_N")
    supervisor_review_N: str = Field("", serialization_alias="supervisorReview_N")
    supervisor_score_N: str = Field("", serialization_alias="supervisorScore_N")
    peer_score_N: str = Field("", serialization_alias="peerScore_N")
    subordinate_score_N: str = Field("", serialization_alias="subordinateScore_N")
    supervisor_comment_N: str = Field("", serialization_alias="supervisorComment_N")
    peer_comment_N: str = Field("", serialization_alias="peerComment_N")
    subordinate_comment_N: str = Field("", serialization_alias="subordinateComment_N")

    # N-1년도
    performance_N1: str = Field("", serialization_alias="performance_N1")
    competency_N1: str = Field("", serialization_alias="competency_N1")
    supervisor_review_N1: str = Field("", serialization_alias="supervisorReview_N1")
    supervisor_score_N1: str = Field("", serialization_alias="supervisorScore_N1")
    peer_score_N1: str = Field("", serialization_alias="peerScore_N1")
    subordinate_score_N1: str = Field("", serialization_alias="subordinateScore_N1")
    supervisor_comment_N1: str = Field("", serialization_alias="supervisorComment_N1")
    peer_comment_N1: str = Field("", serialization_alias="peerComment_N1")
    subordinate_comment_N1: str = Field("", serialization_alias="subordinateComment_N1")

    # N-2년도
    performance_N2: str = Field("", serialization_alias="performance_N2")
    competency_N2: str = Field("", serialization_alias="competency_N2")
    supervisor_review_N2: str = Field("", serialization_alias="supervisorReview_N2")
    supervisor_score_N2: str = Field("", serialization_alias="supervisorScore_N2")
    peer_score_N2: str = Field("", serialization_alias="peerScore_N2")
    subordinate_score_N2: str = Field("", serialization_alias="subordinateScore_N2")
    supervisor_comment_N2: str = Field("", serialization_alias="supervisorComment_N2")
    peer_comment_N2: str = Field("", serialization_alias="peerComment_N2")
    subordinate_comment_N2: str = Field("", serialization_alias="subordinateComment_N2")


# ── 응답 Envelope ────────────────────────────────────────────

class EmployeeFlatV2Response(BaseModel):
    data: Optional[EmployeeFlatV2] = None
    error: Optional[str] = None


class EvaluationFlatV2Response(BaseModel):
    data: Optional[EvaluationFlatV2] = None
    error: Optional[str] = None
