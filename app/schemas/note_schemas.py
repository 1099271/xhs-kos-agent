from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class XhsNoteItem(BaseModel):
    note_id: str
    note_url: Optional[str] = None
    note_xsec_token: Optional[str] = None
    author_user_id: Optional[str] = Field(default=None, alias="auther_user_id")
    author_nick_name: Optional[str] = Field(default=None, alias="auther_nick_name")
    author_avatar: Optional[str] = Field(default=None, alias="auther_avatar")
    author_home_page_url: Optional[str] = Field(
        default=None, alias="auther_home_page_url"
    )
    note_display_title: Optional[str] = None
    note_cover_url_pre: Optional[str] = None
    note_cover_url_default: Optional[str] = None
    note_cover_width: Optional[str] = None
    note_cover_height: Optional[str] = None
    note_liked_count: Optional[str] = None
    note_liked: Optional[bool] = None
    note_card_type: Optional[str] = None
    note_model_type: Optional[str] = None

    model_config = {"from_attributes": True}


class XhsSearchResponse(BaseModel):
    data: List[XhsNoteItem]
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class SearchNoteRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsSearchResponse


class XhsNoteDetailItem(BaseModel):
    note_last_update_time: Optional[str] = None
    note_model_type: Optional[str] = None
    video_h266_url: Optional[str] = None
    author_avatar: Optional[str] = Field(default=None, alias="auther_avatar")
    note_card_type: Optional[str] = None
    note_desc: Optional[str] = None
    comment_count: Optional[str] = None
    note_liked_count: Optional[str] = None
    share_count: Optional[str] = None
    video_a1_url: Optional[str] = None
    author_home_page_url: Optional[str] = Field(
        default=None, alias="auther_home_page_url"
    )
    author_user_id: Optional[str] = Field(default=None, alias="auther_user_id")
    collected_count: Optional[str] = None
    note_url: Optional[str] = None
    video_id: Optional[str] = None
    note_create_time: Optional[str] = None
    note_display_title: Optional[str] = None
    note_image_list: Optional[List[str]] = None
    note_tags: Optional[List[str]] = None
    video_h264_url: Optional[str] = None
    video_h265_url: Optional[str] = None
    author_nick_name: Optional[str] = Field(default=None, alias="auther_nick_name")
    note_duration: Optional[str] = None
    note_id: str
    note_xsec_token: Optional[str] = None
    note_liked: Optional[bool] = None
    collected: Optional[bool] = None
    note_cover_url_pre: Optional[str] = None
    note_cover_url_default: Optional[str] = None
    note_cover_width: Optional[str] = None
    note_cover_height: Optional[str] = None

    model_config = {"from_attributes": True}


class XhsNoteDetailData(BaseModel):
    note: XhsNoteDetailItem

    model_config = {"from_attributes": True}


class XhsNoteDetailResponse(BaseModel):
    data: XhsNoteDetailData
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class NoteDetailRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsNoteDetailResponse
