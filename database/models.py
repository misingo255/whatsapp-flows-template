from sqlmodel import (
    Field,
    Session,
    SQLModel,
    create_engine,
    select,
)
from sqlmodel.sql.expression import Select, SelectOfScalar
from datetime import datetime, timezone
import os


# INITIALIZE THE DATABASE
SQLITE_FILENAME = "database.db"
sqlite_url = f"sqlite:///{SQLITE_FILENAME}"
database_url = os.getenv("DATABASE_URL", "")
if not database_url:
    database_url = sqlite_url
else:
    pass

engine = create_engine(database_url, echo=False)

# Configure database caching
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore


class FlowData(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    flow_name: str = Field(description="Name of the flow")
    flow_id: str = Field(description="ID of the flow")
    is_published: bool = Field(default=False, description="is the flow published")
    is_uploaded: bool = Field(default=False, description="is the flow uploaded")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def save(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

        with Session(engine) as session:
            session.add(self)
            session.commit()
            session.refresh(self)
        return self

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self.save()

    def delete(self):
        with Session(engine) as session:
            session.delete(self)
            session.commit()
        return {"message": "Data deleted."}

    @classmethod
    def get_all(cls):
        with Session(engine) as session:
            return session.exec(select(cls)).fetchall()

    @classmethod
    def by_id(cls, id: int):
        with Session(engine) as session:
            data = session.exec(select(cls).where(cls.id == id)).first()
            return data

    @classmethod
    def first_data(cls):
        with Session(engine) as session:
            data = session.exec(select(cls)).first()
            return data


# Create the tables
SQLModel.metadata.create_all(engine)
