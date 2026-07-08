# Frontend README

This directory contains a production-ready Next.js 15 frontend for the SPARK AI Platform.

Setup

1. Install dependencies

   cd frontend
   npm install

2. Configure environment

   Create a .env.local in the frontend root with:

   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

3. Run dev

   npm run dev

Notes

- The frontend connects to the backend at NEXT_PUBLIC_API_URL. Ensure the backend is running.
- Authentication stores access_token and refresh_token in localStorage for simplicity. In production, prefer httpOnly secure cookies for refresh tokens.

