import random
from datetime import timedelta

from app.models.users import User
from app.seeds.config import (
    TUNISIE_PREFIXES,
    USER_COUNT,
    USER_STATUS_WEIGHTS,
    BATCH_SIZE,
)
from app.seeds.utils import uid, rand_date, weighted_choice
from .base import BaseGenerator


class UsersGenerator(BaseGenerator):
    name = "users"

    def run(self, count: int = USER_COUNT, **kwargs) -> list:
        self.log(f"{count} users — distribution ElJournal...")

        generated = 0
        attempts  = 0
        max_attempts = count * 3  # éviter boucle infinie

        while generated < count and attempts < max_attempts:
            attempts += 1

            # ✅ TUNISIE_PREFIXES = "+216XX" (6 chars)
            # ✅ On ajoute 6 chiffres → total après +216 = 8 chiffres
            # Exemple : +216 98 123456 → +21698123456
            prefix = random.choice(TUNISIE_PREFIXES)   # ex: "+21698"
            suffix = str(random.randint(100_000, 999_999))  # 6 chiffres
            phone  = prefix + suffix                   # ex: "+21698123456"

            # Vérifier unicité
            exists = (
                self.db.query(User.id)
                .filter(User.phone_number == phone)
                .first()
            )
            if exists:
                continue

            status     = weighted_choice(
                USER_STATUS_WEIGHTS["choices"],
                USER_STATUS_WEIGHTS["weights"],
            )
            created_at = rand_date(1, 180)

            user = User(
                id=uid(),
                phone_number=phone,
                status=status,
                created_at=created_at,
                last_activity_at=(
                    created_at + timedelta(days=random.randint(0, 7))
                    if status == "active"
                    else None
                ),
            )
            self.db.add(user)
            generated += 1

            self.commit_batch(BATCH_SIZE, count)

        self.db.commit()
        self.log_done(generated)

        # ✅ Retourner une Query (pas une liste)
        return self.db.query(User)