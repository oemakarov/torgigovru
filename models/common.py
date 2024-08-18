from typing import Any

from pydantic import BaseModel

from models.attachment import AttachmentMethods


class CodeModel(BaseModel):
    code: str


class CodeNameModel(CodeModel):
    name: str


class CodeNameValueModel(CodeNameModel):
    value: Any


class SignedDataModel(BaseModel, AttachmentMethods):
    id: str
    size: int
    hash: str
    fileType: str


class DocModel(BaseModel, AttachmentMethods):
    id: str
    name: str
    size: int
    hash: str
    attachmentType: CodeNameModel
