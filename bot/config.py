from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Config:
    bot_token: str
    supabase_url: str
    supabase_key: str
    groq_api_key: str


def load_config() -> Config:
    required = {
        "BOT_TOKEN": os.getenv("BOT_TOKEN"),
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

    return Config(
        bot_token=required["BOT_TOKEN"],
        supabase_url=required["SUPABASE_URL"],
        supabase_key=required["SUPABASE_SERVICE_ROLE_KEY"],
        groq_api_key=required["GROQ_API_KEY"],
    )


config = load_config()
