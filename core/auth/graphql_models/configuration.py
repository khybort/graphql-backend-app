from typing import Optional

import strawberry

from core.auth.enum import SlaTypeEnum, TimeUnitEnum, TimezoneEnum
from core.base_graphql_error import AuthenticationExceptionType, BaseErrorType
from core.graphql_base_model import (
    AllOptional,
    BaseGraphQLModel,
    BaseGraphQLQueryMeta,
    BaseRead,
)


@strawberry.type
class DatetimeConfigurationRead:
    timezone: TimezoneEnum
    date_format: str
    time_format: str


@strawberry.input
class DatetimeConfigurationInput(DatetimeConfigurationRead, BaseGraphQLModel):
    pass


@strawberry.type
class TimeUnitRead:
    value: int
    unit: TimeUnitEnum


@strawberry.input
class TimeUnitInput(TimeUnitRead, BaseGraphQLModel):
    pass


@strawberry.type
class SlaConfigurationRead:
    sla_type: SlaTypeEnum
    alert_type: SlaTypeEnum
    period: TimeUnitRead
    time: TimeUnitRead


@strawberry.input
class SlaConfigurationInput(SlaConfigurationRead, BaseGraphQLModel):
    period: TimeUnitInput
    time: TimeUnitInput


@strawberry.type
class EmailConfigurationRead:
    display_name: str
    email_address: str
    username: str
    password: str
    server: str
    port: int
    use_ssl = bool


@strawberry.input
class EmailConfigurationInput(EmailConfigurationRead, BaseGraphQLModel):
    pass


@strawberry.type
class SettingsConfigurationRead(BaseRead):
    email_configuration: EmailConfigurationRead
    sla_configuration: SlaConfigurationRead
    datetime_configuration: DatetimeConfigurationRead


@strawberry.type
class SettingsConfigurationList:
    response: list[SettingsConfigurationRead]
    meta: BaseGraphQLQueryMeta


@strawberry.input
class SettingsConfigurationCreate(BaseGraphQLModel):
    email_configuration: Optional[EmailConfigurationInput] = strawberry.UNSET
    sla_configuration: Optional[SlaConfigurationInput] = strawberry.UNSET
    datetime_configuration: Optional[DatetimeConfigurationInput] = strawberry.UNSET


@strawberry.input
class SettingsConfigurationUpdate(SettingsConfigurationCreate, metaclass=AllOptional):
    pass


@strawberry.input
class SettingsConfigurationQuery(SettingsConfigurationUpdate):
    id: Optional[strawberry.ID] = strawberry.UNSET


############################################
###### Query & Mutation Return Types #######
############################################

SettingsConfigurationListResponse = strawberry.union(
    "SettingsConfigurationListResponse",
    (
        SettingsConfigurationList,
        BaseErrorType,
        AuthenticationExceptionType,
    ),
)

mutation_responses = (
    SettingsConfigurationRead,
    BaseErrorType,
    AuthenticationExceptionType,
)

SettingsConfigurationCreateResponse = strawberry.union(
    "SettingsConfigurationCreateResponse",
    mutation_responses,
)

SettingsConfigurationUpdateResponse = strawberry.union(
    "SettingsConfigurationUpdateResponse",
    mutation_responses,
)
