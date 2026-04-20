"""
OpenAPI 3.1 → Swagger 2.0 변환기
FastAPI가 생성하는 OpenAPI 3.1 스펙을 Copilot Studio / Power Platform
Custom Connector에서 요구하는 Swagger 2.0 형식으로 변환한다.
"""

import copy


def convert_openapi3_to_swagger2(spec, host="", base_path="/"):
    """OpenAPI 3.x 스펙을 Swagger 2.0으로 변환"""
    spec = copy.deepcopy(spec)

    swagger = {
        "swagger": "2.0",
        "info": spec.get("info", {}),
        "host": host,
        "basePath": base_path,
        "schemes": ["https", "http"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "paths": {},
        "definitions": {},
    }

    # tags 복사
    if "tags" in spec:
        swagger["tags"] = spec["tags"]

    # components/schemas → definitions
    schemas = spec.get("components", {}).get("schemas", {})
    for name, schema in schemas.items():
        swagger["definitions"][name] = _convert_schema(schema)

    # paths 변환
    for path, path_item in spec.get("paths", {}).items():
        swagger["paths"][path] = {}
        for method, operation in path_item.items():
            if method not in ("get", "post", "put", "delete", "patch", "options", "head"):
                continue
            swagger["paths"][path][method] = _convert_operation(operation)

    # $ref 경로 일괄 치환
    swagger = _fix_refs(swagger)

    return swagger


# ──────────────────────────────────────────────
# 내부 변환 함수
# ──────────────────────────────────────────────

def _convert_schema(schema):
    """OpenAPI 3.1 JSON Schema → Swagger 2.0 호환 스키마"""
    if not isinstance(schema, dict):
        return schema

    # anyOf 처리 (Pydantic v2 Optional 필드가 anyOf: [{type:X}, {type:null}] 생성)
    if "anyOf" in schema:
        non_null = [s for s in schema["anyOf"]
                    if s != {"type": "null"} and s.get("type") != "null"]
        if len(non_null) == 1:
            result = _convert_schema(non_null[0])
        elif non_null:
            result = _convert_schema(non_null[0])
        else:
            result = {"type": "string"}
        # 원본 schema의 default, title 등 보존
        for k in ("default", "title", "description"):
            if k in schema:
                result[k] = schema[k]
        return result

    result = {}
    for key, value in schema.items():
        if key == "const":
            result["enum"] = [value]
        elif key == "examples":
            if isinstance(value, list) and value:
                result["example"] = value[0]
        elif key == "items":
            result["items"] = _convert_schema(value)
        elif key == "properties":
            result["properties"] = {k: _convert_schema(v) for k, v in value.items()}
        elif key == "additionalProperties":
            result["additionalProperties"] = (
                _convert_schema(value) if isinstance(value, dict) else value
            )
        elif key == "allOf":
            result["allOf"] = [_convert_schema(s) for s in value]
        elif key == "oneOf":
            # Swagger 2.0에는 oneOf 없음 → 첫 번째 것 사용
            non_null = [s for s in value if s.get("type") != "null"]
            if non_null:
                result.update(_convert_schema(non_null[0]))
            elif value:
                result.update(_convert_schema(value[0]))
        else:
            result[key] = value

    # Swagger 2.0 / Power Platform: integer·number에 format 필수
    _type = result.get("type")
    if _type == "integer" and "format" not in result:
        result["format"] = "int32"
    elif _type == "number" and "format" not in result:
        result["format"] = "double"

    return result


def _convert_operation(operation):
    """OpenAPI 3.x operation → Swagger 2.0 operation"""
    result = {"responses": {}}

    for key in ("summary", "description", "operationId", "tags"):
        if key in operation:
            result[key] = operation[key]

    # parameters 변환
    if "parameters" in operation:
        result["parameters"] = []
        for param in operation["parameters"]:
            new_param = {
                "name": param["name"],
                "in": param["in"],
                "required": param.get("required", False),
            }
            if "description" in param:
                new_param["description"] = param["description"]

            if "schema" in param:
                schema = param["schema"]
                # anyOf 처리 (Optional query params)
                if "anyOf" in schema:
                    non_null = [s for s in schema["anyOf"]
                                if s.get("type") != "null"]
                    schema = non_null[0] if non_null else {"type": "string"}

                new_param["type"] = schema.get("type", "string")
                if "default" in schema:
                    new_param["default"] = schema["default"]
                if "enum" in schema:
                    new_param["enum"] = schema["enum"]
                if "format" in schema:
                    new_param["format"] = schema["format"]

            result["parameters"].append(new_param)

    # responses 변환
    for status, response in operation.get("responses", {}).items():
        new_response = {"description": response.get("description", "")}
        if "content" in response:
            for _content_type, content in response["content"].items():
                if "schema" in content:
                    new_response["schema"] = _convert_schema(content["schema"])
                break
        result["responses"][status] = new_response

    return result


def _fix_refs(obj):
    """$ref 경로를 #/components/schemas/ → #/definitions/ 로 치환"""
    if isinstance(obj, dict):
        return {
            k: (v.replace("#/components/schemas/", "#/definitions/")
                if k == "$ref" and isinstance(v, str)
                else _fix_refs(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_fix_refs(item) for item in obj]
    return obj
