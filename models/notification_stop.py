import datetime
from typing import Optional

from pydantic import BaseModel

from models.attachment import AttachmentModel
from models.common import CodeNameModel, DocModel, SignedDataModel


class NoticeStopCommonInfoModel(BaseModel):
    noticeNumber: str
    lotNumber: int
    publishDate: datetime.datetime
    href: str


class NoticeStopModel(BaseModel):
    schemeVersion: str
    id: str
    commonInfo: NoticeStopCommonInfoModel
    stopReason: CodeNameModel
    decisionDate: datetime.date
    addInfo: str
    timezone: CodeNameModel
    signedData: SignedDataModel
    docs: Optional[list[DocModel]] = []
    attachments: list[AttachmentModel] = []
