# from datetime import date, datetime

import datetime
from typing import Any, Optional, Union

import requests
from pydantic import BaseModel

import config


class AttachmentMethods:
    def attachment_content(self, content_id: str, **kwargs):
        response = requests.get(config.URL_FILESTORE + content_id, verify=False, **kwargs)
        content_filename = requests.utils.unquote(
            list(
                filter(
                    lambda x: x.startswith('filename'),
                    response.headers.get('Content-Disposition', '').split('; '),
                )
            )[0].split("''")[1]
        )
        if response.content:
            return content_filename, response.content
        else:
            return None, None

    def attachment_save(self, content_id: str, new_filename: str = None, **kwargs):
        content_filename, content = self.attachment_content(content_id, **kwargs)
        filename = new_filename or content_filename
        if content:
            with open(filename, 'wb') as f:
                f.write(content)
                return True, filename
        else:
            return False, None

    def get_attachment_content(self):
        return self.attachment_content(self.id or self.contentId)

    def download(self, filename: str = None):
        return self.attachment_save(content_id=self.id or self.contentId, new_filename=filename)


class AttachmentModel(BaseModel, AttachmentMethods):
    contentId: str
    URL: str
    detachedSignature: str


class CodeModel(BaseModel):
    code: str


class CodeNameModel(CodeModel):
    name: str


class CodeNameValueModel(CodeNameModel):
    value: Any


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


# -------------------------
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


class SignedDataModel(BaseModel, AttachmentMethods):
    id: str
    size: int
    hash: str
    fileType: str


class BiddConditionsModel(BaseModel):
    biddStartTime: datetime.datetime
    biddEndTime: datetime.datetime
    biddReviewDate: Optional[datetime.date] = None
    startDate: Optional[datetime.datetime] = None


# -------------------------
class DocModel(BaseModel, AttachmentMethods):
    id: str
    name: str
    size: int
    hash: str
    attachmentType: CodeNameModel


# -------------------------
class ImageIdModel(BaseModel, AttachmentMethods):
    id: str
    name: str
    size: int
    hash: str
    attachmentType: CodeModel


class ChangeInfoModel(BaseModel):
    changeReasonText: Optional[str] = None
    changeReasonRef: CodeNameModel


# -------------------------


class AdditionalDetailModel(CodeNameModel):
    value: Union[str, int, float, CodeNameModel, list[CodeNameModel]]


class CharacteristicModel(BaseModel):
    code: str
    name: str
    characteristicValue: Union[int, float, str, CodeNameModel, list[CodeNameModel]]
    OKEI: Optional[CodeNameModel] = None


class BiddingObjectInfoModel(BaseModel):
    subjectRF: Optional[CodeNameModel] = None
    estateAddress: Optional[str] = None
    category: CodeNameModel
    isCompound: Optional[bool] = None
    ownershipForms: CodeNameModel
    characteristics: Optional[list[CharacteristicModel]] = []


class RecipientModel(BaseModel):
    name: str
    INN: str
    KPP: str


class AccountsRequisitesModel(BaseModel):
    electronicPlatform: bool
    bankName: str
    BIK: str
    payAccount: str
    corAccount: str
    treasuryAccount: Optional[str] = None
    purposePayment: Optional[str] = None
    recipient: RecipientModel


class LotModel(BaseModel):
    lotNumber: int
    lotStatus: str
    lotName: str
    lotDescription: str
    privatizationReason: Optional[str] = None
    priceMin: Optional[float] = None
    priceStep: Optional[float] = None
    deposit: Optional[float] = None
    currency: Optional[CodeNameModel] = None
    accountsRequisites: Optional[AccountsRequisitesModel] = None
    biddingObjectInfo: BiddingObjectInfoModel
    additionalDetails: Optional[list[AdditionalDetailModel]] = []
    biddingFeatures: Optional[list[CodeNameValueModel]] = []
    docs: Optional[list[DocModel]] = []
    imageIds: Optional[list[ImageIdModel]] = []

    @property
    def region_code(self) -> Optional[str]:
        try:
            return self.biddingObjectInfo.subjectRF.code
        except Exception as e:  # noqa: F841
            print(self.biddingObjectInfo)

    @property
    def region_name(self) -> Optional[str]:
        if self.biddingObjectInfo.subjectRF:
            return self.biddingObjectInfo.subjectRF.name
        return None

    @property
    def price_min_for(self) -> Optional[str]:
        return self._item_name_by_code_startswith('DA_priceMinFor')

    @property
    def price_min_for_short(self) -> Optional[str]:
        if self.price_min_for is None:
            return None
        parts = self.price_min_for.split('Арендный платеж ')
        if len(parts) == 2:
            return parts[1]
        return self.price_min_for
        # 'Арендный платеж за год' 'Арендный платеж за месяц'

    @property
    def price_min_ready(self) -> Optional[str]:
        return f'{self.priceMin} ({self.price_min_for_short})'

    @property
    def contract_years(self) -> Optional[str]:
        return self._item_value_by_code_startswith('DA_contractYears')

    @property
    def contract_months(self) -> Optional[str]:
        return self._item_value_by_code_startswith('DA_contractMonths')

    @property
    def contract_date(self) -> Optional[str]:
        return self._item_value_by_code_startswith('DA_contractDate')

    @property
    def address(self) -> Optional[str]:
        return self.biddingObjectInfo.estateAddress

    @property
    def description(self) -> str:
        return self.lotDescription

    def _item_name_by_code_startswith(self, start: str) -> Optional[AdditionalDetailModel]:
        for item in self.additionalDetails:
            if item.code.startswith(start):
                return item.value.name
        return None

    def _item_value_by_code_startswith(self, start: str) -> Optional[AdditionalDetailModel]:
        for item in self.additionalDetails:
            if item.code.startswith(start):
                return item.value
        return None


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


# ___ CANCEL NOTICE
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


# ___ STOP NOTICE
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
