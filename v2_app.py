"""
v2 FastAPI Sub-Application — 평탄화(Flattened) API
모든 nested 데이터를 문자열로 평탄화하여 Power Automate 전처리 불필요
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import db
from v2_models import EmployeeFlatV2Response, EvaluationFlatV2Response
from v2_flatten import flatten_employee, flatten_evaluation

v2_app = FastAPI(
    title="Mock HR API v2",
    description="HR 데이터 API v2 — Copilot Studio / Power Automate용",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

v2_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@v2_app.get(
    "/inhr/employees/{employee_id}",
    response_model=EmployeeFlatV2Response,
    response_model_by_alias=True,
    summary="특정 임직원 인적정보 조회",
    description="기본정보 + 학력/경력/해외경험/가족/자격 포함",
    tags=["v2 inHR - 인적정보"],
)
def get_employee_flat(employee_id: str):
    """사번으로 특정 임직원의 평탄화된 전체정보 조회"""
    emp = db.get_employee_by_id(employee_id)
    if emp is None:
        return EmployeeFlatV2Response(error=f"Employee {employee_id} not found")
    return EmployeeFlatV2Response(data=flatten_employee(emp))


@v2_app.get(
    "/myhr/evaluations/{employee_id}",
    response_model=EvaluationFlatV2Response,
    response_model_by_alias=True,
    summary="특정 임직원 평가정보 조회",
    description="최근 3년치 평가/리더십 데이터 조회",
    tags=["v2 myHR - 평가정보"],
)
def get_evaluation_flat(employee_id: str):
    """사번으로 특정 임직원의 평탄화된 평가 데이터 조회"""
    ev = db.get_evaluation_by_employee(employee_id)
    if ev is None:
        return EvaluationFlatV2Response(error=f"Evaluation data for {employee_id} not found")
    return EvaluationFlatV2Response(data=flatten_evaluation(ev))
