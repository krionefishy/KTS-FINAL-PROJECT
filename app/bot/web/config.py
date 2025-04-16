
import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application


@dataclass
class BotConfig:
    token: str


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    

@dataclass
class AdminConfig:
    id: int
    email: str
    password: str


@dataclass
class Config:
    bot: BotConfig
    database: DatabaseConfig
    admin: AdminConfig


@dataclass
class SessionConfig:
    key: str
    lifetime: int = 24 * 3600
    cookie_name: str = "session_id"
    http_only: bool = True
    secure: bool = False

   
def setup_config(app: "Application", cfg_path: str):
    with open(cfg_path, "r") as f:
        raw_config = yaml.safe_load(f)
    app.config = Config(
        admin=AdminConfig(
            id=1,
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"]
        ),
        database=DatabaseConfig(
                host=raw_config["database"]["host"],
                port=raw_config["database"]["port"],
                user=raw_config["database"]["user"],
                password=raw_config["database"]["password"],
                database=raw_config["database"]["database"],
        ),
        bot=BotConfig(
                token=raw_config["bot"]["token"],
                group_id=raw_config["bot"]["group_id"]
        ),
        session=SessionConfig(
            key=raw_config["session"]["key"],
            lifetime=raw_config["session"].get("lifetime", 86400), 
            cookie_name=raw_config["session"].get("cookie_name", "session_id"),
            http_only=raw_config["session"].get("http_only", True),
            secure=raw_config["session"].get("secure", False)
        ),
    )