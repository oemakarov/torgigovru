import datetime
from typing import Optional

from pydantic import BaseModel


class BidModel(BaseModel):
    bidderOrgCode: str
    rightHolderCode: str
    documentType: str
    regNum: str
    publishDate: datetime.datetime
    biddTypeCode: str
    ownershipFormsCode: str
    subjectEstateCode: Optional[str] = None
    subjectRightHolderCode: str
    href: str


class DayListModel(BaseModel):
    listObjects: list[BidModel]

    @property
    def list(self):
        return self.listObjects

    def list_filtered(self, document_type: str):
        return [o for o in self.list if o.documentType == document_type]
