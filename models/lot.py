from typing import Optional, Union
from pydantic import BaseModel

from models.attachment import AttachmentMethods
from models.common import CodeModel, CodeNameModel, CodeNameValueModel, DocModel


class ImageIdModel(BaseModel, AttachmentMethods):
    id: str
    name: str
    size: int
    hash: str
    attachmentType: CodeModel


class AdditionalDetailModel(CodeNameModel):
    value: Union[str, int, float, CodeNameModel, list[CodeNameModel]]


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
        return self._item_value_name_by_code_startswith('DA_priceMinFor')

    @property
    def price_min_for_short(self) -> Optional[str]:
        """make short variant for payment period
        'Арендный платеж за год' - 'за год'
        'Арендный платеж за месяц' - 'за месяц'

        Returns:
            Optional[str]: _description_
        """
        if self.price_min_for is None:
            return None
        parts = self.price_min_for.split('Арендный платеж ')
        if len(parts) == 2:
            return parts[1]
        return self.price_min_for

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

    def _item_value_name_by_code_startswith(self, start: str) -> Optional[AdditionalDetailModel]:
        for item in self.additionalDetails:
            if item.code.startswith(start):
                return item.value.name
        return None

    def _item_value_by_code_startswith(self, start: str) -> Optional[AdditionalDetailModel]:
        for item in self.additionalDetails:
            if item.code.startswith(start):
                return item.value
        return None
