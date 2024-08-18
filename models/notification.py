import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel

import config
from models.attachment import AttachmentModel
from models.common import CodeNameModel, CodeNameValueModel, DocModel, SignedDataModel
from models.lot import LotModel
from models.notification_cancel import NoticeCancelModel
from models.notification_stop import NoticeStopModel


class CommonInfoModel(BaseModel):
    noticeNumber: str
    biddType: CodeNameModel
    biddForm: CodeNameModel
    publishDate: datetime.datetime
    procedureName: str
    etp: Optional[CodeNameModel] = None
    href: str


class OrgInfoModel(BaseModel):
    code: str
    name: str
    INN: str
    KPP: Optional[str] = None
    OGRN: str
    orgType: str
    legalAddress: str
    actualAddress: str


class ContactInfoModel(BaseModel):
    contPerson: str
    tel: str
    email: str


class BidderOrgModel(BaseModel):
    orgInfo: OrgInfoModel
    contactInfo: ContactInfoModel


class RightHolderOrgModel(BaseModel):
    code: str
    name: str
    INN: str
    KPP: str
    OGRN: str
    orgType: str
    legalAddress: str
    actualAddress: str


class RightHolderInfoModel(BaseModel):
    biddOrgRightHolder: bool
    rightHolderOrg: RightHolderOrgModel


class BiddConditionsModel(BaseModel):
    biddStartTime: datetime.datetime
    biddEndTime: datetime.datetime
    biddReviewDate: Optional[datetime.date] = None
    startDate: Optional[datetime.datetime] = None


class ChangeInfoModel(BaseModel):
    changeReasonText: Optional[str] = None
    changeReasonRef: CodeNameModel


class NoticeModel(BaseModel):
    schemeVersion: str
    id: str
    rootId: str
    version: int
    commonInfo: CommonInfoModel
    bidderOrg: BidderOrgModel
    rightHolderInfo: RightHolderInfoModel
    lots: list[LotModel] = []
    biddConditions: BiddConditionsModel
    changeInfo: Optional[ChangeInfoModel] = None
    timeZone: CodeNameModel
    additionalDetails: Optional[list[CodeNameValueModel]] = None
    signedData: SignedDataModel
    docs: Optional[list[DocModel]] = []

    @property
    def number(self) -> str:
        return self.commonInfo.noticeNumber

    @property
    def link(self) -> str:
        return f'{config.URL_NOTICE_LINK}{self.commonInfo.noticeNumber}'

    @property
    def procedure_name(self) -> str:
        return self.commonInfo.procedureName

    @property
    def bidd_end_time(self) -> datetime.datetime:
        return self.biddConditions.biddEndTime

    def lot_link(self, lot_num: int) -> Optional[str]:
        if 1 <= lot_num <= len(self.lots):
            return f'{config.URL_LOT_LINK}{self.number}_{lot_num}'
        raise ValueError(f'lot number {lot_num} is out of range')


class StructuredObjectModel(BaseModel):
    notice: Optional[NoticeModel] = None
    noticeCancel: Optional[NoticeCancelModel] = None
    noticeStop: Optional[NoticeStopModel] = None


class ExportObjectModel(BaseModel):
    structuredObject: StructuredObjectModel
    attachments: list[AttachmentModel] = []


class NotificationModel(BaseModel):
    exportObject: ExportObjectModel

    @property
    def notice(self) -> NoticeModel:
        return self.exportObject.structuredObject.notice

    @property
    def attachments(self) -> Optional[list[AttachmentModel]]:
        return self.exportObject.attachments
