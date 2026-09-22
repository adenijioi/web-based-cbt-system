# Web-Based CBT Assessment System

Research project: **Development and Implementation of a Web-Based Computer-Based Test System for Student Assessment Using Python**

- Researcher: Ogunbode Ayishat Morenikeji
- Supervisor: Adeniji O. Israel

## Features

- Multiple courses identified by course code
- Protected administrator dashboard
- Excel question-bank upload and validation
- Preview and activation workflow
- 20 randomly selected questions per student
- Shuffled answer options
- 15-minute countdown and automatic submission
- Automatic marking and immediate student result
- One attempt per course for each matriculation number and examination number
- PostgreSQL persistence
- Administrator result search view and Excel export
- Mobile-friendly interface

## Excel upload columns

The first worksheet must use these exact columns in the first row:

`Question | Option A | Option B | Option C | Option D | Correct Answer | Mark`

`Correct Answer` may contain A, B, C or D, or the exact text of the correct option. At least 20 valid questions are required.

## Local setup

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and configure the values in your shell or environment manager.
4. Run `flask --app app run`.

For a quick local launch, export `ADMIN_PASSWORD` before starting the application. SQLite is used locally when `DATABASE_URL` is not set.

## Production deployment

The project includes `render.yaml`. Add the following secrets in Render:

- `DATABASE_URL`: a persistent PostgreSQL connection string
- `ADMIN_PASSWORD`: a strong administrator password

Render generates `SECRET_KEY`. Do not commit credentials to GitHub.

The application is compatible with a persistent external PostgreSQL service such as Neon. This avoids reliance on an expiring Render free PostgreSQL instance.
