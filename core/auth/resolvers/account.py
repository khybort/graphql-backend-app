import mimetypes
import os
import shutil
import uuid
from typing import Optional

import strawberry
from strawberry.types import Info

from core.auth.crud.account import AccountCrud
from core.auth.graphql_models.account import (
    AccountCreate,
    AccountCreateResponse,
    AccountList,
    AccountListResponse,
    AccountQuery,
    AccountRead,
    AccountUpdate,
    AccountUpdateResponse,
)
from core.auth.models.account import Avatar
from core.auth.models.permission import PermissionsEnum
from core.auth.utilities.decorators import check_perm
from core.auth.utilities.utilities import resize_image
from core.utils import (
    db_to_graphql_type_converter,
    get_requested_fields,
)
from core.exception import UnsupportedImage
from core.graphql_base_model import (
    BaseGraphQLQueryMeta,
    BaseGraphQLQueryMetaInput,
    DeleteOutput,
)
from core.graphql_base_responses import DeleteResponse
from core.graphql_decorator import graphql_exception_handler

MUTATION_READ_OBJECT = AccountRead


@graphql_exception_handler
@check_perm(PermissionsEnum.ACCOUNT_READ_VALUES)
def resolve_account(
    info: Info,
    query: AccountQuery,
    meta: Optional[BaseGraphQLQueryMetaInput] = None,
    search_text: Optional[str] = None,
) -> AccountListResponse:
    if not meta:
        meta = BaseGraphQLQueryMetaInput()
    requested_fields = get_requested_fields(info, "AccountList")
    accounts, has_more, count = AccountCrud.get_many_partial_with_pagination(
        query.to_dict(), requested_fields, **meta.to_dict(), search_text=search_text
    )
    return AccountList(
        response=accounts,
        meta=BaseGraphQLQueryMeta(**meta.to_dict(), has_more=has_more, count=count),
    )


@graphql_exception_handler
@db_to_graphql_type_converter(MUTATION_READ_OBJECT)
@check_perm(PermissionsEnum.ACCOUNT_CREATE_VALUES)
def resolve_create_account(info: Info, account: AccountCreate) -> AccountCreateResponse:
    if account.avatar:
        account.avatar = upload_avatar(account.avatar)

    return AccountCrud.create(account.to_dict())


@graphql_exception_handler
@db_to_graphql_type_converter(MUTATION_READ_OBJECT)
@check_perm(PermissionsEnum.ACCOUNT_UPDATE_VALUES)
def resolve_update_account(
    info: Info, id: strawberry.ID, set: AccountUpdate
) -> AccountUpdateResponse:
    if set.avatar:
        set.avatar = upload_avatar(set.avatar)
    return AccountCrud.update({"id": id}, set.to_dict())


@graphql_exception_handler
@check_perm(PermissionsEnum.ACCOUNT_DELETE_VALUES)
def resolve_delete_account(info: Info, id: strawberry.ID) -> DeleteResponse:
    return DeleteOutput(message="Deleted successfully", success=AccountCrud.delete(id))


def upload_avatar(avatar):
    support_image_formats = ["png", "jpeg", "jpg", "ppm", "gif", "tiff", "bmp"]
    path = "data/files/profile/avatar/"

    display_name = avatar.filename
    guess_type, _ = mimetypes.guess_type(display_name)
    mime_type = mimetypes.guess_extension(guess_type).replace(".", "")
    name = f"{str(uuid.uuid4())}.{mime_type}"

    if mime_type not in support_image_formats:
        raise UnsupportedImage()
    with open(os.path.join(path, name), "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)
    resize_image(f"{path}{name}", new_size=(400, 200), thumbnail_size=(50, 50))
    return Avatar(name=name, path=path)
