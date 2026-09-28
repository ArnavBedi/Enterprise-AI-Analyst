from __future__ import annotations

import os
import re
from dataclasses import dataclass

from app.database.connection import DatabaseConnection


@dataclass(frozen=True)
class DatabaseProfile:
    name: str
    environment_variable: str
    url: str

    def connection(self) -> DatabaseConnection:
        return DatabaseConnection(self.url, profile_name=self.name)


def load_database_profiles() -> dict[str, DatabaseProfile]:
    """Load an allowlisted set of database URLs from environment variables."""
    configured = os.getenv("DATABASE_PROFILES", "").strip()
    candidates: list[tuple[str, str]] = []

    if configured:
        for entry in configured.split(","):
            label, separator, variable = entry.strip().partition(":")
            if separator and label.strip() and variable.strip():
                candidates.append((label.strip(), variable.strip()))
    else:
        candidates.append(("Default Database", "DATABASE_URL"))
        for variable in sorted(os.environ):
            if variable == "DATABASE_URL" or not variable.endswith("_DATABASE_URL"):
                continue
            label = re.sub(r"_+", " ", variable[: -len("_DATABASE_URL")]).title()
            candidates.append((label, variable))

    profiles: dict[str, DatabaseProfile] = {}
    for label, variable in candidates:
        url = os.getenv(variable, "").strip()
        if url:
            unique_label = label
            suffix = 2
            while unique_label in profiles:
                unique_label = f"{label} {suffix}"
                suffix += 1
            profiles[unique_label] = DatabaseProfile(unique_label, variable, url)
    return profiles
