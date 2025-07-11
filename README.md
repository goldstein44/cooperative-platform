# Cooperative Management Platform

A platform for cooperatives to manage members, contributions, dues, penalties, transactions, income/expenses, payment tracking, and attendance. Built with Flask, Nest.js, Supabase, Paystack, Termii, and Redis.

## Setup Instructions
1. Clone the repository: `git clone https://github.com/goldstein4/cooperative-platform.git`
2. Set up the backend (see `backend/README.md`).
3. Set up the frontend (see `frontend/README.md`).
4. Configure Supabase, Paystack, Termii, and Redis (see `docs/setup.md`).

## Tech Stack
- Backend: Flask (Python)
- Frontend: Nest.js (TypeScript)
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth
- Payments: Paystack
- SMS: Termii
- Hosting: Firebase (frontend), Render (backend)
- Caching: Redis
- CI/CD: GitHub Actions
- IaC: Terraform
- Security: Snyk, Dependabot

## Folder Structure
- `backend/`: Flask backend code
- `frontend/`: Nest.js frontend code
- `infrastructure/`: Terraform configs
- `docs/`: Documentation
- `.github/workflows/`: CI/CD pipelines

## License
MIT