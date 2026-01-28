# DevOps Étapes Complètes (React/Vite + Django + Koyeb + Cloudflare)

Ce fichier est un guide réutilisable, pensé pour être copié/collé et adapté à un nouveau projet frontend + backend, CI/CD et déploiement.

================================================================================
0) Prérequis locaux
================================================================================
- Node.js 18+ et npm
- Python 3.11+ (recommandé)
- Git
- Docker (optionnel mais utile pour tests locaux)
- Un compte GitHub
- Un compte Koyeb
- Un compte Cloudflare

Astuce : crée un fichier `NOTES.md` dans chaque nouveau projet pour noter les URLs, secrets et variables.

================================================================================
1) Préparer le repo GitHub
================================================================================
1. Créer un repo GitHub (public ou privé).
2. Cloner localement :
   - git clone https://github.com/<user>/<repo>.git
   - cd <repo>
3. Créer la structure :
   - frontend/ (React/Vite)
   - backend/ (Django)
4. Ajouter un README.md minimal.

================================================================================
2) Frontend (React + Vite)
================================================================================
2.1 Créer le frontend
- npm create vite@latest frontend -- --template react-ts

2.2 Installer les dépendances
- cd frontend
- npm install

2.3 Configurer l’URL du backend
- Créer `frontend/.env.example` :
  VITE_API_URL=https://<ton-backend>.koyeb.app/api

- (optionnel) Créer `frontend/.env.local` en local :
  VITE_API_URL=http://localhost:8000/api

2.4 Exemple d’utilisation (axios)
- Créer un client :
  ```ts
  import axios from "axios";

  export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
  });
  ```

================================================================================
3) Backend (Django + DRF)
================================================================================
3.1 Créer le backend
- python -m venv .venv
- source .venv/bin/activate
- pip install django djangorestframework django-cors-headers gunicorn
- django-admin startproject <project_name> backend

3.2 Ajouter vos apps
- cd backend
- python manage.py startapp users (exemple)
- Ajouter dans `INSTALLED_APPS` :
  - rest_framework
  - corsheaders
  - users (ou autres apps)

3.3 Configurer CORS/CSRF
- Dans `settings.py` :
  - Ajouter "corsheaders.middleware.CorsMiddleware" dans MIDDLEWARE (haut de liste).
  - Configurer CORS_ALLOWED_ORIGINS
  - Configurer CSRF_TRUSTED_ORIGINS

3.4 Configurer PostgreSQL via variables d’environnement
- Installer psycopg :
  - pip install psycopg[binary]
- Exemple `DATABASES` :
  DB_HOST / DB_NAME / DB_USER / DB_PASS / DB_PORT

3.5 Créer `backend/.env.example` (sans secrets)
- Exemple :
  SECRET_KEY=change-me
  DEBUG=False
  DB_HOST=...
  DB_NAME=...
  DB_USER=...
  DB_PASS=...
  DB_PORT=5432
  CORS_ALLOWED_ORIGINS=https://<ton-frontend>.pages.dev
  CSRF_TRUSTED_ORIGINS=https://<ton-frontend>.pages.dev
  EMAIL_HOST=...

  EMAIL_PORT=587
  EMAIL_HOST_USER=...
  EMAIL_HOST_PASSWORD=...
  EMAIL_USE_TLS=True
  DEFAULT_FROM_EMAIL=...
  OTP_EMAIL_SUBJECT_PREFIX=[<ton-app>]

3.6 Charger les variables en local
- Installer python-dotenv ou utiliser `os.environ`.
- Option simple : créer `backend/.env` en local (ne pas commit).

3.7 OTP (email) fiable en production
- Recommandation simple : utiliser un fournisseur SMTP transactionnel :
  - Brevo/Sendinblue, Mailgun, SendGrid, Postmark, Amazon SES, etc.
- Paramètres SMTP recommandés :
  - PORT = 587
  - TLS activé (EMAIL_USE_TLS=True)
  - Authentification avec EMAIL_HOST_USER / EMAIL_HOST_PASSWORD
- Exemple de config Django (settings.py) :
  EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
  EMAIL_HOST = os.environ.get("EMAIL_HOST")
  EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
  EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
  EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
  EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
  DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

================================================================================
4) Dockeriser le backend (prod)
================================================================================
4.1 requirements.txt
- pip freeze > requirements.txt

4.2 Dockerfile (backend/Dockerfile)
- Exemple :
  FROM python:3.11-slim
  WORKDIR /app
  ENV PYTHONDONTWRITEBYTECODE=1
  ENV PYTHONUNBUFFERED=1
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["/app/entrypoint.sh"]

4.3 entrypoint.sh (backend/entrypoint.sh)
- Exemple :
  #!/bin/sh
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  gunicorn <project_name>.wsgi:application --bind 0.0.0.0:${PORT:-8000}

4.4 Rendre exécutable
- chmod +x backend/entrypoint.sh

================================================================================
5) Création d’un conteneur Docker (local)
================================================================================
5.1 Build de l’image
- cd backend
- docker build -t <repo>-backend:local .

5.2 Lancer en local
- docker run --rm -p 8000:8000 \
  -e PORT=8000 \
  -e DEBUG=True \
  -e SECRET_KEY=dev \
  -e DB_HOST=... \
  -e DB_NAME=... \
  -e DB_USER=... \
  -e DB_PASS=... \
  -e DB_PORT=5432 \
  <repo>-backend:local

5.3 Vérifier
- Ouvrir http://localhost:8000
- Vérifier /admin et /api

================================================================================
6) GHCR (GitHub Container Registry)
================================================================================
6.1 Activer GHCR
- Settings du repo → Packages → activer GHCR.

6.2 Workflow GitHub Actions
- Créer .github/workflows/backend.yml
- Objectif : build + push image Docker à chaque push sur main.
- Tag recommandé : ghcr.io/<user>/<repo>-backend:latest

Exemple minimal (adapter) :
```yaml
name: Build & Push Backend
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ghcr.io/<user>/<repo>-backend:latest
```

================================================================================
7) Base de données PostgreSQL (Koyeb)
================================================================================
- Koyeb → Databases → créer PostgreSQL
- Récupérer les Connection Details :
  DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

================================================================================
8) Déployer le backend sur Koyeb
================================================================================
8.1 Créer un service
- Koyeb → Create Service → "Pre-built Docker image"
- Image : ghcr.io/<user>/<repo>-backend:latest
- Port : 8000 (HTTP)

8.2 Variables d’environnement
- DEBUG=False
- SECRET_KEY=...
- DB_HOST / DB_NAME / DB_USER / DB_PASS / DB_PORT
- CORS_ALLOWED_ORIGINS=https://<ton-frontend>.pages.dev
- CSRF_TRUSTED_ORIGINS=https://<ton-frontend>.pages.dev
- EMAIL_* (si besoin)

8.3 Vérifier que Gunicorn écoute sur 0.0.0.0:$PORT

================================================================================
9) Déployer le frontend sur Cloudflare Pages
================================================================================
9.1 Créer un projet
- Cloudflare Pages → connecter le repo GitHub

9.2 Paramètres
- Root directory : frontend
- Build command : npm ci && npm run build
- Output directory : dist

9.3 Variables d’environnement (Production)
- VITE_API_URL=https://<ton-backend>.koyeb.app/api

================================================================================
10) CORS + CSRF (prod)
================================================================================
- CORS_ALLOWED_ORIGINS = domaine Cloudflare Pages
- CSRF_TRUSTED_ORIGINS = domaine Cloudflare Pages
- Ne pas laisser CORS_ALLOW_ALL_ORIGINS=True en prod.

================================================================================
11) CI/CD complet
================================================================================
- Push sur main → GitHub Actions build & push image (GHCR)
- Koyeb auto-deploy → redéploiement automatique
- Cloudflare Pages → rebuild automatique du frontend

================================================================================
12) Vérifications finales
================================================================================
- Tester /admin, /api/, et login frontend
- Vérifier que les requêtes front → back passent (pas d’erreur CORS)
- Vérifier que la DB est bien utilisée (pas sqlite)
- Vérifier les logs Koyeb (migrations, gunicorn OK)

================================================================================
13) Bonnes pratiques (optionnel mais recommandé)
================================================================================
- Ajouter un fichier .gitignore (node_modules, .env, etc.)
- Créer un script de migration/seed si besoin
- Utiliser un linter (flake8/ruff, eslint)
- Sauvegarder les secrets dans GitHub Secrets / Koyeb env vars

================================================================================
Astuce
================================================================================
Copier/coller ce fichier pour tout nouveau projet similaire.
