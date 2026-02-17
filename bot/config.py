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
    anthropic_api_key: str


def load_config() -> Config:
    missing = []
    fields = {
        "BOT_TOKEN": os.getenv("BOT_TOKEN"),
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    }
    for key, value in fields.items():
        if not value:
            missing.append(key)
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

    return Config(
        bot_token=fields["BOT_TOKEN"],
        supabase_url=fields["SUPABASE_URL"],
        supabase_key=fields["SUPABASE_SERVICE_ROLE_KEY"],
        groq_api_key=fields["GROQ_API_KEY"],
        anthropic_api_key=fields["ANTHROPIC_API_KEY"],
    )


config = load_config()
