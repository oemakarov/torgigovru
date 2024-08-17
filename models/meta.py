import datetime
from typing import List

from pydantic import BaseModel, field_validator


def parse_date(value) -> datetime.date:
    return datetime.datetime.strptime(value, '%Y%m%d').date()


def parse_datetime(value) -> datetime.datetime:
    return datetime.datetime.strptime(value, '%Y%m%dT%H%M')


class DataModel(BaseModel):
    source: str
    created: datetime.datetime
    provenance: str
    valid: datetime.date
    structure: datetime.date

    @field_validator('valid', 'structure', mode='before')
    def parse_date(cls, value):
        return parse_date(value)

    @field_validator('created', mode='before')
    def validate_datetime(cls, value):
        return parse_datetime(value)


class StructureModel(BaseModel):
    source: str
    created: datetime.date

    @field_validator('created', mode='before')
    def parse_date(cls, value):
        return parse_date(value)


class PublisherModel(BaseModel):
    name: str
    phone: str
    mbox: str


class MetaModel(BaseModel):
    standardversion: str
    identifier: str
    title: str
    description: str
    creator: str
    created: datetime.date
    modified: datetime.datetime
    subject: str
    format: str
    data: list[DataModel]
    structure: list[StructureModel]
    publisher: PublisherModel

    @field_validator('created', mode='before')
    def parse_date(cls, value):
        return parse_date(value)

    @field_validator('modified', mode='before')
    def parse_datetime(cls, value):
        return parse_datetime(value)

    def sorted_data(self) -> List[DataModel]:
        return sorted(self.data, key=lambda x: x.created, reverse=True)
