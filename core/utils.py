import re
from functools import wraps

from strawberry.types import Info
from strawberry.types.nodes import InlineFragment


def convert_to_snake_case(string):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def get_requested_fields(info: Info, object_type: str, inner_object="response") -> set:
    for field in info.selected_fields:
        for selection in field.selections:
            if (
                not isinstance(selection, InlineFragment)
                or selection.type_condition != object_type
            ):
                continue
            for _selection in selection.selections:
                if _selection.name == inner_object:
                    return {
                        convert_to_snake_case(__selection.name)
                        for __selection in _selection.selections
                    }


def db_to_graphql_type_converter(graphql_return_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            db_model_object = func(*args, **kwargs)
            return convert_to_graphql_type(db_model_object, graphql_return_type)

        return wrapper

    return decorator


def convert_to_graphql_type(db_model_object, graphql_return_type):
    fields = graphql_return_type.__dict__["__dataclass_fields__"].keys()
    return graphql_return_type(**{f: getattr(db_model_object, f) for f in fields})
