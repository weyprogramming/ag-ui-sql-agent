from __future__ import annotations

import json

from typing import List, Optional, TypedDict, Literal

from enum import StrEnum

from uuid import UUID, uuid4

from cryptography.fernet import Fernet

from pydantic import BaseModel, Field, computed_field

from typing_extensions import Self

from uuid import UUID, uuid4

from dataclasses import dataclass

from pydantic import Field, model_validator

from sqlalchemy import Engine, create_engine, MetaData, text

from pandas import read_sql_query, DataFrame


from settings import settings

class State(BaseModel):
    sql_dependencies: List[SQLBaseDependency] = []

class SQLType(StrEnum):
    MSSQL = "mssql"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    SQLITE = "sqlite"
    
class SQLDatasourceDict(TypedDict):
    sql_dialect: SQLType
    tables: list[SQLDatabaseTable]

class SQLConnectionParams(BaseModel):
    type: SQLType
    host: str
    port: int
    username: str
    encrypted_password: bytes
    database: str
    
    @computed_field
    def password(self) -> str:
        return Fernet(settings.DB_PASSWORD_KEY).decrypt(self.encrypted_password).decode()
    
class JoinDict(TypedDict):
    table: str
    table_id: Optional[str]
    column: str
    column_id: Optional[str]

class ColumnDict(TypedDict):
    id: str
    name: str
    key: str
    type: str
    nullable: Optional[bool]
    unique: Optional[bool]
    comment: Optional[str]
    join: Optional[JoinDict] | None

class TableDict(TypedDict):
    id: str
    name: str
    columns: List[ColumnDict]
    
class SQLJoin(BaseModel):
    table: str
    table_id: UUID
    column_key: str
    column_id: UUID

class SQLTableColumn(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    table_id: UUID
    exclude: bool = False
    name: str
    key: str
    type: str | None = None
    nullable: bool | None = None
    primary_key: bool | None = None
    unique: bool | None = None
    comment: str | None = None
    join: SQLJoin | None = None


class SQLDatabaseTable(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    table_name: str
    description: str | None
    comment: str | None
    columns: list[SQLTableColumn] = []
    
    def get_dict(self, short: bool = False, table_subset: list[SQLDatabaseTable] | None = None, include_table_id: bool = False, include_column_ids: bool = False) -> dict:
            
        table_dict: TableDict = {
            "table_name": self.table_name,
            "description": self.description,
            "comment": self.comment,
            "columns": []
        }
        
        if include_table_id:
            table_dict["id"] = str(self.id)
            
        for column in self.columns:
            
            if short:

                column_dict = column.name
            
            else:
                column_dict: ColumnDict = {
                    key: value for key, value in {
                        "name": column.name,
                        "key": column.key,
                        "type": column.type,
                        "nullable": column.nullable,
                        "unique": column.unique,
                        "comment": column.comment,
                    }.items() if ((value is not None) and (not column.exclude))
                }
            
                if column.join is not None:
                    
                    if table_subset is None:
                        
                        column_dict["join"] = {
                            "table": column.join.table,
                            "column_key": column.join.column_key
                        }
                        
                        if include_column_ids:
                            column_dict["join"]["id"] = column.join.column_id
                        
                    else:
                        
                        if column.join.table_id in [table.id for table in table_subset]:
                            
                            column_dict["join"] = {
                                "table": column.join.table,
                                "column": column.join.column_key
                            }
                            
                            if include_column_ids:
                                column_dict["join"]["id"] = column.join.column_id
                                
            if include_column_ids:
                column_dict["id"] = str(column.id)
                
            table_dict["columns"].append(column_dict)
        
        return table_dict
        
        
    def get_prompt(self, table_subset: list[SQLDatabaseTable] | None = None) -> str:
        return json.dumps(self.get_dict(table_subset=table_subset), indent=4)
    
    def set_exclude_columns_by_name(self, column_names_to_exclude: list[str]) -> None:
        for column in self.columns:
            if column.name in column_names_to_exclude:
                column.exclude = True
            else:
                column.exclude = False



class SQLBaseDependency(BaseModel):
    name: str
    connection_params: SQLConnectionParams
    tables: list[SQLDatabaseTable] | None = None
    table_subset: list[SQLDatabaseTable] | None = None
    column_names_to_exclude: list[str]| None = None
            
    
    @model_validator(mode="after")
    def set_exclude_columns(self) -> Self:
        
        if self.column_names_to_exclude is not None:
            
            for column_name in self.column_names_to_exclude:
                
                for table in self.tables:
                    
                    for column in table.columns:
                        if column.name == column_name:
                            column.exclude = True
                                
        return self
            
    def get_engine(self) -> Engine:
        
        if self.connection_params.type == SQLType.MSSQL:
            return create_engine(
                f"mssql+pymssql://{self.connection_params.username}:{self.connection_params.password}@{self.connection_params.host}:{self.connection_params.port}/{self.connection_params.database}"
            )
            
        elif self.connection_params.type == SQLType.MYSQL:
            return create_engine(
                f"mysql+pymysql://{self.connection_params.username}:{self.connection_params.password}@{self.connection_params.host}:{self.connection_params.port}/{self.connection_params.database}"
            )
            
        elif self.connection_params.type == SQLType.POSTGRES:
            return create_engine(
                f"postgresql+psycopg2://{self.connection_params.username}:{self.connection_params.password}@{self.connection_params.host}:{self.connection_params.port}/{self.connection_params.database}"
            )
            
        raise ValueError("Unsupported SQL dialect")
                
    def get_metadata(self) -> MetaData:

        metadata: MetaData = MetaData()
        metadata.reflect(bind=self.get_engine())
        return metadata
    
    def set_tables_from_metadata(self, metadata: MetaData) -> None:
        
        tables: list[SQLDatabaseTable] = []
        
        for sa_table in metadata.tables.values():
            
            table = SQLDatabaseTable(
                provider=self,
                table_name=sa_table.name,
                comment=sa_table.comment,
                description=sa_table.description,
                columns=[]
            )
            
            for sa_column in sa_table.columns:
                
                table.columns.append(
                    SQLTableColumn(
                        table_id=table.id,
                        name=sa_column.name,
                        key=sa_column.key,
                        type=str(sa_column.type),
                        nullable=sa_column.nullable,
                        unique=sa_column.unique,
                        primary_key=sa_column.primary_key,
                        comment=sa_column.comment,
                    )
                )
                
            tables.append(table)
            
        for sa_table in metadata.tables.values():
            
            for sa_column in sa_table.columns:
                
                if sa_column.foreign_keys:
                    
                    child_table: SQLDatabaseTable = next(
                        table for table in tables if table.table_name == sa_table.name
                    )
                    
                    child_column: SQLTableColumn = next(
                        column for column in child_table.columns if column.name == sa_column.name
                    )
                    
                    for foreign_key in sa_column.foreign_keys:
                        
                        parent_table: SQLDatabaseTable = next(
                            table for table in tables if table.table_name == foreign_key.column.table.name
                        )
                        
                        parent_column: SQLTableColumn = next(
                            column for column in parent_table.columns if column.name == foreign_key.column.name
                        )
                        
                        child_column.join = SQLJoin(
                            table=parent_table.table_name,
                            table_id=parent_table.id,
                            column_key=parent_column.key,
                            column_id=parent_column.id
                        )
                        
        self.tables = tables
        self.set_exclude_columns()
        
    def get_dict(self, short: bool = False, table_subset: list[SQLDatabaseTable] | None = None, include_datasource_info: bool = False, include_table_ids: bool = False) -> dict:
        
        datasource_dict: SQLDatasourceDict = {
            "datasource_type": "SQL Database",
            "sql_dialect": self.connection_params.type,
            "tables": []
        }
        
        if include_datasource_info:
            datasource_dict["name"] = self.name
            datasource_dict["id"] = str(self.id)
        
        if table_subset is None:
            
            for table in self.tables:
                datasource_dict["tables"].append(table.get_dict(
                    short=short,
                    include_table_id=include_table_ids
                ))
                
        else:
            
            for table in table_subset:
                datasource_dict["tables"].append(table.get_dict(
                    short=short,
                    table_subset=table_subset,
                    include_table_id=include_table_ids
                ))
        
        return datasource_dict
    
    def get_prompt(self, short: bool = False, table_subset: list[SQLDatabaseTable] | None = None, include_datasource_info: bool = False, include_table_ids: bool = False) -> str:
        
        return json.dumps(self.get_dict(short=short, table_subset=table_subset, include_datasource_info=include_datasource_info, include_table_ids=include_table_ids), indent=4)
    
    def get_dataframe_from_query(self, query: str) -> DataFrame:
        """"
        Returns a DataFrame from a SQL query
        """
        
        df = read_sql_query(text(query), self.get_engine())
        
        if self.column_names_to_exclude is not None:
            df = df.drop(columns=[col for col in self.column_names_to_exclude if col in df.columns], errors='ignore')
        
        return df
    
    def get_table_by_id(self, table_id: UUID) -> SQLDatabaseTable:
        return next(
            (table for table in self.tables if table.id == table_id),
            None
        )
    
    def get_tables_by_ids(self, table_ids: list[UUID]) -> list[SQLDatabaseTable]:
        return [
            table for table in self.tables if table.id in table_ids
        ]
        
    def dump_model_to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "connection_params": self.connection_params.model_dump(mode="json"),
            "tables": [table.get_dict(include_table_id=True, include_column_ids=True) for table in self.tables]
        }
        
    def get_column_by_id(self, column_id: UUID | str) -> SQLTableColumn | None:
        
        if isinstance(column_id, str):
            column_id = UUID(column_id)
            
        for table in self.tables:
            for column in table.columns:
                if column.id == column_id:
                    return column
                
        return None