from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    allowed_origins: str = "http://localhost:3000"
    max_prompt_length: int = 1200

    @property
    def allowed_origins_list(self) -> List[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]

settings = Settings()