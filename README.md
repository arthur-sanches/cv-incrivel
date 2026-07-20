# CV Incrível

AI-powered CV tailoring for real job applications.

Upload your resume once, paste a job description, and get a polished, ATS-friendly CV tailored to that role — ready to download as PDF.

---

## What it does

**CV Incrível** helps you stop rewriting your résumé from scratch for every opening. The flow is simple:

1. **Sign in** with your account  
2. **Set up your profile** by uploading an existing resume (PDF or DOCX)  
3. **Review and edit** the extracted career data (experience, skills, education, and more)  
4. **Generate a tailored CV** from any job description  
5. **Download** the result as a PDF (and manage previous generations)

Under the hood, the app uses [OpenRouter](https://openrouter.ai/) to:

- Extract structured data from your resume  
- Rewrite and tailor content to the target job (metrics-focused, ATS-oriented)  
- Keep section headings and language aligned with the job description  

Personal contact details you provide during setup are redacted from the text before it is sent to the model, so name, email, phone, and address stay under your control in the final document.

---

## Features

- **Resume upload** — PDF and DOCX support  
- **AI extraction** — turns free-form resume text into structured profile data  
- **Profile editing** — refine summary, experience, skills, education, certificates, languages, and links  
- **Job-specific generation** — paste a description and get a tailored CV  
- **PDF export** — clean multi-section layout via WeasyPrint  
- **CV library** — list, re-download, edit, and delete past generations  
- **Email-based auth** — custom user model (no public self-signup; users are created by an admin)

---

## Tech stack

| Layer | Choice |
|--------|--------|
| Backend | [Django](https://www.djangoproject.com/) 6 |
| Database | SQLite (default, great for local use) |
| AI | [OpenRouter](https://openrouter.ai/) Python SDK |
| PDF | [WeasyPrint](https://weasyprint.org/) |
| Resume parsing | pdfplumber, python-docx |
| Config | python-dotenv |

---

## Project layout

```text
cv-incrivel/
├── ai_integration/   # OpenRouter client wrapper
├── cvincrivel/       # Django project settings & root URLs
├── generate_cv/      # CV generation, templates, PDF download
├── login/            # Authentication (email-based user)
├── profile/          # Edit saved resume/profile data
├── resume/           # Upload + first-time profile setup
├── templates/        # Shared base template
├── manage.py
├── requirements.txt
└── .env              # Local secrets (not committed)
```

---

## Prerequisites

- **Python 3.12+** (3.14 works with the pinned deps)  
- **pip** and **venv**  
- An **[OpenRouter](https://openrouter.ai/) API key**  
- System libraries required by **WeasyPrint** (see [WeasyPrint installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) if PDF generation fails)

On Debian/Ubuntu you may need packages such as:

```bash
sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info
```

---

## Quick start

### 1. Clone the repository

```bash
git clone git@github.com:arthur-sanches/cv-incrivel.git
cd cv-incrivel
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-long-random-string
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Generate a Django secret key, for example:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> Never commit `.env`. It is listed in `.gitignore`.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create an admin user

There is no public registration page. Create your first user with:

```bash
python manage.py createsuperuser
```

You will be prompted for **email** and **password** (this project uses email instead of username).

### 7. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). You will be redirected to the login page.

---

## Using the app

| Step | URL | What to do |
|------|-----|------------|
| Log in | `/login/` | Use the superuser (or any user created in admin) |
| Profile setup | `/profile_setup/` | Upload a PDF/DOCX resume and optional contact fields |
| Edit profile | `/profile/` | Adjust extracted data anytime |
| Generate CV | `/generate_cv/` | Paste a job description and generate |
| Your CVs | `/generate_cv/` (list) | Download, edit, or delete previous CVs |
| Django admin | `/admin/` | Manage users and data |

Typical first session:

1. Log in  
2. Complete **profile setup** (upload + confirm personal info)  
3. Open **Generate CV**, paste a job description, generate  
4. Download the PDF and iterate as needed  

---

## Configuration reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `OPENROUTER_API_KEY` | Yes (for AI features) | OpenRouter API key |

Related settings live in `cvincrivel/settings.py`:

- `OPENROUTER_MODEL` — model id used for generation (default is set in code)  
- `DEBUG` — currently `True` for local development; turn off for any real deployment  
- `ALLOWED_HOSTS` — empty by default; set this before deploying  

---

## Development notes

```bash
# Run the test suite
python manage.py test

# Open a Django shell
python manage.py shell
```

**WeasyPrint** needs working system fonts and Cairo/Pango stacks. If PDF download errors mention missing libraries, install the OS packages linked above and retry.

AI calls incur **OpenRouter usage costs**. Keep your API key private and monitor usage in the OpenRouter dashboard.

---

## Security notes

- Keep `.env` and `db.sqlite3` out of version control (already gitignored).  
- Do not commit real API keys or production secrets.  
- This project is set up for **local / trusted use**. Before any public deployment, set `DEBUG=False`, configure `ALLOWED_HOSTS`, use HTTPS-related cookie settings, and protect `/admin/`.  
- Resume content (minus redacted contact fields) is sent to OpenRouter to power extraction and generation.

---

## License

No license file is included yet. All rights reserved by the author unless otherwise stated.
