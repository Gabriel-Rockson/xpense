import json
import os
from difflib import get_close_matches
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

XPENSE_ENV = os.getenv("XPENSE_ENV", "production")
IS_DEV = XPENSE_ENV == "development"

CONFIG_DIR = Path.home() / ".xpense"
CONFIG_FILENAME = "config.dev.json" if IS_DEV else "config.json"
CONFIG_PATH = CONFIG_DIR / CONFIG_FILENAME


class Config(BaseSettings):
    """Xpense configuration model with helpers to manage accounts."""

    default_account: str = "cash"
    accounts: list[str] = ["cash"]
    currency: str = "USD"

    model_config = SettingsConfigDict(
        env_prefix="XPENSE_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("accounts", mode="before")
    def normalize_accounts(cls, accounts: list[str]) -> list[str]:
        return [a.lower().replace(" ", "_") for a in accounts]

    @field_validator("default_account", mode="before")
    def normalize_default_account(cls, account: str) -> str:
        return account.lower().replace(" ", "_")

    def get_default_account(self) -> str:
        return self.default_account

    def set_default_account(self, account: str) -> None:
        account = account.lower().replace(" ", "_")
        if not self.is_account_registered(account):
            raise ValueError(
                f"Account '{account}' is not registered. Add it first with 'xpense account add {account}'"
            )
        self.default_account = account
        self.save()

    def get_accounts(self) -> list[str]:
        return self.accounts

    def add_account(self, account: str) -> None:
        account = account.lower().replace(" ", "_")
        if account in self.accounts:
            raise ValueError(f"Account '{account}' already exists")
        self.accounts.append(account)
        self.save()

    def remove_account(self, account: str) -> None:
        account = account.lower().replace(" ", "_")
        if account not in self.accounts:
            raise ValueError(f"Account '{account}' does not exist")

        if account == self.default_account:
            raise ValueError(
                f"Cannot remove default account '{account}'. Set a different default first."
            )
        if len(self.accounts) == 1:
            raise ValueError("Cannot remove the last account")

        self.accounts.remove(account)
        self.save()

    def is_account_registered(self, account: str) -> bool:
        account = account.lower().replace(" ", "_")
        return account in self.accounts

    def suggest_accounts(self, account: str, limit: int = 3) -> list[str]:
        account = account.lower().replace(" ", "_")
        return get_close_matches(account, self.accounts, n=limit, cutoff=0.6)

    def set_currency(self, code: str) -> None:
        code = code.upper().strip()
        if len(code) != 3:
            raise ValueError(
                f"Currency code must be 3 characters (e.g., 'USD', 'GHS', 'EUR'), got: '{code}'"
            )
        self.currency = code
        self.save()

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(self.model_dump_json(indent=2))

    def reset(self) -> None:
        self.default_account = "cash"
        self.accounts = ["cash"]
        self.currency = "USD"
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


def load_config() -> Config:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            return Config(**data)
        except json.JSONDecodeError:
            cfg = Config()
            cfg.save()
            return cfg
    else:
        cfg = Config()
        cfg.save()
        return cfg


cfg = load_config()
