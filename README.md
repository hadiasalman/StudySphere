# StudySphere Campus

**Learn smarter. Plan better. Achieve more.**

StudySphere Campus is a Streamlit-based academic workspace designed to bring student learning, academic management, AI assistance, university services, and study productivity into one application.

**Current release:** `12.0`

---

## Overview

StudySphere provides a role-aware workspace for:

- Students
- Faculty
- University Administrators
- Creators / platform administrators

The application combines academic records, study planning, AI-powered assistance, document tools, university knowledge, attendance and fee management, learning analytics, integrations, and productivity tools.

The interface uses a navy-focused visual system with Light/Dark mode support and grouped sidebar navigation.

---

## Main Features

### Academic Management

- Dashboard with academic KPIs and quick actions
- Subject management
- Assignment management
- Exam management
- Study Planner
- Attendance tracking
- Student fee management
- Grades and GPA
- Student progress tracking

### AI & Learning Tools

- **AI Agent** with real actions against authorized StudySphere data
- Exam Preparation
- Adaptive Learning
- Academic Insights
- Syllabus Intelligence
- Multimodal AI Tutor for image-based learning help
- Voice Study Mode
- Coding Lab
- Research Workspace
- AI CV & Portfolio
- Presentation Studio
- Document Converter
- Image Compressor
- Flashcards & Quiz
- Focus Mode

### Documents & Knowledge

StudySphere supports uploaded academic material and document processing for formats such as:

- PDF
- DOCX
- PPTX
- TXT
- Markdown

The application also includes document chunking/retrieval and university knowledge functionality for source-grounded academic assistance.

### University & Institutional Features

- My University
- University Knowledge AI
- Career & Skills Roadmap
- Final Year Project (FYP) Project Manager
- Faculty Center
- Faculty AI
- University Admin
- Institutional Analytics
- Academic Support Queue
- Student enrollment and course administration
- Attendance session and attendance-record management
- University course material management

### Planning & Integrations

- Notifications & Calendar
- Downloadable academic calendar (`.ics`)
- LMS & Study Sync
- OneRoster CSV import support
- LTI 1.3 / LTI Advantage registration storage
- Google Drive / Google Slides integration support
- Optional University SSO using OpenID Connect

---

## User Roles

### Student

Students can manage their own subjects, assignments, exams, study tasks, attendance, fees, grades, learning progress, documents, AI tools, university resources, career planning, and FYP work.

### Faculty

Faculty users can work with assigned courses, manage class/roster data, upload teaching material, publish assignments, manage attendance, and use Faculty AI.

### University Administrator

University administrators can manage institutional data, courses, faculty assignments, students, fees, attendance infrastructure, analytics, integrations, and university resources according to their permissions.

### Creator

The Creator role provides higher-level platform configuration and deployment/administration capabilities, including deployment checks, configuration, backups where applicable, and institutional setup.

---

## AI Agent

The StudySphere AI Agent is designed as an **agentic AI workflow**, not only a text-generation chat interface.

The AI reasoning layer can invoke controlled application tools for authorized actions and data retrieval. Examples include:

- Reading the signed-in student's academic records
- Listing subjects
- Searching study material
- Creating subjects
- Creating exams
- Managing assignments/tasks through authorized tools

The agent is restricted to the signed-in user's permitted StudySphere data and actions.

The application also includes multimodal and learning-oriented AI workflows for images, adaptive learning, research, presentations, coding, and study guidance.

---

## Database Architecture

StudySphere supports **SQLite and PostgreSQL** through a small compatibility layer.

### Default: SQLite

When `DATABASE_URL` is not configured, the application uses:

```text
studysphere.db
```

SQLite is convenient for local development, demonstrations, and small deployments because it does not require a separate database server.

### Production Option: PostgreSQL

When `DATABASE_URL` is configured, StudySphere switches to PostgreSQL.

Example:

```text
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/studysphere
```

The application keeps its existing database-facing API while adapting SQL placeholders and a few SQLite/PostgreSQL differences through the compatibility layer.

> **Important:** The application supports PostgreSQL, but simply having PostgreSQL support in the code does not mean a deployment is already using PostgreSQL. The active backend depends on whether `DATABASE_URL` is configured.

---

## Data Storage

By default, the database file is:

```text
studysphere.db
```

The storage directory can be configured with:

```text
STUDYSPHERE_STORAGE_DIR=studysphere_data
```

Uploaded files and generated artifacts should be stored in a persistent location when deploying to an environment where the local filesystem may be ephemeral.

---

## Authentication & Security

StudySphere supports two authentication approaches:

### Local account authentication

- Email + password sign-in
- Password hashing using salted PBKDF2-SHA256
- Recovery-code based password reset flow
- Role-based access control
- Account status management
- Audit logging for important account/administrative actions

### University SSO

StudySphere can optionally use Streamlit OpenID Connect for a university identity provider.

The university password is handled by the identity provider rather than stored in StudySphere.

Example Streamlit Secrets structure:

```toml
[auth]
redirect_uri = "https://YOUR-APP.streamlit.app/oauth2callback"
cookie_secret = "YOUR-LONG-RANDOM-SECRET"

[auth.university]
client_id = "YOUR-CLIENT-ID"
client_secret = "YOUR-CLIENT-SECRET"
server_metadata_url = "https://YOUR-IDP/.well-known/openid-configuration"
```

Do not commit passwords, API keys, client secrets, recovery codes, or database credentials to source control.

---

## AI Configuration

The AI features use Gemini APIs.

A Gemini API key can be supplied through Streamlit Secrets or the configured application settings.

Recommended Streamlit Secret:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

AI features gracefully report configuration or quota problems instead of exposing secret values.

---

## Optional Google Integration

Google Drive / Google Slides export can be enabled with the required Google API credentials.

Relevant configuration values include:

```text
GOOGLE_SERVICE_ACCOUNT_JSON=...
GOOGLE_DRIVE_FOLDER_ID=...
GOOGLE_SLIDES_SHARE_WITH_USER=false
```

The Presentation Studio can generate downloadable PowerPoint files and can export to Google Slides when the Google integration is correctly configured.

---

## Python Requirements

The deployment bundle generated by the application specifies these core packages:

```text
streamlit>=1.40,<2
pypdf>=5.0
python-docx>=1.1
reportlab>=4.2
python-pptx>=1.0
Pillow>=10.0
google-api-python-client>=2.170.0
google-auth>=2.40.0
Authlib>=1.3.2
psycopg[binary]>=3.2
```

---

## Local Installation

### 1. Clone or copy the project

Place the following files in your project directory:

```text
app.py
requirements.txt
```

Add `.streamlit/secrets.toml` when secrets are required.

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run StudySphere

```bash
streamlit run app.py
```

The Streamlit server will display the local URL in the terminal, normally similar to:

```text
http://localhost:8501
```

---

## Suggested `requirements.txt`

Use the following dependency list for the current application:

```text
streamlit>=1.40,<2
pypdf>=5.0
python-docx>=1.1
reportlab>=4.2
python-pptx>=1.0
Pillow>=10.0
google-api-python-client>=2.170.0
google-auth>=2.40.0
Authlib>=1.3.2
psycopg[binary]>=3.2
```

---

## Environment Variables / Secrets

Common configuration values used by the application include:

| Variable | Purpose | Default / Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | Empty = SQLite |
| `STUDYSPHERE_DB_PATH` | SQLite database path | `studysphere.db` |
| `STUDYSPHERE_ENV` | Deployment environment label | `development` |
| `STUDYSPHERE_TIMEZONE` | Application timezone | `Asia/Karachi` |
| `GEMINI_API_KEY` | Gemini API access | Required for AI features |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Drive/Slides credentials | Optional |
| `GOOGLE_DRIVE_FOLDER_ID` | Optional Google Drive folder | Optional |
| `GOOGLE_SLIDES_SHARE_WITH_USER` | Optional Slides sharing behavior | `false` |
| `STUDYSPHERE_STORAGE_DIR` | Persistent file storage directory | `studysphere_data` |

For Streamlit deployment, sensitive values should normally be placed in **Streamlit Secrets** rather than committed to the repository.

---

## Streamlit Cloud Deployment

1. Push the project to your Git repository.
2. Set the main application file to `app.py`.
3. Add `requirements.txt`.
4. Configure required secrets in Streamlit Cloud.
5. Deploy the application.
6. For PostgreSQL, add `DATABASE_URL` before deployment or restart after adding it.
7. For Gemini-powered features, add `GEMINI_API_KEY`.
8. For Google Slides export, add the required Google credentials and folder settings.

For production use, prefer a managed PostgreSQL database and persistent file storage rather than relying only on a local SQLite file.

---

## Navigation & Browser History

StudySphere uses grouped sidebar navigation and page-state navigation.

Internal page navigation is designed to preserve page state in the URL so that browser **Back** and **Forward** navigation can move between StudySphere pages instead of immediately leaving the application.

Example flow:

```text
Dashboard → Subjects → Exams

Back:
Exams → Subjects → Dashboard

Forward:
Dashboard → Subjects → Exams
```

The browser history behavior depends on the deployed Streamlit frontend and the current application navigation implementation.

---

## Application Structure

The current application is intentionally organized as a single Streamlit entry point with supporting helper functions and database compatibility code.

```text
StudySphere/
├── app.py
├── requirements.txt
├── README.md
├── studysphere.db              # created when SQLite is active
├── studysphere_data/           # optional persistent file storage
└── .streamlit/
    └── secrets.toml            # local secrets; do not commit
```

### Important internal layers

```text
Streamlit UI
    ↓
Session State / Authentication
    ↓
Role & Permission Checks
    ↓
Application Feature Functions
    ↓
SQLite / PostgreSQL Compatibility Layer
    ↓
Database

AI features
    ↓
Gemini API
    ↓
Controlled StudySphere tools / source retrieval
```

---

## Database Areas

The current schema contains tables covering areas such as:

- Users and authentication
- Institutions and departments
- Subjects, assignments, exams, and tasks
- Attendance
- Student fees and fee history
- Grades / learning attempts / learning mistakes
- Documents and document chunks
- Chat sessions and messages
- Faculty and course management
- University course materials and knowledge sources
- Academic support cases
- Syllabus topics
- Research projects and sources
- FYP projects and milestones
- Student AI privacy/preferences
- Integrations, sync runs, external mappings, and LTI registrations
- Audit logs and application settings

The exact schema may evolve through the application's schema migration logic.

---

## Backup

When SQLite is active, StudySphere includes an application-level logical SQLite backup mechanism.

For PostgreSQL deployments, use database-native backup tooling or managed-provider backups, such as `pg_dump` or the provider's automated backup system.

Do not store secrets inside database backups or public deployment bundles.

---

## Troubleshooting

### `PostgreSQL support is enabled ... but psycopg is not installed`

Install the PostgreSQL dependency:

```bash
pip install "psycopg[binary]>=3.2"
```

### `StudySphere could not connect to PostgreSQL`

Check:

- `DATABASE_URL`
- Database hostname
- Port
- Username/password
- Database availability
- Firewall/network access

### AI features are unavailable

Confirm that `GEMINI_API_KEY` is configured and valid.

If the key is configured but requests fail with a quota/rate-limit message, the issue is with Gemini API availability or quota rather than the StudySphere database.

### PDF/DOCX/PPTX processing is unavailable

Confirm that these packages are installed:

```bash
pip install pypdf python-docx python-pptx reportlab Pillow
```

### Google Slides export is unavailable

Confirm that the Google API packages and credentials are configured correctly and that the service account has access to the target Drive/folder.

---

## Development Notes

- Keep database credentials and API secrets outside source control.
- Use SQLite for simple local development and demos.
- Use PostgreSQL for larger multi-user deployments.
- Keep uploaded-file storage on persistent storage when the deployment platform uses ephemeral filesystems.
- Test role permissions after changing navigation or database schema.
- When adding new pages, keep page IDs, navigation labels, permission checks, and page handlers synchronized.

---

## License

No explicit open-source license is defined in the current project. Add the appropriate license here if this project will be distributed publicly.

---

## Project

**StudySphere Campus**  
Learn smarter. Plan better. Achieve more.
