from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy import Column, String, BigInteger, Boolean, create_engine, ForeignKey, DateTime, Table

engine = create_engine("postgresql+psycopg2://postgres:ra1020@localhost:5432/fundoo_notes")
session = Session(engine)
Base = declarative_base()

collaborator = Table('collaborator', Base.metadata,
                     Column('user_id', BigInteger, ForeignKey('user.id')),
                     Column('note_id', BigInteger, ForeignKey('notes.id')))


def get_db():
    db = session
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, index=True)
    user_name = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    location = Column(String, nullable=False)
    phone = Column(BigInteger)
    is_verified = Column(Boolean, default=False)
    notes = relationship('Notes', back_populates='user')
    labels = relationship('Labels', back_populates='user')
    notes_m2m = relationship('Notes', secondary=collaborator, back_populates='user')

    def __repr__(self):
        return self.user_name


class Notes(Base):
    __tablename__ = 'notes'

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    color = Column(String, nullable=False)
    reminder = Column(DateTime, default=None)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='notes')
    user_m2m = relationship('User', secondary=collaborator, back_populates='notes')

    def __repr__(self):
        return self.title


class Labels(Base):
    __tablename__ = 'labels'
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='Cascade'), nullable=False)
    user = relationship('User', back_populates='labels')

    def __repr__(self):
        return self.name


def hash_password(password: str):
    return pbkdf2_sha256.hash(password)


def verify_password(hashed_password: str, raw_password: str):
    return pbkdf2_sha256.verify(raw_password, hashed_password)
