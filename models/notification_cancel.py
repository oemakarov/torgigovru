import datetime
from typing import Optional

from pydantic import BaseModel

from models.common import CodeNameModel, DocModel, SignedDataModel


class NoticeCancelCommonInfoModel(BaseModel):
    noticeNumber: str
    publishDate: datetime.datetime
    href: str


class NoticeCancelModel(BaseModel):
    schemeVersion: str
    id: str
    commonInfo: NoticeCancelCommonInfoModel
    cancelReason: CodeNameModel
    decisionDate: datetime.date
    timezone: CodeNameModel
    signedData: SignedDataModel
    docs: Optional[list[DocModel]] = []

