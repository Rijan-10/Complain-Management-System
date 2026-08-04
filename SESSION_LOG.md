# Session Log

## Session 1 — July 30, 2026

### Summary
- Explored existing codebase: Complaint Management System (frontend HTML + SQL schema)
- Read proposal PDF: "Complaint Management System Based on GPS and Photo Upload Technology"
- User wants to set up Django backend with MySQL
- Django 6.0.7 and mysqlclient 2.2.8 are already installed
- MySQL Server needs to be installed

### Current Status
- **Database:** MariaDB 11.4.2 running on port 3306 (portable install, no admin needed)
- **Django:** Connected to MariaDB (`project` database), migrated and working
- **Home page:** Running at http://localhost:8000 — Login button linked to `/login/`
- **Login page:** Working with Django auth — POST to `/login/`, error messages displayed
- **Auth:** Custom `EmailAuthBackend` — users log in with email instead of username
- **Superuser:** admin@example.com / admin123
- **Branch:** `dev` — all changes committed

### Next Steps
1. Create Django models matching Project.sql schema (users, complaints, categories, etc.)
2. Wire up Sign Up, New Complaint, Dashboard, etc.
3. Serve admin HTML pages via Django
