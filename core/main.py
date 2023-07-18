import logging
import sys
from datetime import datetime
from functools import cached_property

import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongoengine import connect
from strawberry.fastapi import BaseContext, GraphQLRouter
from core.storage_management.routers.storage import storage
from core.auth.crud.user import UserCrud
from core.auth.models.user import User
from core.auth.utilities.auth_handler import AuthHandler
from core.config import settings
from core.graphql_base_model import DateTimeWithTimezone
from core.logging.config import configure_colorized_logging
from core.mutations import Mutations
from core.query import Query

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
configure_colorized_logging()
sys.path.append("/core")

API_PREFIX = "/api/v1"

client = connect("app", host="mongodb://mongo:27017/")

origins = [
    settings.ALLOW_HOST,
]


class Context(BaseContext):
    @cached_property
    def user(self) -> User | None:
        if not self.request:
            return None

        authorization = self.request.headers.get("Authorization")
        email = AuthHandler.decode_token(token=authorization, scope="access_token")
        return UserCrud.get(email=email)

    @cached_property
    def source_info(self) -> dict | None:
        source_address = f"{self.request.client.host}:{self.request.client.port}"
        user_agent = self.request.headers.get("user-agent")
        return {"source_address": source_address, "user_agent": user_agent}


app = FastAPI()
auth_handler = AuthHandler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutations,
    scalar_overrides={
        datetime: DateTimeWithTimezone,
    },
)


def get_context() -> Context:
    return Context()


graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(graphql_app, prefix="/graphql")
app.add_websocket_route("/graphql", graphql_app)

app.include_router(storage.router, prefix=API_PREFIX)