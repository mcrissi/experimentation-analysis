from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    data_dir: Path = Field(
        default=Path("data"), validation_alias=AliasChoices("XPA_DATA_DIR", "DATA_DIR", "data_dir")
    )
    seed: int = Field(default=20080320, validation_alias=AliasChoices("XPA_SEED", "seed"))

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"
