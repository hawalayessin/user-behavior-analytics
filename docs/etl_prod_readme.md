# ETL prod_db (PROD) vers analytics_db

## Objectif

Charger des donnees reelles prod_db dans analytics_db sans modifier le schema utilise par le frontend React et le backend FastAPI.

## Architecture ETL

1. Source PROD: base prod_db (lecture seule).
2. Transform: normalisation statuts/champs, UUID deterministes, validation de coherence.
3. Load: ecriture batch par table dans analytics_db avec upsert.
4. Post-load: recalcul des cohortes via script dedie.

## Mapping prod_db -> analytics_db

| prod_db                     | Analytics      | Mapping                                                                                                                                                   |
| -------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| subscribed_clients         | users          | phone_number -> phone_number, status -> status, subscription_start_date -> created_at                                                                     |
| subscribed_clients         | subscriptions  | service_subscription_type_id/service_id -> service_id, subscription_start_date -> subscription_start_date, subscription_end_date -> subscription_end_date |
| transaction_histories      | billing_events | subscribed_client_id -> subscription_id puis user_id/service_id, status -> status, type -> is_first_charge                                                |
| services                   | services       | entitled -> name, status -> is_active                                                                                                                     |
| service_subscription_types | service_types  | amount -> price, subscription_period_id -> billing_frequency_days                                                                                         |

## Regles statuts validees

- users.status:
  - 1 -> active
  - -1 -> inactive
  - -2 -> inactive
  - 0 -> inactive
- subscriptions.status:
  - 1 -> active
  - -1 -> cancelled
  - -2 -> expired
  - 0 -> trial
- billing_events.status:
  - 1 -> SUCCESS
  - 0, 2, 3 -> FAILED
- is_first_charge:
  - type=1 -> true
  - type=2,3,4 -> false

## Performance et robustesse

- Batch size par defaut: 50000.
- Progression: tqdm par etape volumineuse.
- Retry: 3 tentatives avec backoff exponentiel sur erreurs DB transitoires.
- Idempotence:
  - users: ON CONFLICT(phone_number) DO UPDATE.
  - subscriptions/billing_events/services: UUID deterministes + ON CONFLICT(id) DO UPDATE.
- Journalisation technique: logs JSON horodates + ecriture dans import_logs.

## Execution

Depuis user-analytics-backend:

```bash
pip install pandas sqlalchemy psycopg2-binary tqdm python-dotenv
python etl_prod_to_analytics.py --batch-size 50000 --limit 10000
python etl_prod_to_analytics.py --batch-size 50000
python recalcul_cohorts.py
```

## Variables d'environnement (.env)

```env
PROD_CONN=postgresql://postgres:password@localhost:5432/prod_db
ANALYTICS_CONN=postgresql://postgres:password@localhost:5432/analytics_db
```

## Validation 10k avant full ETL

1. Lancer avec --limit 10000.
2. Verifier comptages cibles et distributions de statuts.
3. Verifier absence de FK orphelines dans subscriptions/billing_events.
4. Relancer la meme commande pour verifier l'idempotence.

## KPI avant/apres (modele de comparaison)

- Avant (seed): jeu synthÃ©tique de reference (10k users env.).
- Apres (prod):
  - users >= 1.17M
  - subscriptions >= 1M
  - billing_events ~ 228k
  - services reels (9)
  - churn global cible ~7-8% (a verifier selon fenetre temporelle)

## Validation modele churn sur donnees reelles

1. Recalculer cohortes apres ETL.
2. Re-entrainer le modele churn via endpoint backend ou pipeline ML existant.
3. Comparer AUC/precision/recall vs baseline seed.
4. Verifier stabilite des segments de risque et coherence metier.

## Notes importantes

- Schema analytics_db immuable: aucune migration/alter table dans ce flux.
- Le champ amount de billing_events est injecte seulement s'il existe dans la table cible.
- Le channel prod_db est normalise (USSD/WEB) pendant la transformation, mais non persiste si la table cible n'a pas de colonne dediee.

