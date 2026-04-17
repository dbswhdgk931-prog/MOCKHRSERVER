"""
Pydantic 응답 모델 — OpenAPI 스키마 자동 생성용
camelCase JSON 출력 (기존 API 호환)
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Education(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    school: str = Field(serialization_alias="school")
    degree: str = Field(serialization_alias="degree")
    major: str = Field(serialization_alias="major")
    grad_year: int = Field(serialization_alias="gradYear")


class Career(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    company: str = Field(serialization_alias="company")
    department: str = Field(serialization_alias="department")
    role: str = Field(serialization_alias="role")
    start_date: str = Field(serialization_alias="startDate")
    end_date: Optional[str] = Field(None, serialization_alias="endDate")
    region: str = Field("", serialization_alias="region")
    description: str = Field("", serialization_alias="description")
    is_current: bool = Field(serialization_alias="isCurrent")


class OverseasExperience(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    country: str = Field(serialization_alias="country")
    purpose: str = Field(serialization_alias="purpose")
    start_date: str = Field(serialization_alias="startDate")
    end_date: str = Field(serialization_alias="endDate")


class Family(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    relation: str = Field(serialization_alias="relation")
    name: str = Field(serialization_alias="name")
    birth_year: Optional[int] = Field(None, serialization_alias="birthYear")
    education: str = Field("", serialization_alias="education")
    occupation: str = Field("", serialization_alias="occupation")


class Certification(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cert_name: str = Field(serialization_alias="certName")
    issuer: str = Field(serialization_alias="issuer")
    country: str = Field(serialization_alias="country")
    score_or_grade: str = Field(serialization_alias="scoreOrGrade")
    issued_date: str = Field(serialization_alias="issuedDate")
    expiry_date: str = Field("", serialization_alias="expiryDate")


class EmployeeBasic(BaseModel):
    """기본 인적정보 (01_Employee.xlsx 1:1 매핑, nested 없음)"""
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


class Employee(BaseModel):
    """전체 인적정보 (기본정보 + 학력/경력/해외/가족/자격 nested)"""
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
    educations: list[Education] = Field(default_factory=list, serialization_alias="educations")
    careers: list[Career] = Field(default_factory=list, serialization_alias="careers")
    overseas_experiences: list[OverseasExperience] = Field(default_factory=list, serialization_alias="overseasExperiences")
    family: list[Family] = Field(default_factory=list, serialization_alias="family")
    certifications: list[Certification] = Field(default_factory=list, serialization_alias="certifications")


# --- 개별 조회용 (employeeId 포함) ---

class EducationWithEmployee(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    school: str = Field(serialization_alias="school")
    degree: str = Field(serialization_alias="degree")
    major: str = Field(serialization_alias="major")
    grad_year: int = Field(serialization_alias="gradYear")


class CareerWithEmployee(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    company: str = Field(serialization_alias="company")
    department: str = Field(serialization_alias="department")
    role: str = Field(serialization_alias="role")
    start_date: str = Field(serialization_alias="startDate")
    end_date: Optional[str] = Field(None, serialization_alias="endDate")
    region: str = Field("", serialization_alias="region")
    description: str = Field("", serialization_alias="description")
    is_current: bool = Field(serialization_alias="isCurrent")


class OverseasExpWithEmployee(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    country: str = Field(serialization_alias="country")
    purpose: str = Field(serialization_alias="purpose")
    start_date: str = Field(serialization_alias="startDate")
    end_date: str = Field(serialization_alias="endDate")


class FamilyWithEmployee(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    relation: str = Field(serialization_alias="relation")
    name: str = Field(serialization_alias="name")
    birth_year: Optional[int] = Field(None, serialization_alias="birthYear")
    education: str = Field("", serialization_alias="education")
    occupation: str = Field("", serialization_alias="occupation")


class CertificationWithEmployee(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    cert_name: str = Field(serialization_alias="certName")
    issuer: str = Field(serialization_alias="issuer")
    country: str = Field(serialization_alias="country")
    score_or_grade: str = Field(serialization_alias="scoreOrGrade")
    issued_date: str = Field(serialization_alias="issuedDate")
    expiry_date: str = Field("", serialization_alias="expiryDate")


# --- 평가 관련 ---

class LeadershipSurvey(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    evaluator_type: str = Field(serialization_alias="evaluatorType")
    score: float = Field(serialization_alias="score")
    strength_comment: str = Field(serialization_alias="strengthComment")
    development_comment: str = Field(serialization_alias="developmentComment")


class EvalComment(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(serialization_alias="type")
    text: str = Field(serialization_alias="text")
    commenter: str = Field("직속상사", serialization_alias="commenter")


class EvaluationYear(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    year: int = Field(serialization_alias="year")
    performance_grade: str = Field(serialization_alias="performanceGrade")
    competency_grade: str = Field(serialization_alias="competencyGrade")
    comment: Optional[EvalComment] = Field(None, serialization_alias="comment")
    leadership_surveys: list[LeadershipSurvey] = Field(default_factory=list, serialization_alias="leadershipSurveys")


class EmployeeEvaluation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    employee_id: str = Field(serialization_alias="employeeId")
    last_modified: str = Field(serialization_alias="lastModified")
    evaluations: list[EvaluationYear] = Field(default_factory=list, serialization_alias="evaluations")


# --- 응답 envelope ---

class EmployeeBasicListResponse(BaseModel):
    data: list[EmployeeBasic]
    count: int

    model_config = ConfigDict(populate_by_name=True)


class EmployeeBasicSingleResponse(BaseModel):
    data: Optional[EmployeeBasic] = None
    error: Optional[str] = None


class EmployeeListResponse(BaseModel):
    data: list[Employee]
    count: int
    delta_from: Optional[str] = Field(None, serialization_alias="deltaFrom")

    model_config = ConfigDict(populate_by_name=True)


class EmployeeSingleResponse(BaseModel):
    data: Optional[Employee] = None
    error: Optional[str] = None


class EvaluationListResponse(BaseModel):
    data: list[EmployeeEvaluation]
    count: int
    delta_from: Optional[str] = Field(None, serialization_alias="deltaFrom")

    model_config = ConfigDict(populate_by_name=True)


class EvaluationSingleResponse(BaseModel):
    data: Optional[EmployeeEvaluation] = None
    error: Optional[str] = None


# --- 개별 리소스 응답 envelope ---

class SubResourceListResponse(BaseModel):
    """개별 하위 리소스 목록 응답 (교육/경력/해외경험/가족/자격)"""
    data: list
    count: int

    model_config = ConfigDict(populate_by_name=True)


class EducationListResponse(BaseModel):
    data: list[EducationWithEmployee]
    count: int

    model_config = ConfigDict(populate_by_name=True)


class CareerListResponse(BaseModel):
    data: list[CareerWithEmployee]
    count: int

    model_config = ConfigDict(populate_by_name=True)


class OverseasExpListResponse(BaseModel):
    data: list[OverseasExpWithEmployee]
    count: int

    model_config = ConfigDict(populate_by_name=True)


class FamilyListResponse(BaseModel):
    data: list[FamilyWithEmployee]
    count: int

    model_config = ConfigDict(populate_by_name=True)


class CertificationListResponse(BaseModel):
    data: list[CertificationWithEmployee]
    count: int

    model_config = ConfigDict(populate_by_name=True)
