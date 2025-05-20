from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class XhsCommentAtUserItem(BaseModel):
    at_user_id: str
    at_user_nickname: Optional[str] = None
    at_user_home_page_url: Optional[str] = None

    model_config = {"from_attributes": True}


class XhsCommentSubItem(BaseModel):
    comment_id: str
    note_id: str
    comment_user_id: str
    comment_user_nickname: Optional[str] = None
    comment_user_image: Optional[str] = None
    comment_user_home_page_url: Optional[str] = None
    comment_content: Optional[str] = None
    comment_like_count: Optional[str] = None
    comment_sub_comment_count: Optional[str] = None
    comment_create_time: Optional[str] = None
    comment_liked: Optional[bool] = False
    comment_show_tags: Optional[List[str]] = None
    comment_sub_comment_cursor: Optional[str] = None
    comment_sub_comment_has_more: Optional[bool] = False
    comment_at_users: Optional[List[XhsCommentAtUserItem]] = Field(default_factory=list)
    comment_sub: Optional[List["XhsCommentSubItem"]] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class XhsCommentItem(BaseModel):
    comment_id: str
    note_id: str
    comment_user_id: str
    comment_user_nickname: Optional[str] = None
    comment_user_image: Optional[str] = None
    comment_user_home_page_url: Optional[str] = None
    comment_content: Optional[str] = None
    comment_like_count: Optional[str] = None
    comment_sub_comment_count: Optional[str] = None
    comment_create_time: Optional[str] = None
    comment_liked: Optional[bool] = False
    comment_show_tags: Optional[List[str]] = None
    comment_sub_comment_cursor: Optional[str] = None
    comment_sub_comment_has_more: Optional[bool] = False
    comment_at_users: Optional[List[XhsCommentAtUserItem]] = Field(default_factory=list)
    comment_sub: Optional[List[XhsCommentSubItem]] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class XhsCommentsData(BaseModel):
    comments: List[XhsCommentItem]
    cursor: Optional[str] = None
    has_more: Optional[bool] = False

    model_config = {"from_attributes": True}


class XhsCommentsResponse(BaseModel):
    data: XhsCommentsData
    msg: str = ""
    tips: Optional[str] = None
    code: int = 0

    model_config = {"from_attributes": True}


class CommentsRequest(BaseModel):
    req_info: Dict[str, Any]
    req_body: XhsCommentsResponse
