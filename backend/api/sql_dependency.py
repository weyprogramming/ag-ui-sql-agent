from fastapi import APIRouter, HTTPException

from redis_om import NotFoundError

from cryptography.fernet import Fernet

from models.sql_dependency_model import SQLBaseDependencyModel
from deps.sql_dependency import SQLConnectionParams
from schemas.sql_dependency import SQLBaseDependencyCreateRequest
from settings import settings

sql_dependency_router = APIRouter()


@sql_dependency_router.post("/sql-dependency")
async def create_sql_dependency(
    sql_dependency_request: SQLBaseDependencyCreateRequest
) -> SQLBaseDependencyModel:

    sql_connection_params = SQLConnectionParams(
        type=sql_dependency_request.type,
        host=sql_dependency_request.host,
        port=sql_dependency_request.port,
        database=sql_dependency_request.database,
        username=sql_dependency_request.username,
        encrypted_password=Fernet(settings.DB_PASSWORD_KEY.encode()).encrypt(sql_dependency_request.password.encode())
    )

    sql_dependency_model = SQLBaseDependencyModel(
        name=sql_dependency_request.name,
        connection_params=sql_connection_params
    )
    
    metadata = sql_dependency_model.get_metadata()
    sql_dependency_model.set_tables_from_metadata(metadata)

    await sql_dependency_model.save()
    
    return sql_dependency_model

@sql_dependency_router.get("/sql-dependency/{dependency_pk}")
async def get_sql_dependency(dependency_pk: str) -> SQLBaseDependencyModel:
    try:
        return await SQLBaseDependencyModel.get(dependency_pk)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="SQL Dependency not found")
    
@sql_dependency_router.get("/sql-dependency")
async def get_all_sql_dependencies() -> list[SQLBaseDependencyModel]:
    primary_keys = await SQLBaseDependencyModel.all_pks()
    
    sql_dependencies: list[SQLBaseDependencyModel] = []
    
    async for pk in primary_keys:
        sql_dependency = await SQLBaseDependencyModel.get(pk)
        sql_dependencies.append(sql_dependency)

    return sql_dependencies