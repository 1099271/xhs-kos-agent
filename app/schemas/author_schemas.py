from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict

from app.schemas.note_schemas import XhsNoteItem


class XhsAuthorInfo(BaseModel):
    user_link_url: Optional[str] = None
    desc: Optional[str] = None
    interaction: Optional[str] = None
    ip_location: Optional[str] = None
    red_id: Optional[str] = None
    user_id: str
    tags: Optional[List[str]] = None
    avatar: Optional[str] = None
    fans: Optional[str] = None
    follows: Optional[str] = None
    gender: Optional[str] = None
    nick_name: Optional[str] = None

    model_config = {"from_attributes": True}


class XhsAuthorNotesData(BaseModel):
    notes: List[XhsNoteItem]
    author_info: XhsAuthorInfo
    cursor: Optional[str] = None
    has_more: Optional[bool] = False

    model_config = {"from_attributes": True}


class XhsAuthorNotesResponse(BaseModel):
    data: XhsAuthorNotesData
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class authorNotesRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsAuthorNotesResponse
