from core.auth.models.account import Account
from core.lib.basecrud import Crud


class AccountCrud(Crud):
    model = Account

    @classmethod
    def create(cls, account: dict) -> Account:
        account_model = Account(**account)
        account_model.save()
        return account_model

    @classmethod
    def update(cls, query: dict, update_fields: dict) -> Account:
        cls.validate(update_fields)
        account = cls.get(**query)
        account.modify(update_fields)
        return account
