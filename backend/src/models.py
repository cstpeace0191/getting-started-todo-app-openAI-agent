import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

# AI 자동 분류 값 (DB/API 에는 영문 코드로 저장하고, 화면에서 한글로 표시)
#   category: study(학업) / work(업무) / personal(개인)
#   priority: high(높음) / medium(보통) / low(낮음)
Category = Literal["study", "work", "personal"]
Priority = Literal["high", "medium", "low"]


def valid_date(value: Optional[str]) -> Optional[str]:
    """YYYY-MM-DD 형식의 실제 존재하는 날짜면 그대로, 아니면 None"""
    if not value:
        return None
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return None
    return value if len(value) == 10 else None


def valid_time(value: Optional[str]) -> Optional[str]:
    """HH:MM (24시간) 형식이면 그대로, 아니면 None"""
    if not value or len(value) != 5:
        return None
    try:
        datetime.time.fromisoformat(value)
    except ValueError:
        return None
    return value


def _check_date(value: Optional[str], allow_empty: bool = False) -> Optional[str]:
    if value is None or (allow_empty and value == ""):
        return value
    if valid_date(value) is None:
        raise ValueError("date must be a valid YYYY-MM-DD date")
    return value


def _check_time(value: Optional[str], allow_empty: bool = False) -> Optional[str]:
    if value is None or (allow_empty and value == ""):
        return value
    if valid_time(value) is None:
        raise ValueError("time must be HH:MM (24-hour)")
    return value


class Item(BaseModel):
    id: str
    name: str
    completed: bool = False
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    # 등록(Register) 여부: True 면 작업 목록에서 숨겨지고 검색 대상이 된다
    registered: bool = False
    # 일정: 기한 날짜(YYYY-MM-DD)와 선택적 시간(HH:MM)
    due_date: Optional[str] = None
    due_time: Optional[str] = None


class BulkDelete(BaseModel):
    """여러 항목 일괄 삭제 요청"""

    ids: List[str] = Field(..., min_length=1, max_length=1000)


class BulkDeleteResult(BaseModel):
    deleted: int


class CategoryCount(BaseModel):
    category: Category
    count: int


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    # 사용자가 직접 지정한 일정 (지정하면 AI 가 추출한 날짜보다 우선한다)
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    # 클라이언트 기준 오늘 날짜 (AI 가 '내일', '토요일' 등을 날짜로 바꿀 때 사용)
    today: Optional[str] = None

    @field_validator("due_date", "today")
    @classmethod
    def _date(cls, v):
        return _check_date(v)

    @field_validator("due_time")
    @classmethod
    def _time(cls, v):
        return _check_time(v)


class ItemUpdate(BaseModel):
    # 값이 있으면 비어 있을 수 없고 DB 컬럼(VARCHAR(255)) 길이를 넘을 수 없다
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    completed: Optional[bool] = None
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    registered: Optional[bool] = None
    # None: 변경 없음 / "": 일정 삭제 / 값: 변경
    due_date: Optional[str] = None
    due_time: Optional[str] = None

    @field_validator("name")
    @classmethod
    def _name(cls, v):
        # 앞뒤 공백을 제거하고, 공백만 있는 이름은 거절한다
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v

    @field_validator("due_date")
    @classmethod
    def _date(cls, v):
        return _check_date(v, allow_empty=True)

    @field_validator("due_time")
    @classmethod
    def _time(cls, v):
        return _check_time(v, allow_empty=True)


class Classification(BaseModel):
    """OpenAI 에이전트(Agents SDK)가 반환하는 구조화된 분류 결과"""

    category: Category
    priority: Priority
    # 문장에서 추출한 일정 (없으면 null). 형식 검증은 classifier 에서 한다.
    due_date: Optional[str] = Field(
        default=None, description="YYYY-MM-DD. 날짜 표현이 없으면 null"
    )
    due_time: Optional[str] = Field(
        default=None, description="24시간 HH:MM. 시간 표현이 없으면 null"
    )


class BriefingRequest(BaseModel):
    # 클라이언트 기준 오늘 날짜 (없으면 서버 오늘)
    today: Optional[str] = None

    @field_validator("today")
    @classmethod
    def _today(cls, v):
        return _check_date(v)


class FocusItem(BaseModel):
    item_id: str = Field(description="추천하는 할 일의 id (도구로 조회한 값 그대로)")
    name: str
    reason: str = Field(description="왜 먼저 해야 하는지 한 문장")


class Briefing(BaseModel):
    """일정 브리핑 에이전트가 돌려주는 구조화된 결과"""

    summary: str = Field(description="오늘 상황 2~3문장 요약")
    focus: List[FocusItem] = Field(description="오늘 우선 처리할 항목, 최대 5개, 우선순위 순")
    warnings: List[str] = Field(description="기한 초과·일정 겹침·과부하 등 주의사항")
    tips: List[str] = Field(description="실행 가능한 짧은 조언, 최대 3개")


class GreetingResponse(BaseModel):
    greeting: str
