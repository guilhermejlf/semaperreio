---
phase: 01-authentication
plan: 01
status: completed
date_completed: 2026-04-30
---

# Summary: Backend JWT Authentication

## What Was Accomplished

- Added `djangorestframework-simplejwt` to `requirements.txt`
- Configured JWT in `backend/settings.py`:
  - `JWTAuthentication` as default auth class
  - `IsAuthenticated` as default permission class
  - `ACCESS_TOKEN_LIFETIME=30min`, `REFRESH_TOKEN_LIFETIME=7days`
- Created `api/views_auth.py` with `RegisterView`, `LoginView` (TokenObtainPairView), `RefreshView` (TokenRefreshView)
- Created `api/serializers_auth.py` with `RegisterSerializer` (username, email, password, first_name, email uniqueness validation)
- Added `user = ForeignKey(User)` to `Gasto` model; reset SQLite and recreated migrations
- Protected all gastos endpoints: filter by `request.user`, save with `user=request.user`
- Added auth routes: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/user/`

## Key Decisions

- Used default Django `User` model (not custom) — sufficient for MVP
- SQLite reset accepted — MVP data loss acceptable per discuss-phase
- Global `IsAuthenticated` permission with `AllowAny` override on auth endpoints

## Files Created/Modified

- `api/views_auth.py` (new)
- `api/serializers_auth.py` (new)
- `api/models.py` (added `user` FK to Gasto)
- `api/urls.py` (added auth routes)
- `backend/settings.py` (JWT config)
- `requirements.txt` (added simplejwt)
- Migrations recreated

## Verification

- [x] `python manage.py check` passes
- [x] `POST /api/auth/register/` returns 201
- [x] `POST /api/auth/login/` returns access + refresh tokens
- [x] `POST /api/auth/refresh/` returns new access token
- [x] `GET /api/gastos/` without token returns 401
- [x] `GET /api/gastos/` with Bearer token returns user's own gastos only

## Notes

Implemented outside formal `/gsd-execute-phase` workflow. Code verified by manual testing and committed in `8a0ac9f`.
