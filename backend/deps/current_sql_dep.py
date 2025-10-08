from cryptography.fernet import Fernet

from deps.sql_dependency import (
    SQLBaseDependency, 
    SQLConnectionParams, 
    SQLType
)
from settings import settings

# TODO: Rework this as this is just a workaround. Database schema information will be stored in redis later on


sql_connection_params = SQLConnectionParams(
    type=SQLType.MSSQL,
    host="localhost",
    port=1433,
    database="German",
    username="sa",
    encrypted_password=Fernet(settings.DB_PASSWORD_KEY.encode()).encrypt("Administrator0803".encode())
)

sql_dep = SQLBaseDependency(
    name="Tradedatabase",
    connection_params=sql_connection_params,
)

metadata = sql_dep.get_metadata()
sql_dep.set_tables_from_metadata(metadata)

current_sql_dep = sql_dep