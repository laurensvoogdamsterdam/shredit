from fastapi import APIRouter
from starlette_graphene3 import GraphQLApp, make_playground_handler

from api.db.pool import AsyncSessionLocal
from api.utils.gql import schema

router = APIRouter(prefix="/gql")


router.add_route("/", GraphQLApp(schema, on_get=make_playground_handler()))
