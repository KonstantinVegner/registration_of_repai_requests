import sqlalchemy

from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('requests', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('requests.id')),
                                     sqlalchemy.Column('priority', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('priority.id')))


class Priority(SqlAlchemyBase):
    __tablename__ = 'priority'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
