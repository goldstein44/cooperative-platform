# Architecture Overview

## System Design
- **Backend**: Flask (Python) for RESTful APIs, handling business logic and integrations.
- **Frontend**: Nest.js (TypeScript) for a scalable, mobile-friendly UI.
- **Database**: Supabase (PostgreSQL) with Row-Level Security for multi-tenant data.
- **Auth**: Supabase Auth for email/phone-based user management.
- **Payments**: Paystack for registration, contributions, dues, and penalties.
- **SMS**: Termii for automated reminders (dues, penalties, meetings).
- **Caching**: Redis for performance optimization.
- **Hosting**: Firebase (frontend), Render (backend, Redis).
- **CI/CD**: GitHub Actions for automated testing and deployment.
- **IaC**: Terraform for infrastructure management.
- **Security**: Snyk for vulnerability scanning, Dependabot for dependency updates.

## Folder Structure
- `backend/`: Flask app, routes, models, services, and tests.
- `frontend/`: Nest.js app, components, pages, and services.
- `infrastructure/`: Terraform configs for Supabase, Firebase, Render, Redis.
- `docs/`: Setup guides, API specs, and architecture details.
- `.github/workflows/`: CI/CD pipelines.

## Authentication
- Supabase Auth handles user management with email and phone providers.
- Roles: super_admin (manages cooperative and users), admin (manages contributions, dues, etc.), member (views data).
- RLS policies ensure data isolation per cooperative and role-based access.