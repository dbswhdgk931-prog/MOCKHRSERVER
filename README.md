# Mock HR API Server

SK케미칼 HR Data 원큐 Agent 프로토타입용 Mock 인사 시스템 API.
`data/` 폴더의 9개 엑셀 파일을 SQLite DB로 import하고, FastAPI로 JSON 제공.

## 빠른 시작

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. Excel → SQLite import
python import_data.py

# 3. 서버 실행
python mock_hr_api.py
```

서버 실행 후:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 프로젝트 구조

```
MockHRServer/
  mock_hr_api.py      # FastAPI 서버 (엔드포인트 정의)
  models.py            # Pydantic 응답 모델 (OpenAPI 스키마)
  db.py                # SQLite 쿼리 함수
  import_data.py       # Excel → SQLite import 스크립트
  test_api.py          # 전체 API 테스트 스크립트
  requirements.txt     # Python 패키지 목록
  data/
    01_Employee.xlsx ~ 09_LeadershipSurvey.xlsx   # 원본 데이터
    hr_data.db         # import 후 생성 (gitignore)
```

## 엑셀 데이터 재import

엑셀 파일 수정 후 아래 명령만 실행하면 DB가 재생성됩니다.
서버 재시작 불필요 (요청마다 DB 연결을 새로 생성).

```bash
python import_data.py
```

## API 엔드포인트

### inHR — 기본 인적정보

#### `GET /api/v1/inhr/employees`

전체 임직원 기본정보 조회. 교육/경력/해외경험/가족/자격 nested 포함.

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `modifiedAfter` | string (optional) | ISO 8601 형식. 이 시각 이후 변경된 데이터만 반환 |

**응답 예시:**
```json
{
  "data": [
    {
      "employeeId": "EMP001",
      "name": "김철수",
      "birthDate": "1985-03-15",
      "department": "People Development팀",
      "position": "매니저",
      "grade": "M2",
      "tenure": 12,
      "promotionDate": "2022-01-01",
      "photoUrl": "https://sp.example.com/photos/emp001.jpg",
      "managerId": "EMP010",
      "lastModified": "2026-04-17T06:00:30Z",
      "educations": [
        { "school": "서울대학교", "degree": "학사", "major": "경영학", "gradYear": 2007 }
      ],
      "careers": [
        {
          "company": "SK케미칼", "department": "인사팀", "role": "인사기획 담당",
          "startDate": "2013-03-01", "endDate": "2016-12-31",
          "region": "", "description": "채용/교육/평가 제도 운영", "isCurrent": false
        }
      ],
      "overseasExperiences": [
        { "country": "미국", "purpose": "Stanford HR Leaders Program 수료", "startDate": "2018-06-01", "endDate": "2018-08-31" }
      ],
      "family": [
        { "relation": "배우자", "name": "이수진", "birthYear": 1987, "education": "이화여대 영문학 학사", "occupation": "OO출판사 편집자" }
      ],
      "certifications": [
        { "certName": "TOEIC", "issuer": "ETS", "country": "미국", "scoreOrGrade": "950", "issuedDate": "2024-03-15", "expiryDate": "2026-03-14" }
      ]
    }
  ],
  "count": 10,
  "deltaFrom": null
}
```

Delta Sync 예시:
```
GET /api/v1/inhr/employees?modifiedAfter=2026-04-17T00:00:00Z
```

---

#### `GET /api/v1/inhr/employees/{employee_id}`

특정 임직원 기본정보 조회.

**응답 예시:**
```json
{
  "data": { "employeeId": "EMP001", "name": "김철수", ... },
  "error": null
}
```

직원이 없을 경우:
```json
{
  "data": null,
  "error": "Employee EMP999 not found"
}
```

---

### inHR — 학력 (개별 조회)

#### `GET /api/v1/inhr/educations`

전체 임직원 학력 조회. 각 레코드에 `employeeId` 포함.

**응답 예시:**
```json
{
  "data": [
    { "employeeId": "EMP001", "school": "서울대학교", "degree": "학사", "major": "경영학", "gradYear": 2007 },
    { "employeeId": "EMP001", "school": "서울대학교", "degree": "석사", "major": "경영학(인사조직)", "gradYear": 2009 }
  ],
  "count": 19
}
```

#### `GET /api/v1/inhr/educations/{employee_id}`

특정 임직원 학력 조회.

---

### inHR — 경력 (개별 조회)

#### `GET /api/v1/inhr/careers`

전체 임직원 경력 조회. `endDate`가 null이면 `isCurrent: true`.

**응답 예시:**
```json
{
  "data": [
    {
      "employeeId": "EMP001", "company": "SK케미칼", "department": "인사팀",
      "role": "인사기획 담당", "startDate": "2013-03-01", "endDate": "2016-12-31",
      "region": "", "description": "채용/교육/평가 제도 운영", "isCurrent": false
    }
  ],
  "count": 23
}
```

#### `GET /api/v1/inhr/careers/{employee_id}`

특정 임직원 경력 조회.

---

### inHR — 해외경험 (개별 조회)

#### `GET /api/v1/inhr/overseas`

전체 임직원 해외경험 조회.

**응답 예시:**
```json
{
  "data": [
    { "employeeId": "EMP001", "country": "미국", "purpose": "Stanford HR Leaders Program 수료", "startDate": "2018-06-01", "endDate": "2018-08-31" }
  ],
  "count": 7
}
```

#### `GET /api/v1/inhr/overseas/{employee_id}`

특정 임직원 해외경험 조회.

---

### inHR — 가족사항 (개별 조회)

#### `GET /api/v1/inhr/family`

전체 임직원 가족사항 조회. DB의 `FinalEducation` 컬럼은 `education` 키로 출력.

**응답 예시:**
```json
{
  "data": [
    { "employeeId": "EMP001", "relation": "배우자", "name": "이수진", "birthYear": 1987, "education": "이화여대 영문학 학사", "occupation": "OO출판사 편집자" }
  ],
  "count": 20
}
```

#### `GET /api/v1/inhr/family/{employee_id}`

특정 임직원 가족사항 조회.

---

### inHR — 자격/어학 (개별 조회)

#### `GET /api/v1/inhr/certifications`

전체 임직원 자격/어학 조회.

**응답 예시:**
```json
{
  "data": [
    { "employeeId": "EMP001", "certName": "TOEIC", "issuer": "ETS", "country": "미국", "scoreOrGrade": "950", "issuedDate": "2024-03-15", "expiryDate": "2026-03-14" }
  ],
  "count": 21
}
```

#### `GET /api/v1/inhr/certifications/{employee_id}`

특정 임직원 자격/어학 조회.

---

### myHR — 평가/리더십

#### `GET /api/v1/myhr/evaluations`

전체 임직원 평가 데이터 조회. 코멘트 + 리더십 서베이 nested 포함.

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `modifiedAfter` | string (optional) | ISO 8601 형식. 이 시각 이후 변경된 데이터만 반환 |

**응답 예시:**
```json
{
  "data": [
    {
      "employeeId": "EMP001",
      "lastModified": "2026-04-17T06:00:30Z",
      "evaluations": [
        {
          "year": 2023,
          "performanceGrade": "A",
          "competencyGrade": "A",
          "comment": {
            "type": "상사평가",
            "text": "전략적 사고력이 뛰어나며 PD 프로그램 설계 시 ...",
            "commenter": "직속상사"
          },
          "leadershipSurveys": [
            { "evaluatorType": "동료", "score": 4.1, "strengthComment": "...", "developmentComment": "..." },
            { "evaluatorType": "부하", "score": 4.3, "strengthComment": "...", "developmentComment": "..." }
          ]
        }
      ]
    }
  ],
  "count": 10,
  "deltaFrom": null
}
```

---

#### `GET /api/v1/myhr/evaluations/{employee_id}`

특정 임직원 평가 데이터 조회.

---

### 유틸리티

#### `GET /api/v1/health`

서버 상태 확인.

```json
{
  "status": "healthy",
  "timestamp": "2026-04-17T06:00:30.000000+00:00",
  "employeeCount": 10,
  "version": "2.0.0",
  "dbExists": true
}
```

---

#### `GET /api/v1/stats`

테이블별 데이터 건수.

```json
{
  "employees": 10,
  "educations": 19,
  "careers": 23,
  "overseasExperiences": 7,
  "family": 20,
  "certifications": 21,
  "evaluations": 30,
  "evalComments": 30,
  "leadershipSurveys": 60
}
```

## 엔드포인트 요약

### inHR — 기본 인적정보 (nested)

| Method | Path | 설명 | 건수 |
|---|---|---|---|
| GET | `/api/v1/inhr/employees` | 전체 직원 (교육/경력/해외/가족/자격 nested) | 10 |
| GET | `/api/v1/inhr/employees/{id}` | 특정 직원 상세 | 1 |

### inHR — 개별 리소스 조회

| Method | Path | 설명 | 건수 |
|---|---|---|---|
| GET | `/api/v1/inhr/educations` | 전체 학력 | 19 |
| GET | `/api/v1/inhr/educations/{id}` | 특정 직원 학력 | |
| GET | `/api/v1/inhr/careers` | 전체 경력 | 23 |
| GET | `/api/v1/inhr/careers/{id}` | 특정 직원 경력 | |
| GET | `/api/v1/inhr/overseas` | 전체 해외경험 | 7 |
| GET | `/api/v1/inhr/overseas/{id}` | 특정 직원 해외경험 | |
| GET | `/api/v1/inhr/family` | 전체 가족사항 | 20 |
| GET | `/api/v1/inhr/family/{id}` | 특정 직원 가족사항 | |
| GET | `/api/v1/inhr/certifications` | 전체 자격/어학 | 21 |
| GET | `/api/v1/inhr/certifications/{id}` | 특정 직원 자격/어학 | |

### myHR — 평가/리더십

| Method | Path | 설명 | 건수 |
|---|---|---|---|
| GET | `/api/v1/myhr/evaluations` | 전체 평가 (코멘트+서베이 nested) | 10 |
| GET | `/api/v1/myhr/evaluations/{id}` | 특정 직원 평가 | |

### 유틸리티

| Method | Path | 설명 |
|---|---|---|
| GET | `/api/v1/health` | 헬스체크 |
| GET | `/api/v1/stats` | 데이터 통계 |

## DB 스키마

9개 엑셀 → 9개 테이블 1:1 매핑 + import_metadata:

| 테이블 | PK | FK | 비고 |
|---|---|---|---|
| `employee` | employee_id | — | last_modified 자동 기록 |
| `education` | education_id | employee_id | |
| `career` | career_id | employee_id | EndDate null → isCurrent=true |
| `overseas_exp` | overseas_id | employee_id | |
| `family` | family_id | employee_id | FinalEducation → API에서 education 키로 출력 |
| `certification` | cert_id | employee_id | |
| `evaluation` | eval_id | employee_id | |
| `eval_comment` | comment_id | employee_id + year | |
| `leadership_survey` | survey_id | employee_id + year | |
| `import_metadata` | key | — | 마지막 import 시각 |

## 테스트

```bash
python test_api.py
```

82개 항목 자동 검증 (응답 코드, row count, camelCase 키, nested 구조, 개별 리소스 조회, Delta Sync 등).
