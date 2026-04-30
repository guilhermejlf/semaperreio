---
phase: 02-family-group
plan: 01
status: completed
date_completed: 2026-04-30
---

# Summary: Backend Family Group

## What Was Accomplished

- Created `Family` model in `api/models.py`:
  - `name` (CharField 100), `code` (6-char uppercase unique, auto-generated), `code_expires_at` (DateTimeField, default +7 days)
  - `created_by` (FK User), `created_at` (auto_now_add)
  - `regenerate_code()` method
- Created `FamilyMembership` model:
  - `user` (OneToOneField User), `family` (FK Family), `role` (admin/member, default=member), `joined_at`
  - `unique_together` on [user, family]
- Added `family = ForeignKey(Family, null=True, on_delete=SET_NULL)` to `Gasto` and `Receita` models
- Created `api/views_family.py` with `FamilyViewSet` (ModelViewSet + @action methods):
  - `GET /api/family/` — retrieve current user's family (404 if none)
  - `POST /api/family/` — create family, auto-generate code, set creator as admin
  - `DELETE /api/family/` — delete family (admin only)
  - `POST /api/family/join/` — join via code, validate expiry, reject if already in family
  - `POST /api/family/leave/` — leave family
  - `POST /api/family/regenerate-code/` — admin only, new code + 7-day expiry
  - `DELETE /api/family/members/<user_id>/` — admin only, remove member
- Updated `api/views.py` gastos CRUD to filter by family (user's family OR own gastos with no family)
- Created `api/permissions.py` with `GastoPermission` for edit/delete ownership checks
- Added serializers for Family, Membership, Detail, Join, Create, RegenerateCode

## Key Decisions

- `FamilyMembership` is OneToOneField per user — one user belongs to exactly one family
- Pre-join gastos remain private (not retroactively linked)
- Gastos created after joining auto-get `family` set by backend

## Files Created/Modified

- `api/models.py` (Family, FamilyMembership, family FK on Gasto/Receita)
- `api/views_family.py` (new)
- `api/serializers.py` (Family serializers)
- `api/permissions.py` (new)
- `api/urls.py` (family router)
- Migrations updated

## Verification

- [x] `POST /api/family/` creates family with 6-char code
- [x] `GET /api/family/` returns 404 when user has no family
- [x] `POST /api/family/join/` with valid code creates membership
- [x] `POST /api/family/join/` with expired code returns 400
- [x] `POST /api/family/join/` when already in family returns 400
- [x] Admin can remove members; member cannot
- [x] Gastos filtered by family context

## Notes

Implemented outside formal `/gsd-execute-phase` workflow. Committed in `8a0ac9f`.
