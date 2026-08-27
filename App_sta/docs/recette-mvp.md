# Recette MVP

Cette recette valide le parcours utilisateur principal sur un environnement propre.

## Prerequis

- Python 3.11 ou plus recent
- Node.js et npm
- Docker Desktop pour PostgreSQL
- un emulateur Android ou un appareil Android

## Demarrage backend

```powershell
Copy-Item .env.example services/api/.env
cd services/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
cd ../..
docker compose up -d db
cd services/api
python -m alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Avec Docker Compose, `migrate` applique automatiquement les migrations avant `api`.

Verifier :

- `GET /health` retourne `status = ok` ;
- `GET /docs` affiche la documentation OpenAPI ;
- la revision Alembic est `0006_unique_user_progress_method`.

## Donnees de reference

Utiliser [mvp_reference.csv](fixtures/mvp_reference.csv). Il contient :

- variables quantitatives : `age`, `revenu`, `education` ;
- variables qualitatives : `region` ;
- cible binaire : `adoption`.

## Parcours API

- [ ] Creer un compte.
- [ ] Se connecter et obtenir les tokens.
- [ ] Lire `/users/me` avec l'access token.
- [ ] Importer `mvp_reference.csv`.
- [ ] Verifier 20 observations et 5 variables.
- [ ] Verifier les types et l'aperçu paginé.
- [ ] Calculer les statistiques descriptives sur `revenu`.
- [ ] Executer un test t.
- [ ] Executer l'ANOVA sur `revenu` par `region`.
- [ ] Executer Chi-deux sur `region` et `adoption`.
- [ ] Executer OLS sur `revenu` avec `age` et `education`.
- [ ] Executer Logit et Probit sur `adoption`.
- [ ] Consulter `/analysis/history`.
- [ ] Vérifier qu'un second utilisateur ne voit pas le dataset ni l'historique du premier.
- [ ] Vérifier `/progress` et les méthodes marquées après analyse.

## Parcours Android

- [ ] Installer les dependances dans `apps/mobile`.
- [ ] Definir `EXPO_PUBLIC_API_URL` vers l'adresse accessible depuis l'emulateur.
- [ ] Creer un compte depuis l'application.
- [ ] Importer le CSV depuis le tableau de bord.
- [ ] Ouvrir l'explorateur et verifier l'aperçu.
- [ ] Ouvrir le parcours d'apprentissage.
- [ ] Ouvrir une méthode et vérifier sa progression.
- [ ] Lancer une analyse descriptive.
- [ ] Ouvrir une analyse t-test ou OLS.
- [ ] Consulter les analyses récentes.
- [ ] Couper le serveur et vérifier le message réseau.
- [ ] Restaurer le serveur et vérifier le renouvellement de session.

## Critères de sortie

- Aucun échec dans les tests backend.
- Typecheck mobile sans erreur.
- Résultats contrôlés avec Python ou R sur le fixture.
- Aucun dataset ou historique visible par un autre utilisateur.
- Erreurs compréhensibles en français.
- APK de test installé sur au moins un appareil ou émulateur Android.
