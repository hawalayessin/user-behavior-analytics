# Report Generator et MCP - Documentation Simple

## Objectif

Le Report Generator produit un rapport PDF DigMaco à partir des choix faits dans l'interface:

- type de rapport;
- période d'analyse;
- services inclus;
- sections sélectionnées;
- options IA;
- recommandations stratégiques.

Le rapport final doit toujours être généré, même si Gemini échoue. Dans ce cas, le système utilise un fallback métier et l'indique clairement dans le PDF.

## Choix Utilisateur

### 01 - Report Type

Le type de rapport définit les sections sélectionnées par défaut:

- **Executive Summary**: résumé KPI pour leadership.
- **Churn & Retention Analysis**: churn, désabonnement et cohortes.
- **AI Insights & Segmentation**: prédictions ML et segmentation.
- **Complete Report**: rapport complet sur tous les modules.

L'utilisateur peut ensuite modifier les sections manuellement.

### 02 - Included Services

Le frontend charge les services via:

```text
GET /services
```

Puis il envoie les services sélectionnés dans:

```json
"services_included": ["ElJournal By TT", "Esports By TT", "..."]
```

Ces services sont utilisés côté backend pour filtrer les données quand les requêtes SQL le supportent.

### 03 - Report Sections

Sections possibles:

- Executive Summary
- User Activity
- Churn Analysis
- Retention & Cohorts
- Free Trial Behavior
- Campaign Impact (SMS)
- AI & Segmentation
- Raw Data Export

Le template PDF affiche uniquement les sections présentes dans:

```json
"sections_included": [...]
```

### 04 - AI Options

Deux modes existent:

- **Avec IA**: Gemini génère les textes d'analyse.
- **Sans IA**: le rapport utilise uniquement les règles métier, sans consommer le quota Gemini.

Le bouton **Générer sans IA (économiser le quota)** sert aux tests quotidiens.

## Flux de Génération

1. Le frontend envoie `POST /reports/generate`.
2. Le backend crée une entrée dans `report_history`.
3. La génération tourne en tâche background.
4. Le backend collecte les données:
   - KPIs globaux;
   - churn;
   - segments;
   - anomalies;
   - campagnes;
   - cohortes de rétention.
5. Le service PDF appelle le service MCP si l'IA est activée.
6. Le service MCP vérifie le cache 24h.
7. Si cache miss, le quota guard vérifie la limite journalière.
8. Le backend collecte les résultats des tools MCP.
9. Un prompt compact est envoyé à Gemini.
10. Gemini retourne un JSON structuré.
11. Le backend parse le JSON et le sauvegarde dans le cache.
12. Les insights sont fusionnés avec le fallback métier pour remplir les clés manquantes.
13. Le template HTML est rendu.
14. Playwright convertit le HTML en PDF.
15. Le frontend poll `/reports/status/{id}`.
16. Le PDF est téléchargé via `/reports/download/{id}`.

## Architecture MCP

Le MCP est représenté par une couche de tools analytiques:

- `get_global_kpis`
- `get_churn_analysis`
- `get_segments`
- `get_anomalies`
- `get_campaign_performance`
- `get_retention_cohorts`

Ancien fonctionnement:

```text
Gemini -> tool 1 -> Gemini -> tool 2 -> ... -> Gemini final
```

Problème: trop de requêtes Gemini, donc risque élevé de `429 quota exceeded`.

Fonctionnement actuel:

```text
Backend -> collecte tous les tools -> 1 seul appel Gemini
```

Résultat:

- 1 rapport = 1 requête Gemini maximum;
- moins de risque de quota;
- plus stable pour la soutenance.

## Protection Quota

Le système applique 5 protections.

### 1. Cache 24h

Table:

```text
report_insights_cache
```

Même rapport, même période et mêmes services:

```text
0 nouvel appel Gemini
```

Logs:

```text
INSIGHT_CACHE_HIT key=...
INSIGHT_CACHE_MISS key=...
INSIGHT_CACHE_SAVED key=...
```

### 2. Quota Guard

Limite conservative par défaut:

```text
MCP_GEMINI_DAILY_LIMIT=15
```

Logs:

```text
GEMINI_QUOTA_GUARD_ALLOW call=1/15
GEMINI_QUOTA_GUARD_LIMIT_REACHED calls=15/15
```

### 3. Prompt Compact

Le prompt n'envoie plus tout le JSON complet.

Il envoie seulement les métriques clés:

- active users;
- churn;
- conversion;
- ARPU;
- high risk users;
- segments principaux;
- campagnes;
- rétention;
- anomalies.

Objectif:

```text
moins de tokens, réponse plus courte, moins d'erreurs JSON
```

### 4. Modèles Fallback

Ordre de priorité:

```text
gemini-2.5-flash
gemini-1.5-flash-latest
gemini-1.5-flash-8b
```

Si le premier modèle échoue temporairement, le backend réessaie puis tente le modèle suivant.

### 5. Génération Sans IA

Le frontend contient un bouton:

```text
Générer sans IA (économiser le quota)
```

Ce mode force:

```json
"include_ai_insights": false
```

Donc aucun appel Gemini n'est fait.

## Variables d'Environnement

```text
GEMINI_API_KEY=your-gemini-api-key
MCP_GEMINI_MODEL=gemini-2.5-flash
MCP_GEMINI_FALLBACK_MODELS=gemini-1.5-flash-latest,gemini-1.5-flash-8b
MCP_GEMINI_MIN_INTERVAL_SECONDS=15
MCP_GEMINI_MAX_RETRIES=3
MCP_GEMINI_RETRY_BASE_SECONDS=8
MCP_GEMINI_DAILY_LIMIT=15
```

## Migration Cache

La migration ajoute la table:

```text
report_insights_cache
```

Commande à lancer:

```powershell
alembic upgrade head
```

Vérification:

```powershell
alembic heads
```

Le head attendu est:

```text
b8d4e2f9c713
```

## Résilience Gemini

Cas gérés:

- `429 quota exceeded`: retry avec backoff.
- `503 high demand`: retry avec backoff.
- JSON invalide: tentative de réparation JSON stricte.
- API key manquante: fallback métier.
- quota guard dépassé: fallback métier.

Si Gemini renvoie un JSON invalide:

```text
MCP JSON parse failed ...
Retrying Gemini with strict JSON repair prompt ...
```

Si Gemini réussit:

```text
MCP insights parsed successfully from one Gemini synthesis call
```

## Logs de Succès

Exemple d'un run réussi avec Gemini:

```text
INSIGHT_CACHE_MISS key=fc03cc8c
GEMINI_QUOTA_GUARD_ALLOW call=1/15
MCP backend collection started — report_type=full model=gemini-2.5-flash
MCP backend collecting tool: get_global_kpis
MCP backend collecting tool: get_churn_analysis
MCP backend collecting tool: get_segments
MCP backend collecting tool: get_anomalies
MCP backend collecting tool: get_campaign_performance
MCP backend collecting tool: get_retention_cohorts
MCP insights parsed successfully from one Gemini synthesis call; model=gemini-2.5-flash
INSIGHT_CACHE_SAVED key=fc03cc8c
REPORT_AI_RESULT source=gemini pdf_ai_source=gemini sections=6 report_type=full
REPORT_PDF_DONE filename=... ai_source=gemini
REPORT_GENERATION_DONE id=... ai_source=gemini
```

Exemple d'un run servi depuis le cache:

```text
INSIGHT_CACHE_HIT key=fc03cc8c
REPORT_AI_RESULT source=cache pdf_ai_source=gemini
```

Exemple fallback:

```text
REPORT_AI_RESULT source=fallback
REPORT_PDF_DONE filename=... ai_source=fallback
```

## Vérification PDF

Dans la section `Métadonnées techniques`:

Si Gemini a réussi:

```text
Modèle IA gemini-2.5-flash
```

Si le rapport vient du cache Gemini:

```text
Modèle IA gemini-2.5-flash
```

Si fallback métier:

```text
Modèle IA Règle métier
```

## Sections Alimentées par Gemini

Quand Gemini réussit, il alimente les textes d'analyse suivants:

- résumé exécutif;
- analyse churn;
- analyse segmentation;
- synthèse anomalies;
- performance campagnes;
- recommandations.

Les chiffres, tableaux et graphiques restent fournis par le backend.

## Points à Surveiller

- Le PDF doit afficher les services sélectionnés.
- Le PDF doit afficher les sections demandées.
- Le modèle IA doit correspondre à la source réelle.
- Le cache ne doit pas sauvegarder les fallbacks.
- Le bouton sans IA ne doit pas consommer de quota.
- Les logs `REPORT_*` doivent permettre de diagnostiquer chaque génération.

## Procédure de Test Rapide

1. Lancer la migration:

```powershell
alembic upgrade head
```

2. Redémarrer le backend:

```powershell
uvicorn app.main:app --reload
```

3. Générer un rapport avec IA.

4. Vérifier:

```text
REPORT_AI_RESULT source=gemini
```

5. Regénérer le même rapport.

6. Vérifier:

```text
INSIGHT_CACHE_HIT
REPORT_AI_RESULT source=cache
```

7. Générer sans IA.

8. Vérifier:

```text
REPORT_AI_RESULT source=fallback
```
