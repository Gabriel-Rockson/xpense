"""Configuration management for xpense."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from difflib import get_close_matches


class Config:
    """Manages user configuration and account registry."""

    DEFAULT_CONFIG = {
        "default_account": "cash",
        "accounts": ["cash"],
        "currency": "USD"
    }

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config with optional custom directory."""
        if config_dir is None:
            config_dir = Path.home() / ".xpense"

        self.config_dir = config_dir
        self.config_path = config_dir / "config.json"
        self._data: Dict[str, Any] = {}
        self._ensure_config()

    def _ensure_config(self) -> None:
        """Ensure config directory and file exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.config_path.exists():
            self._create_default_config()
        else:
            self._load_config()

    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self._data = self.DEFAULT_CONFIG.copy()
        self._save_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, "r") as f:
                self._data = json.load(f)

            # Ensure all default keys exist
            updated = False
            for key, value in self.DEFAULT_CONFIG.items():
                if key not in self._data:
                    self._data[key] = value
                    updated = True

            if updated:
                self._save_config()

        except (json.JSONDecodeError, FileNotFoundError):
            # Corrupted or missing config, recreate
            self._create_default_config()

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._data[key] = value
        self._save_config()

    def get_default_account(self) -> str:
        """Get the default account name."""
        return self._data.get("default_account", "cash")

    def set_default_account(self, account: str) -> None:
        """Set the default account name."""
        # Normalize account name
        account = account.lower().replace(" ", "_")

        # Ensure account is registered
        if not self.is_account_registered(account):
            raise ValueError(f"Account '{account}' is not registered. Add it first with 'xpense account add {account}'")

        self.set("default_account", account)

    def get_accounts(self) -> List[str]:
        """Get list of registered accounts."""
        return self._data.get("accounts", ["cash"])

    def add_account(self, account: str) -> None:
        """Register a new account."""
        # Normalize account name
        account = account.lower().replace(" ", "_")

        accounts = self.get_accounts()
        if account in accounts:
            raise ValueError(f"Account '{account}' already exists")

        accounts.append(account)
        self.set("accounts", accounts)

    def remove_account(self, account: str) -> None:
        """Remove a registered account."""
        # Normalize account name
        account = account.lower().replace(" ", "_")

        accounts = self.get_accounts()
        if account not in accounts:
            raise ValueError(f"Account '{account}' does not exist")

        # Prevent removing default account
        if account == self.get_default_account():
            raise ValueError(f"Cannot remove default account '{account}'. Set a different default first.")

        # Prevent removing last account
        if len(accounts) == 1:
            raise ValueError("Cannot remove the last account")

        accounts.remove(account)
        self.set("accounts", accounts)

    def is_account_registered(self, account: str) -> bool:
        """Check if an account is registered."""
        # Normalize account name
        account = account.lower().replace(" ", "_")
        return account in self.get_accounts()

    def suggest_accounts(self, account: str, limit: int = 3) -> List[str]:
        """Suggest similar account names for typos."""
        # Normalize account name
        account = account.lower().replace(" ", "_")
        accounts = self.get_accounts()
        return get_close_matches(account, accounts, n=limit, cutoff=0.6)

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._data = self.DEFAULT_CONFIG.copy()
        self._save_config()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config