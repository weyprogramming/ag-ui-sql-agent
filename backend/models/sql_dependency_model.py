from aredis_om import JsonModel

from deps.sql_dependency import SQLBaseDependency


class SQLBaseDependencyModel(SQLBaseDependency, JsonModel):
    pass