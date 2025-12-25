# Build Smart Hub ✅

**Portal for Home Makers** — a Django-based web portal that connects homeowners with service providers (architects, builders, interior designers, vendors, etc.). This repository contains the Django project and a sample `demo` app with templates, static assets, and management utilities to populate sample data.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Sample Data](#sample-data)
- [Project Structure](#project-structure)
- [Development Notes](#development-notes)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features ✨

- Django-based web application with a `demo` app and templates
- Static assets and media upload support (logo/profile images)
- Management command to create sample profiles
- Uses SQLite by default for quick local development

---

## Prerequisites 🔧

- Python 3.8+ (3.10/3.11 recommended)
- pip
- Optional: virtual environment tool (venv, virtualenv)

Note: If a `requirements.txt` file is missing, install core dependencies with: `pip install django pillow` (add other libraries as needed).

---

## Quick Start 🚀

1. Clone the repo:

```bash
git clone <repo-url>
cd djangify_demo
```

2. Create and activate a virtual environment (Windows):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1  # or venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
# Or if none exists
pip install django pillow
```

4. Run migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. (Optional) Collect static files for production:

```bash
python manage.py collectstatic
```

6. Run the development server:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

---

## Sample Data 🧪

This project includes a management command to create sample profiles for local development:

```bash
python manage.py create_sample_profiles
```

Use this to populate the site with demo users and profiles.

---

## Project Structure 📁

- `djangify_demo/` — Django project settings and URL configuration
- `demo/` — main app containing models, views, templates and management commands
- `demo/templates/` — HTML templates (see `demo/templates/demo/Modified_files`)
- `static/` — CSS, JS and image assets
- `media/` — uploaded media (profile images, logos)
- `db.sqlite3` — default development database

---

## Development Notes 🔧

- Static and media paths are configured in settings; in production, serve media from a proper storage backend (S3, etc.).
- Add environment-specific secrets (SECRET_KEY, DEBUG, DB settings) via environment variables or a `.env` file.
- To add sample data or modify how it's created, inspect `demo/management/commands/create_sample_profiles.py`.

---

## Testing ✅

Run Django tests with:

```bash
python manage.py test
```

---

## Contributing 🤝

Contributions are welcome. Suggested workflow:

1. Fork the repo
2. Create a feature branch
3. Make changes and add tests
4. Open a pull request with a clear description

Please include a short description of changes and any migration notes.

---

## License

This project does not include an explicit license file. Add a `LICENSE` (e.g., MIT) if you intend to open-source it.

---

## Screenshots / Demo 🎬

Below are placeholder demo images — replace with real screenshots or recorded GIFs from your running site.

![Home screen](docs/screenshots/screenshot_home.svg)

![Demo animation](docs/screenshots/demo_animation.svg)

---

If you want, I can also:
- Add real screenshots or record demo GIFs if you provide images or give me instructions to capture them
- Create a `requirements.txt` (generated and added to the repo)
- Add a `CONTRIBUTING.md` or `LICENSE`

Feel free to tell me which additions you'd like. 🔧