# Architecture initiale

Le monorepo separera le client mobile, l'API et les contrats partages.

## Etape 1

Le service API expose `/health`. PostgreSQL est provisionne par Docker Compose.

## Etape 2

SQLAlchemy et Alembic sont installes. Le modele initial contient la table `users`, prete pour l'implementation de l'authentification. Les migrations sont appliquees explicitement par la commande `alembic upgrade head`.

## Prochaines etapes

1. Configuration et migrations PostgreSQL.
2. Authentification et autorisation.
3. Import et exploration CSV.
4. Moteur statistique.
5. Historique des analyses.
6. Catalogue pedagogique des modules et methodes.
7. Progression utilisateur.
