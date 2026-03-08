from sqlalchemy.orm import Session


class BaseGenerator:
    """Classe de base pour tous les generators de seed."""

    name: str = "base"

    def __init__(self, db: Session):
        self.db = db
        self.created: list = []

    def run(self, **kwargs) -> list:
        raise NotImplementedError

    def log(self, message: str):
        print(f"  → [{self.name}] {message}")

    def log_done(self, count: int | None = None):
        c = count or len(self.created)
        print(f"     ✅ {c} {self.name}")

    def commit_batch(self, batch_size: int, total: int | None = None):
        if len(self.created) % batch_size == 0:
            self.db.commit()
            if total:
                print(f"        ... {len(self.created)}/{total}")