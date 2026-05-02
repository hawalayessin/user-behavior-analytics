from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


COMBINED_GITIGNORE = """# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.coverage
htmlcov/
dist/
*.egg-info/
venv/
.venv/
env/

# Environnement
.env
*.env.local

# Logs
logs/
*.log

# IDE
.vscode/settings.json
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
dist/
build/

# Data
*.csv
*.xlsx
__pycache__

# Documentation and progress reports
docs/
RAPPORT*.md
"""

BACKEND_ENV_EXAMPLE = """# Database
ANALYTICS_CONN=postgresql+psycopg2://user:password@localhost:5432/analytics_db
PROD_CONN=postgresql+psycopg2://user:password@prod_db_host:5432/prod_db

# API
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# App
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=[\"http://localhost:5173\"]

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
"""

MAKEFILE_CONTENT = """.PHONY: dev migrate seed test lint

dev:
\tuvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
\talembic upgrade head

seed:
\tpython scripts/seeder/seed_missing_data.py

seed-dry:
\tpython scripts/seeder/seed_missing_data.py --dry-run

test:
\tpytest tests/ -v

lint:
\truff check app/ scripts/
\tblack app/ scripts/ --check

format:
\tblack app/ scripts/
\truff check app/ scripts/ --fix

etl:
\tpython scripts/etl/etl_prod_to_analytics.py

etl-fix:
\tpython scripts/etl/fix_services_mapping.py
"""

PYPROJECT_CONTENT = """[project]
name = \"user-analytics-backend\"
version = \"1.0.0\"
requires-python = \">=3.11\"

dependencies = [
    \"fastapi>=0.111.0\",
    \"uvicorn[standard]>=0.29.0\",
    \"sqlalchemy>=2.0.0\",
    \"alembic>=1.13.0\",
    \"psycopg2-binary>=2.9.9\",
    \"pydantic>=2.7.0\",
    \"pydantic-settings>=2.2.0\",
    \"python-dotenv>=1.0.0\",
    \"python-jose[cryptography]>=3.3.0\",
    \"passlib[bcrypt]>=1.7.4\",
    \"faker>=24.0.0\",
    \"tqdm>=4.66.0\",
    \"pandas>=2.2.0\",
    \"openpyxl>=3.1.0\",
]

[tool.ruff]
line-length = 100
target-version = \"py311\"

[tool.black]
line-length = 100
target-version = [\"py311\"]
"""

README_CONTENT = """# User Analytics Platform - PFE DigMaco

## Stack
- Backend: FastAPI + PostgreSQL + Alembic + SQLAlchemy
- Frontend: React + Vite
- ETL: Python scripts (prod_db -> analytics_db)

## Setup

### Backend
```bash
cp .env.example .env
pip install -e .
make migrate
make seed
make dev
```

### Frontend
```bash
cd user-analytics-frontend
cp .env.example .env
npm install
npm run dev
```

## Commandes utiles
| Commande | Action |
|----------|--------|
| make dev | Lancer FastAPI |
| make migrate | Appliquer migrations |
| make seed | Seeder la base analytics |
| make etl | ETL prod_db -> analytics |
| make test | Tests unitaires |
| make lint | Verifier le code |
"""


@dataclass
class Report:
    created_dirs: list[str] = field(default_factory=list)
    created_files: list[str] = field(default_factory=list)
    moved_files: list[dict[str, str]] = field(default_factory=list)
    deleted_paths: list[str] = field(default_factory=list)
    updated_files: list[str] = field(default_factory=list)
    backed_up_files: list[str] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "created_dirs": self.created_dirs,
            "created_files": self.created_files,
            "moved_files": self.moved_files,
            "deleted_paths": self.deleted_paths,
            "updated_files": self.updated_files,
            "backed_up_files": self.backed_up_files,
            "skipped": self.skipped,
            "errors": self.errors,
            "summary": {
                "created_dirs": len(self.created_dirs),
                "created_files": len(self.created_files),
                "moved_files": len(self.moved_files),
                "deleted_paths": len(self.deleted_paths),
                "updated_files": len(self.updated_files),
                "backed_up_files": len(self.backed_up_files),
                "skipped": len(self.skipped),
                "errors": len(self.errors),
            },
        }


class Reorganizer:
    def __init__(self, root: Path, dry_run: bool = True):
        self.root = root
        self.backend = root / "user-analytics-backend"
        self.frontend = self._detect_frontend_dir()
        self.dry_run = dry_run
        self.report = Report()
        self.py_import_map: dict[str, str] = {}
        self._planned_dirs: set[str] = set()
        self._ignored_dir_names = {
            ".git",
            ".venv",
            "venv",
            "site-packages",
            ".mypy_cache",
            ".ruff_cache",
            ".idea",
            ".vscode",
        }

    def _detect_frontend_dir(self) -> Path | None:
        candidates = [
            self.root / "user-analytics-frontend",
            self.root / "analytics-platform-front",
        ]
        for c in candidates:
            if c.exists() and c.is_dir():
                return c
        return None

    def _log(self, action: str, target: str, status: str, **extra: str) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "target": target,
            "status": status,
            **extra,
        }
        print(json.dumps(payload, ensure_ascii=True))

    def _safe_rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except Exception:
            return path.as_posix()

    def _mkdir(self, path: Path) -> None:
        rel = self._safe_rel(path)
        if path.exists() or rel in self._planned_dirs:
            return
        self._planned_dirs.add(rel)
        self._log("mkdir", rel, "planned" if self.dry_run else "done")
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
        self.report.created_dirs.append(rel)

    def _backup_if_needed(self, path: Path) -> None:
        if not path.exists():
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = path.with_suffix(path.suffix + f".bak.{ts}")
        self._log("backup", self._safe_rel(path), "planned" if self.dry_run else "done", backup=self._safe_rel(bak))
        if not self.dry_run:
            bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        self.report.backed_up_files.append(self._safe_rel(bak))

    def _write_file(self, path: Path, content: str) -> None:
        rel = self._safe_rel(path)
        self._mkdir(path.parent)
        if path.exists() and path.read_text(encoding="utf-8", errors="ignore") == content:
            self.report.skipped.append({"path": rel, "reason": "unchanged"})
            self._log("write", rel, "skipped", reason="unchanged")
            return
        if path.exists():
            self._backup_if_needed(path)
            self.report.updated_files.append(rel)
            status = "planned" if self.dry_run else "done"
            self._log("write", rel, status, mode="update")
        else:
            self.report.created_files.append(rel)
            status = "planned" if self.dry_run else "done"
            self._log("write", rel, status, mode="create")
        if not self.dry_run:
            path.write_text(content, encoding="utf-8")

    def _delete_path(self, path: Path, reason: str) -> None:
        rel = self._safe_rel(path)
        if not path.exists():
            return
        self._log("delete", rel, "planned" if self.dry_run else "done", reason=reason)
        if not self.dry_run:
            try:
                if path.is_dir():
                    for child in sorted(path.rglob("*"), reverse=True):
                        try:
                            if child.is_file() or child.is_symlink():
                                child.unlink(missing_ok=True)
                            elif child.is_dir():
                                child.rmdir()
                        except PermissionError:
                            try:
                                child.chmod(0o666)
                                if child.is_file() or child.is_symlink():
                                    child.unlink(missing_ok=True)
                                elif child.is_dir():
                                    child.rmdir()
                            except Exception as exc:
                                self.report.errors.append({"path": self._safe_rel(child), "error": str(exc)})
                                self._log("delete", self._safe_rel(child), "error", reason="permission-error", error=str(exc))
                        except Exception as exc:
                            self.report.errors.append({"path": self._safe_rel(child), "error": str(exc)})
                            self._log("delete", self._safe_rel(child), "error", reason="delete-failed", error=str(exc))

                    try:
                        path.rmdir()
                    except Exception as exc:
                        self.report.errors.append({"path": rel, "error": str(exc)})
                        self._log("delete", rel, "error", reason="dir-not-empty-or-locked", error=str(exc))
                else:
                    try:
                        path.unlink(missing_ok=True)
                    except PermissionError:
                        path.chmod(0o666)
                        path.unlink(missing_ok=True)
            except Exception as exc:
                self.report.errors.append({"path": rel, "error": str(exc)})
                self._log("delete", rel, "error", reason="delete-failed", error=str(exc))
        self.report.deleted_paths.append(rel)

    def _module_from_path(self, py_path: Path) -> str | None:
        if not py_path.suffix == ".py":
            return None
        rel = py_path.relative_to(self.backend)
        parts = list(rel.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts)

    def _move_file(self, src: Path, dst: Path, reason: str) -> None:
        if not src.exists() or not src.is_file():
            return
        src_rel = self._safe_rel(src)
        dst_rel = self._safe_rel(dst)
        if src.resolve() == dst.resolve():
            return
        self._mkdir(dst.parent)
        if dst.exists():
            self._backup_if_needed(dst)
        self._log("move", src_rel, "planned" if self.dry_run else "done", to=dst_rel, reason=reason)
        if not self.dry_run:
            dst.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
            src.unlink(missing_ok=True)
        self.report.moved_files.append({"from": src_rel, "to": dst_rel})

        if src.suffix == ".py" and dst.suffix == ".py" and src.is_relative_to(self.backend) and dst.is_relative_to(self.backend):
            old_mod = self._module_from_path(src)
            new_mod = self._module_from_path(dst)
            if old_mod and new_mod and old_mod != new_mod:
                self.py_import_map[old_mod] = new_mod

    def _ensure_backend_structure(self) -> None:
        target_dirs = [
            self.backend / "app" / "api" / "v1",
            self.backend / "app" / "services",
            self.backend / "app" / "repositories",
            self.backend / "app" / "core",
            self.backend / "app" / "utils",
            self.backend / "scripts" / "etl",
            self.backend / "scripts" / "seeder",
            self.backend / "scripts" / "sql",
            self.backend / "tests" / "unit",
            self.backend / "tests" / "integration",
            self.backend / "logs",
        ]
        for d in target_dirs:
            self._mkdir(d)

        init_files = [
            self.backend / "app" / "__init__.py",
            self.backend / "app" / "api" / "__init__.py",
            self.backend / "app" / "api" / "v1" / "__init__.py",
            self.backend / "app" / "services" / "__init__.py",
            self.backend / "app" / "repositories" / "__init__.py",
            self.backend / "app" / "core" / "__init__.py",
            self.backend / "app" / "utils" / "__init__.py",
            self.backend / "scripts" / "etl" / "__init__.py",
            self.backend / "scripts" / "seeder" / "__init__.py",
            self.backend / "tests" / "__init__.py",
        ]
        for f in init_files:
            self._write_file(f, "")

        self._write_file(self.backend / "logs" / ".gitkeep", "")

    def _move_backend_root_scripts(self) -> None:
        if not self.backend.exists():
            return

        for etl_script in self.backend.glob("etl_*.py"):
            self._move_file(etl_script, self.backend / "scripts" / "etl" / etl_script.name, "etl-root-to-scripts")

        explicit_moves = {
            "fix_services_mapping.py": self.backend / "scripts" / "etl" / "fix_services_mapping.py",
            "seed_missing_data.py": self.backend / "scripts" / "seeder" / "seed_missing_data.py",
            "recalcul_cohorts.py": self.backend / "scripts" / "etl" / "recalcul_cohorts.py",
            "verify_services_mapping.sql": self.backend / "scripts" / "sql" / "diagnostics.sql",
        }
        moved_sql_names: set[str] = set()
        for name, dest in explicit_moves.items():
            if name.endswith(".sql"):
                moved_sql_names.add(name)
            self._move_file(self.backend / name, dest, "standardize-location")

        # Move raw SQL files in backend root to scripts/sql if still present.
        for sql_file in self.backend.glob("*.sql"):
            if sql_file.name in moved_sql_names:
                continue
            self._move_file(sql_file, self.backend / "scripts" / "sql" / sql_file.name, "sql-root-to-scripts")

        # Duplicate wrapper no longer required when fix script has canonical path.
        dup = self.backend / "script_fix_services_mapping.py"
        if dup.exists():
            self._delete_path(dup, "duplicate-wrapper")

    def _cleanup_unwanted(self) -> None:
        file_patterns = ["*.pyc", "*.pyo", ".DS_Store", "Thumbs.db", "desktop.ini", "*.bak", "*.old", "*_backup*", "*_copy*"]
        dir_names = {"__pycache__", ".pytest_cache", "node_modules", "dist", "build"}

        dir_candidates: list[Path] = []
        file_candidates: list[tuple[Path, str]] = []

        for path in self.root.rglob("*"):
            name = path.name
            if path.is_dir() and name in dir_names:
                if any(part in self._ignored_dir_names for part in path.parts):
                    continue
                dir_candidates.append(path)
                continue

            if any(part in self._ignored_dir_names for part in path.parts):
                continue

            if not path.is_file():
                continue

            if path.suffix == ".ipynb" and "notebooks" not in [p.lower() for p in path.parts]:
                file_candidates.append((path, "notebook-outside-notebooks"))
                continue

            if path.suffix == ".log" and "logs" not in [p.lower() for p in path.parts]:
                file_candidates.append((path, "log-outside-logs"))
                continue

            if path.match("test_*.py") and "tests" not in [p.lower() for p in path.parts]:
                file_candidates.append((path, "test-outside-tests"))
                continue

            if path.name == ".env":
                self.report.skipped.append({"path": self._safe_rel(path), "reason": "protected-env"})
                self._log("delete", self._safe_rel(path), "skipped", reason="protected-env")
                continue

            for pattern in file_patterns:
                if path.match(pattern):
                    file_candidates.append((path, "unwanted-file"))
                    break

        # Delete parent directories once; child candidates are skipped automatically.
        scheduled_dirs: list[Path] = []
        for d in sorted(dir_candidates, key=lambda p: len(p.parts)):
            if any(parent == d or parent in d.parents for parent in scheduled_dirs):
                continue
            scheduled_dirs.append(d)
            self._delete_path(d, "unwanted-dir")

        for f, reason in file_candidates:
            if any(parent in f.parents for parent in scheduled_dirs):
                continue
            self._delete_path(f, reason)

    def _update_python_imports(self) -> None:
        if not self.py_import_map:
            return

        for py_file in self.backend.rglob("*.py"):
            if any(part in self._ignored_dir_names for part in py_file.parts):
                continue
            content = py_file.read_text(encoding="utf-8", errors="ignore") if py_file.exists() else ""
            if not content:
                continue

            updated = content
            for old, new in self.py_import_map.items():
                updated = re.sub(rf"\\bfrom\\s+{re.escape(old)}(\\s+import\\s+)", f"from {new}\\1", updated)
                updated = re.sub(rf"\\bimport\\s+{re.escape(old)}\\b", f"import {new}", updated)

            if updated != content:
                self._log("update_imports", self._safe_rel(py_file), "planned" if self.dry_run else "done")
                if not self.dry_run:
                    self._backup_if_needed(py_file)
                    py_file.write_text(updated, encoding="utf-8")
                self.report.updated_files.append(self._safe_rel(py_file))

    def _generate_standard_files(self) -> None:
        self._write_file(self.root / ".gitignore", COMBINED_GITIGNORE)
        self._write_file(self.backend / ".env.example", BACKEND_ENV_EXAMPLE)
        self._write_file(self.backend / "Makefile", MAKEFILE_CONTENT)
        self._write_file(self.backend / "pyproject.toml", PYPROJECT_CONTENT)
        self._write_file(self.backend / "README.md", README_CONTENT)

        if self.frontend:
            self._write_file(self.frontend / ".env.example", "VITE_API_BASE_URL=http://localhost:8000/api/v1\n")

    def run(self) -> Report:
        self._ensure_backend_structure()
        self._move_backend_root_scripts()
        self._cleanup_unwanted()
        self._update_python_imports()
        self._generate_standard_files()
        return self.report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reorganize PFE full-stack project with safe dry-run mode.")
    parser.add_argument("--root", default=".", help="Project root path")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview actions without changing files")
    mode.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--report", default="reorganize_report.json", help="Output report path (JSON)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    dry_run = True if not args.apply else False

    runner = Reorganizer(root=root, dry_run=dry_run)
    report = runner.run().to_dict()

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = root / report_path

    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "root": root.as_posix(),
        "mode": "dry-run" if dry_run else "apply",
        "report": report,
    }

    report_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps({"message": "report_generated", "path": report_path.as_posix()}, ensure_ascii=True))


if __name__ == "__main__":
    main()


