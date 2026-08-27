# App Statistique

Application pedagogique d'apprentissage et d'analyse statistique.

## Etape actuelle

Le MVP comprend l'authentification, l'import CSV, l'exploration, les analyses statistiques, les modèles econometriques, l'historique, le contenu pedagogique et la progression utilisateur.

## Structure

- `apps/mobile` : application Android React Native / Expo
- `services/api` : API FastAPI et moteur statistique Python
- `packages/contracts` : contrats partages API/mobile
- `packages/ui` : composants UI partages
- `docs` : architecture, securite et documentation produit

## Demarrage local

Prerequis : Python 3.11+ et Docker Desktop.

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

Puis ouvrir :

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

Avec Docker :

```powershell
docker compose up --build
```

Le service `migrate` applique automatiquement les migrations Alembic avant le demarrage de l'API.

## Recette

La procédure complète est disponible dans [docs/recette-mvp.md](docs/recette-mvp.md). Le dataset de référence se trouve dans [docs/fixtures/mvp_reference.csv](docs/fixtures/mvp_reference.csv).

## Qualite

```powershell
cd services/api
python -m pytest
python -m ruff check .
python -m mypy app
```
