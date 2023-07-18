from core.auth.models.configuration import Configuration
from core.lib.basecrud import Crud


class ConfigurationCrud(Crud):
    model = Configuration

    @classmethod
    def create(cls, configuration: dict) -> Configuration:
        configuration_model = Configuration(**configuration)
        configuration_model.save()
        return configuration_model

    @classmethod
    def update(cls, query: dict, update_fields: dict) -> Configuration:
        cls.validate(update_fields)
        configuration = cls.get(**query)

        configuration.modify(update_fields)
        return configuration
