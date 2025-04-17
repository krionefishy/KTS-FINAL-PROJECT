from dataclasses import dataclass

from sqlalchemy import JSON, BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.store.database.sqlalchemy_base import Base


class AdminModel(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    chat_id = Column(BigInteger, primary_key=True)
    is_active = Column(Boolean, default=False)
    admin_id = Column(BigInteger, default=None)
    players = Column(JSON)
    current_game_state = Column(JSON)
    current_theme = Column(Integer)


class ThemeModel(Base):
    __tablename__ = "themes"

    _id = Column(Integer, primary_key=True, autoincrement=True)
    theme_name = Column(String, unique=True)


class QuestionModel(Base):
    __tablename__ = "questions"
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    theme_id = Column(Integer, ForeignKey("themes._id"))
    price = Column(Integer)
    question_text = Column(String(500))


class AnswerModel(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, 
                         ForeignKey("questions.question_id"), unique=True)
    answers = Column(JSON)


class UserModel(Base):
    __tablename__ = "users"

    _id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    total_games: Mapped[int] = mapped_column(Integer, default=0)
    total_wins: Mapped[int] = mapped_column(Integer, default=0)


@dataclass
class Admin:
    id: int
    email: str
    password: str


@dataclass
class Answer:
    questiond_id: int
    answers: dict[str: bool]


@dataclass
class Quesion:
    id: int
    theme_id: int
    price: int
    question_text: str


@dataclass
class Theme:
    id: int
    theme_name: str