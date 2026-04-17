"""
===============================================================
 Mock HR API Server — HR Data 원큐 Agent 프로토타입용
===============================================================
 FastAPI 기반 Mock inHR / myHR REST API
 - SQLite DB에서 데이터 조회 (data/hr_data.db)
 - Delta Sync 지원 (modifiedAfter 파라미터)
 - Swagger UI 자동 생성 → Custom Connector에 바로 활용

 사전 준비: python import_data.py  (Excel → SQLite)
 실행: uvicorn mock_hr_api:app --host 0.0.0.0 --port 8000
 Swagger: http://localhost:8000/docs
 OpenAPI JSON: http://localhost:8000/openapi.json
===============================================================
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime, timezone

import db
from models import (
    EmployeeListResponse, EmployeeSingleResponse,
    EvaluationListResponse, EvaluationSingleResponse,
    EducationListResponse, CareerListResponse,
    OverseasExpListResponse, FamilyListResponse, CertificationListResponse,
)

# ============================================================
# FastAPI 앱 설정
# ============================================================
app = FastAPI(
    title="Mock HR API",
    description="SK케미칼 HR Data 원큐 Agent 프로토타입용 Mock 인사 시스템 API",
    version="2.0.0",
    servers=[
        {"url": "http://localhost:8000", "description": "로컬 개발"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Startup 체크
# ============================================================
@app.on_event("startup")
def startup_check():
    if not db.db_exists():
        print("=" * 60)
        print("  [WARNING] data/hr_data.db 파일이 없습니다!")
        print("  먼저 다음 명령을 실행하세요: python import_data.py")
        print("=" * 60)


# ============================================================
# API 엔드포인트
# ============================================================

# ---- inHR API: 기본 인적정보 ----

@app.get(
    "/api/v1/inhr/employees",
    response_model=EmployeeListResponse,
    response_model_by_alias=True,
    summary="전체 임직원 기본정보 조회 (Delta 지원)",
    description="modifiedAfter 파라미터로 특정 시각 이후 변경된 임직원만 필터링 가능",
    tags=["inHR - 기본인적정보"],
)
def get_employees(
    modifiedAfter: Optional[str] = Query(
        None,
        description="ISO 8601 형식. 이 시각 이후 변경된 데이터만 반환 (예: 2026-04-16T00:00:00Z)",
    )
):
    """기본 인적정보 + 학력/경력/해외경험/가족/자격 포함"""
    employees = db.get_all_employees(modified_after=modifiedAfter)
    return EmployeeListResponse(data=employees, count=len(employees), delta_from=modifiedAfter)


@app.get(
    "/api/v1/inhr/employees/{employee_id}",
    response_model=EmployeeSingleResponse,
    response_model_by_alias=True,
    summary="특정 임직원 기본정보 조회",
    tags=["inHR - 기본인적정보"],
)
def get_employee_by_id(employee_id: str):
    """사번으로 특정 임직원 조회"""
    emp = db.get_employee_by_id(employee_id)
    if emp is None:
        return EmployeeSingleResponse(error=f"Employee {employee_id} not found")
    return EmployeeSingleResponse(data=emp)


# ---- inHR API: 학력 ----

@app.get(
    "/api/v1/inhr/educations",
    response_model=EducationListResponse,
    response_model_by_alias=True,
    summary="전체 임직원 학력 조회",
    tags=["inHR - 학력"],
)
def get_educations_all():
    """전체 임직원의 학력 정보"""
    rows = db.get_all_educations()
    return EducationListResponse(data=rows, count=len(rows))


@app.get(
    "/api/v1/inhr/educations/{employee_id}",
    response_model=EducationListResponse,
    response_model_by_alias=True,
    summary="특정 임직원 학력 조회",
    tags=["inHR - 학력"],
)
def get_educations_by_employee(employee_id: str):
    """사번으로 특정 임직원 학력 조회"""
    rows = db.get_educations_by_employee(employee_id)
    return EducationListResponse(data=rows, count=len(rows))


# ---- inHR API: 경력 ----

@app.get(
    "/api/v1/inhr/careers",
    response_model=CareerListResponse,
    response_model_by_alias=True,
    summary="전체 임직원 경력 조회",
    tags=["inHR - 경력"],
)
def get_careers_all():
    """전체 임직원의 경력 정보"""
    rows = db.get_all_careers()
    return CareerListResponse(data=rows, count=len(rows))


@app.get(
    "/api/v1/inhr/careers/{employee_id}",
    response_model=CareerListResponse,
    response_model_by_alias=True,
    summary="특정 임직원 경력 조회",
    tags=["inHR - 경력"],
)
def get_careers_by_employee(employee_id: str):
    """사번으로 특정 임직원 경력 조회"""
    rows = db.get_careers_by_employee(employee_id)
    return CareerListResponse(data=rows, count=len(rows))


# ---- inHR API: 해외경험 ----

@app.get(
    "/api/v1/inhr/overseas",
    response_model=OverseasExpListResponse,
    response_model_by_alias=True,
    summary="전체 임직원 해외경험 조회",
    tags=["inHR - 해외경험"],
)
def get_overseas_all():
    """전체 임직원의 해외경험 정보"""
    rows = db.get_all_overseas()
    return OverseasExpListResponse(data=rows, count=len(rows))


@app.get(
    "/api/v1/inhr/overseas/{employee_id}",
    response_model=OverseasExpListResponse,
    response_model_by_alias=True,
    summary="특정 임직원 해외경험 조회",
    tags=["inHR - 해외경험"],
)
def get_overseas_by_employee(employee_id: str):
    """사번으로 특정 임직원 해외경험 조회"""
    rows = db.get_overseas_by_employee(employee_id)
    return OverseasExpListResponse(data=rows, count=len(rows))


# ---- inHR API: 가족사항 ----

@app.get(
    "/api/v1/inhr/family",
    response_model=FamilyListResponse,
    response_model_by_alias=True,
    summary="전체 임직원 가족사항 조회",
    tags=["inHR - 가족사항"],
)
def get_family_all():
    """전체 임직원의 가족사항 정보"""
    rows = db.get_all_family()
    return FamilyListResponse(data=rows, count=len(rows))


@app.get(
    "/api/v1/inhr/family/{employee_id}",
    response_model=FamilyListResponse,
    response_model_by_alias=True,
    summary="특정 임직원 가족사항 조회",
    tags=["inHR - 가족사항"],
)
def get_family_by_employee(employee_id: str):
    """사번으로 특정 임직원 가족사항 조회"""
    rows = db.get_family_by_employee(employee_id)
    return FamilyListResponse(data=rows, count=len(rows))


# ---- inHR API: 자격/어학 ----

@app.get(
    "/api/v1/inhr/certifications",
    response_model=CertificationListResponse,
    response_model_by_alias=True,
    summary="전체 임직원 자격/어학 조회",
    tags=["inHR - 자격/어학"],
)
def get_certifications_all():
    """전체 임직원의 자격/어학 정보"""
    rows = db.get_all_certifications()
    return CertificationListResponse(data=rows, count=len(rows))


@app.get(
    "/api/v1/inhr/certifications/{employee_id}",
    response_model=CertificationListResponse,
    response_model_by_alias=True,
    summary="특정 임직원 자격/어학 조회",
    tags=["inHR - 자격/어학"],
)
def get_certifications_by_employee(employee_id: str):
    """사번으로 특정 임직원 자격/어학 조회"""
    rows = db.get_certifications_by_employee(employee_id)
    return CertificationListResponse(data=rows, count=len(rows))


# ---- myHR API: 평가/리더십 ----

@app.get(
    "/api/v1/myhr/evaluations",
    response_model=EvaluationListResponse,
    response_model_by_alias=True,
    summary="전체 임직원 평가/리더십 데이터 조회 (Delta 지원)",
    description="modifiedAfter 파라미터로 특정 시각 이후 변경된 데이터만 필터링 가능",
    tags=["myHR - 평가/리더십"],
)
def get_evaluations(
    modifiedAfter: Optional[str] = Query(
        None,
        description="ISO 8601 형식. 이 시각 이후 변경된 데이터만 반환",
    )
):
    """평가 등급 + 코멘트 + 리더십 서베이 포함"""
    evals = db.get_all_evaluations(modified_after=modifiedAfter)
    return EvaluationListResponse(data=evals, count=len(evals), delta_from=modifiedAfter)


@app.get(
    "/api/v1/myhr/evaluations/{employee_id}",
    response_model=EvaluationSingleResponse,
    response_model_by_alias=True,
    summary="특정 임직원 평가/리더십 데이터 조회",
    tags=["myHR - 평가/리더십"],
)
def get_evaluation_by_id(employee_id: str):
    """사번으로 특정 임직원 평가 데이터 조회"""
    ev = db.get_evaluation_by_employee(employee_id)
    if ev is None:
        return EvaluationSingleResponse(error=f"Evaluation data for {employee_id} not found")
    return EvaluationSingleResponse(data=ev)


# ---- 유틸리티 ----

@app.get(
    "/api/v1/health",
    summary="서버 상태 확인",
    tags=["유틸리티"],
)
def health_check():
    stats = db.get_stats() if db.db_exists() else {}
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "employeeCount": stats.get("employees", 0),
        "version": "2.0.0",
        "dbExists": db.db_exists(),
    }


@app.get(
    "/api/v1/stats",
    summary="데이터 통계",
    tags=["유틸리티"],
)
def get_stats():
    if not db.db_exists():
        return {"error": "DB not found. Run: python import_data.py"}
    return db.get_stats()


# ============================================================
# 직접 실행 시
# ============================================================
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("  Mock HR API Server 시작 (v2.0 — SQLite)")
    print("  Swagger UI: http://localhost:8000/docs")
    print("  OpenAPI JSON: http://localhost:8000/openapi.json")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
