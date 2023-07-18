import pytz
import strawberry

from core.base_enum import BaseStrEnum


@strawberry.enum
class NotStrongPasswordErrorMessage(BaseStrEnum):
    LENGTH = (
        "Not strong enough password: Your password must be at least 8 characters long."
    )
    UPPERCASE = "Not strong enough password: Your password must contain at least 1 uppercase letter."
    LOWERCASE = "Not strong enough password: Your password must contain at least 1 lowercase letter."
    DIGIT = "Not strong enough password: Your password must contain at least 1 digit."
    SPECIAL = "Not strong enough password: Your password must contain at least 1 special character."
    SUCCESS = "Strong Password "


@strawberry.enum
class SlaTypeEnum(BaseStrEnum):
    ALL_ALERT = "All Alert"
    SELECT_ALERT = "Select Alert"


@strawberry.enum
class TimezoneEnum(BaseStrEnum):
    UTC = pytz.utc
    ETC_GMT_PLUS_12 = pytz.timezone("Etc/GMT+12")
    ETC_GMT_PLUS_11 = pytz.timezone("Etc/GMT+11")
    PACIFIC_SAMOA = pytz.timezone("Pacific/Samoa")
    PACIFIC_HONOLULU = pytz.timezone("Pacific/Honolulu")
    AMERICA_ANCHORAGE = pytz.timezone("America/Anchorage")
    AMERICA_LOS_ANGELES = pytz.timezone("America/Los_Angeles")
    AMERICA_PHOENIX = pytz.timezone("America/Phoenix")
    AMERICA_DENVER = pytz.timezone("America/Denver")
    AMERICA_CHICAGO = pytz.timezone("America/Chicago")
    AMERICA_NEW_YORK = pytz.timezone("America/New_York")
    AMERICA_CARACAS = pytz.timezone("America/Caracas")
    AMERICA_HALIFAX = pytz.timezone("America/Halifax")
    AMERICA_MANAUS = pytz.timezone("America/Manaus")
    AMERICA_SANTIAGO = pytz.timezone("America/Santiago")
    AMERICA_ST_JOHNS = pytz.timezone("America/St_Johns")
    AMERICA_BUENOS_AIRES = pytz.timezone("America/Argentina/Buenos_Aires")
    AMERICA_SAO_PAULO = pytz.timezone("America/Sao_Paulo")
    ATLANTIC_SOUTH_GEORGIA = pytz.timezone("Atlantic/South_Georgia")
    ATLANTIC_AZORES = pytz.timezone("Atlantic/Azores")
    AFRICA_CASABLANCA = pytz.timezone("Africa/Casablanca")
    EUROPE_LONDON = pytz.timezone("Europe/London")
    EUROPE_PARIS = pytz.timezone("Europe/Paris")
    EUROPE_ISTANBUL = pytz.timezone("Europe/Istanbul")
    ASIA_JERUSALEM = pytz.timezone("Asia/Jerusalem")
    ASIA_DUBAI = pytz.timezone("Asia/Dubai")
    ASIA_KARACHI = pytz.timezone("Asia/Karachi")
    ASIA_KATHMANDU = pytz.timezone("Asia/Kathmandu")
    ASIA_DHAKA = pytz.timezone("Asia/Dhaka")
    ASIA_BANGKOK = pytz.timezone("Asia/Bangkok")
    ASIA_SHANGHAI = pytz.timezone("Asia/Shanghai")
    ASIA_TOKYO = pytz.timezone("Asia/Tokyo")
    AUSTRALIA_SYDNEY = pytz.timezone("Australia/Sydney")
    PACIFIC_AUCKLAND = pytz.timezone("Pacific/Auckland")


@strawberry.enum
class TimeUnitEnum(BaseStrEnum):
    SECOND = "Second"
    MINUTE = "Minute"
    HOUR = "Hour"


@strawberry.enum
class UserTypeEnum(BaseStrEnum):
    STANDARD = "Standard User"
    API = "API User"
