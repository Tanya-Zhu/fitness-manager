# Tasks: 健身计划管理

**Input**: Design documents from `/specs/001-fitness-plan-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per Constitution principle IV (TDD). Tests must be written FIRST and FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per implementation plan (src/, tests/, alembic/)
- [ ] T002 Initialize Python 3.11 project with virtual environment
- [x] T003 [P] Create requirements.txt with core dependencies (FastAPI, SQLAlchemy, asyncpg, APScheduler, Pydantic, python-jose, passlib)
- [x] T004 [P] Create requirements-dev.txt with testing dependencies (pytest, pytest-asyncio, pytest-cov, httpx, Factory Boy)
- [x] T005 [P] Create .env.example file with environment variable templates
- [x] T006 [P] Create docker-compose.yml for PostgreSQL and Redis services
- [x] T007 [P] Configure linting and formatting tools (.flake8, .black, pyproject.toml)
- [x] T008 Create .gitignore file (venv/, __pycache__/, .env, *.pyc)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create core configuration module in src/core/config.py (load environment variables)
- [x] T010 [P] Setup database connection and session management in src/core/database.py (SQLAlchemy async engine, session factory)
- [x] T011 [P] Create base SQLAlchemy model class in src/core/database.py
- [x] T012 [P] Implement JWT token generation and verification in src/core/security.py
- [x] T013 [P] Implement password hashing utilities (bcrypt) in src/core/security.py
- [x] T014 [P] Create authentication middleware in src/api/middleware/auth.py (JWT verification, get_current_user dependency)
- [x] T015 [P] Create request validation middleware in src/api/middleware/validation.py
- [x] T016 [P] Create User model in src/models/user.py (id, email, password_hash, created_at, updated_at)
- [x] T017 Setup FastAPI application instance in src/main.py (CORS, middleware registration)
- [x] T018 Create unified error response handler in src/api/middleware/error_handler.py
- [x] T019 Initialize Alembic for database migrations
- [x] T020 Create initial migration script for User table
- [ ] T021 Apply database migrations (alembic upgrade head)
- [x] T022 Create health check endpoint in src/api/routes/health.py (GET /health)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 创建个性化健身计划 (Priority: P1) 🎯 MVP

**Goal**: 用户可以创建包含锻炼项目、时长和频率的健身计划

**Independent Test**: 用户可以独立完成创建健身计划的全流程，从输入计划名称、选择锻炼项目到保存计划，并能在计划列表中查看到新创建的计划。

### Tests for User Story 1 (TDD Required) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US1] Contract test for POST /api/v1/plans in tests/contract/test_plans_api_contract.py
- [x] T024 [P] [US1] Contract test for GET /api/v1/plans in tests/contract/test_plans_api_contract.py
- [x] T025 [P] [US1] Contract test for GET /api/v1/plans/{planId} in tests/contract/test_plans_api_contract.py
- [x] T026 [P] [US1] Integration test for complete plan creation flow in tests/integration/test_plan_creation.py
- [x] T027 [P] [US1] Integration test for validation errors (empty name, no exercises) in tests/integration/test_plan_creation.py

### Implementation for User Story 1

- [x] T028 [P] [US1] Create FitnessPlan model in src/models/fitness_plan.py (id, user_id, name, description, status, timestamps)
- [x] T029 [P] [US1] Create Exercise model in src/models/exercise.py (id, plan_id, name, duration_minutes, repetitions, intensity, order_index)
- [x] T030 [US1] Create Alembic migration for fitness_plan and exercise tables
- [ ] T031 [US1] Apply migration (alembic upgrade head)
- [x] T032 [P] [US1] Create Pydantic schemas for plan creation request in src/api/schemas/plan_schemas.py (CreateExerciseRequest, FitnessPlanCreate)
- [x] T033 [P] [US1] Create Pydantic schemas for plan responses in src/api/schemas/plan_schemas.py (Exercise, FitnessPlanSummary, FitnessPlanDetail)
- [x] T034 [US1] Implement PlanService.create_plan() in src/services/plan_service.py (validate, create plan, add exercises, commit transaction)
- [x] T035 [US1] Implement PlanService.get_user_plans() in src/services/plan_service.py (filter by user_id and deleted_at, support pagination)
- [x] T036 [US1] Implement PlanService.get_plan_by_id() in src/services/plan_service.py (verify ownership, include exercises)
- [x] T037 [US1] Create POST /api/v1/plans endpoint in src/api/routes/plans.py (create plan, return 201)
- [x] T038 [US1] Create GET /api/v1/plans endpoint in src/api/routes/plans.py (list plans with pagination)
- [x] T039 [US1] Create GET /api/v1/plans/{planId} endpoint in src/api/routes/plans.py (plan details)
- [x] T040 [US1] Add validation for plan name (non-empty, max 50 chars) in CreateFitnessPlanRequest
- [x] T041 [US1] Add validation for exercises (min 1 exercise, duration_minutes or repetitions required) in CreateExerciseRequest
- [x] T042 [US1] Register plans router in src/main.py
- [x] T043 [US1] Unit test for PlanService.create_plan() in tests/unit/test_plan_service.py
- [x] T044 [US1] Unit test for data validators in tests/unit/test_validators.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 3 - 接收健身提醒通知 (Priority: P1) 🎯 MVP

**Goal**: 用户在计划时间收到推送通知，帮助养成规律的健身习惯

**Independent Test**: 用户可以为健身计划设置提醒时间，并在指定时间收到通知，通知包含计划名称和锻炼内容摘要。

**Note**: US3 before US2 because reminder functionality is P1 (MVP critical) while editing is P2.

### Tests for User Story 3 (TDD Required) ⚠️

- [x] T045 [P] [US3] Contract test for POST /api/v1/plans/{planId}/reminders in tests/contract/test_plans_api_contract.py
- [x] T046 [P] [US3] Contract test for PUT /api/v1/plans/{planId}/reminders/{reminderId} in tests/contract/test_plans_api_contract.py
- [x] T047 [P] [US3] Contract test for DELETE /api/v1/plans/{planId}/reminders/{reminderId} in tests/contract/test_plans_api_contract.py
- [x] T048 [P] [US3] Integration test for setting up reminders in tests/integration/test_plan_reminders.py
- [x] T049 [P] [US3] Integration test for reminder notification delivery (mock APScheduler) in tests/integration/test_plan_reminders.py

### Implementation for User Story 3

- [x] T050 [P] [US3] Create Reminder model in src/models/reminder.py (id, plan_id, reminder_time, frequency, days_of_week, is_enabled, timestamps)
- [x] T051 [US3] Create Alembic migration for reminder table
- [ ] T052 [US3] Apply migration (alembic upgrade head)
- [x] T053 [P] [US3] Create Pydantic schemas for reminders in src/api/schemas/reminder_schemas.py (CreateReminderRequest, UpdateReminderRequest, Reminder)
- [x] T054 [US3] Initialize APScheduler with Redis job store in src/services/reminder_service.py
- [x] T055 [US3] Implement ReminderService.create_reminder() in src/services/reminder_service.py (save to DB, schedule APScheduler job)
- [x] T056 [US3] Implement ReminderService.update_reminder() in src/services/reminder_service.py (update DB, reschedule job)
- [x] T057 [US3] Implement ReminderService.delete_reminder() in src/services/reminder_service.py (delete from DB, remove APScheduler job)
- [x] T058 [US3] Implement ReminderService.schedule_job() helper in src/services/reminder_service.py (parse time, create CronTrigger)
- [x] T059 [P] [US3] Implement NotificationService.send_push_notification() in src/services/notification_service.py (format message, call push API)
- [x] T060 [US3] Create reminder callback function in src/services/reminder_service.py (fetch plan, call NotificationService)
- [x] T061 [US3] Create POST /api/v1/plans/{planId}/reminders endpoint in src/api/routes/plans.py
- [x] T062 [US3] Create PUT /api/v1/plans/{planId}/reminders/{reminderId} endpoint in src/api/routes/plans.py
- [x] T063 [US3] Create DELETE /api/v1/plans/{planId}/reminders/{reminderId} endpoint in src/api/routes/plans.py
- [x] T064 [US3] Add validation for reminder_time format (HH:MM:SS) in CreateReminderRequest
- [x] T065 [US3] Add validation for days_of_week (array of 1-7) in CreateReminderRequest
- [x] T066 [US3] Start APScheduler on FastAPI startup event in src/main.py
- [x] T067 [US3] Shutdown APScheduler on FastAPI shutdown event in src/main.py
- [x] T068 [US3] Unit test for ReminderService scheduling logic in tests/unit/test_reminder_service.py
- [x] T069 [US3] Unit test for NotificationService message formatting in tests/unit/test_notification_service.py

**Checkpoint**: User Stories 1 AND 3 (MVP) should both work independently

---

## Phase 5: User Story 2 - 管理现有健身计划 (Priority: P2)

**Goal**: 用户可以查看、编辑和删除已有计划

**Independent Test**: 用户可以在计划列表中选择任一计划进行查看、编辑（修改锻炼项目或时间）或删除，并看到变更立即生效。

### Tests for User Story 2 (TDD Required) ⚠️

- [x] T070 [P] [US2] Contract test for PUT /api/v1/plans/{planId} in tests/contract/test_plans_api_contract.py
- [x] T071 [P] [US2] Contract test for DELETE /api/v1/plans/{planId} in tests/contract/test_plans_api_contract.py
- [x] T072 [P] [US2] Contract test for POST /api/v1/plans/{planId}/exercises in tests/contract/test_plans_api_contract.py
- [x] T073 [P] [US2] Contract test for PUT /api/v1/plans/{planId}/exercises/{exerciseId} in tests/contract/test_plans_api_contract.py
- [x] T074 [P] [US2] Contract test for DELETE /api/v1/plans/{planId}/exercises/{exerciseId} in tests/contract/test_plans_api_contract.py
- [x] T075 [P] [US2] Integration test for plan CRUD operations in tests/integration/test_plan_management.py

### Implementation for User Story 2

- [x] T076 [P] [US2] Create Pydantic schemas for updates in src/api/schemas/plan_schemas.py (UpdateFitnessPlanRequest, UpdateExerciseRequest)
- [x] T077 [US2] Implement PlanService.update_plan() in src/services/plan_service.py (update name and description)
- [x] T078 [US2] Implement PlanService.delete_plan() in src/services/plan_service.py (soft delete: set deleted_at, cancel reminders)
- [x] T079 [US2] Implement ExerciseService.add_exercise() in src/services/exercise_service.py (add to existing plan)
- [x] T080 [US2] Implement ExerciseService.update_exercise() in src/services/exercise_service.py
- [x] T081 [US2] Implement ExerciseService.delete_exercise() in src/services/exercise_service.py (check min 1 exercise rule)
- [x] T082 [US2] Create PUT /api/v1/plans/{planId} endpoint in src/api/routes/plans.py
- [x] T083 [US2] Create DELETE /api/v1/plans/{planId} endpoint in src/api/routes/plans.py
- [x] T084 [US2] Create POST /api/v1/plans/{planId}/exercises endpoint in src/api/routes/plans.py
- [x] T085 [US2] Create PUT /api/v1/plans/{planId}/exercises/{exerciseId} endpoint in src/api/routes/plans.py
- [x] T086 [US2] Create DELETE /api/v1/plans/{planId}/exercises/{exerciseId} endpoint in src/api/routes/plans.py
- [x] T087 [US2] Add business rule validation (prevent deleting last exercise) in ExerciseService
- [x] T088 [US2] Update ReminderService.delete_plan() integration to cancel all plan reminders
- [x] T089 [US2] Unit test for PlanService.delete_plan() in tests/unit/test_plan_service.py
- [x] T090 [US2] Unit test for ExerciseService delete validation in tests/unit/test_exercise_service.py

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - 暂停和恢复健身计划 (Priority: P3)

**Goal**: 用户可以暂停计划并随时恢复

**Independent Test**: 用户可以将一个活动的计划标记为"暂停"，暂停期间不会收到提醒，且可以随时恢复计划。

### Tests for User Story 4 (TDD Required) ⚠️

- [ ] T091 [P] [US4] Contract test for PATCH /api/v1/plans/{planId}/pause in tests/contract/test_plans_api_contract.py
- [ ] T092 [P] [US4] Contract test for PATCH /api/v1/plans/{planId}/resume in tests/contract/test_plans_api_contract.py
- [ ] T093 [P] [US4] Integration test for pause/resume workflow in tests/integration/test_plan_management.py

### Implementation for User Story 4

- [ ] T094 [US4] Implement PlanService.pause_plan() in src/services/plan_service.py (set status='paused', pause reminder jobs)
- [ ] T095 [US4] Implement PlanService.resume_plan() in src/services/plan_service.py (set status='active', resume reminder jobs)
- [ ] T096 [US4] Update ReminderService to check plan status before sending notifications
- [ ] T097 [US4] Create PATCH /api/v1/plans/{planId}/pause endpoint in src/api/routes/plans.py
- [ ] T098 [US4] Create PATCH /api/v1/plans/{planId}/resume endpoint in src/api/routes/plans.py
- [ ] T099 [US4] Unit test for PlanService.pause_plan() and resume_plan() in tests/unit/test_plan_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T100 [P] Add database indexes per data-model.md (user_id, status, deleted_at composite index)
- [ ] T101 [P] Implement Redis caching for GET /api/v1/plans (30 second TTL)
- [ ] T102 [P] Add request logging middleware in src/api/middleware/logging.py
- [ ] T103 [P] Add rate limiting (100 req/min per user) using slowapi
- [ ] T104 [P] Implement pagination helper utilities in src/core/pagination.py
- [ ] T105 [P] Add CORS configuration for production in src/main.py
- [ ] T106 [P] Create comprehensive API documentation in /docs endpoint (Swagger UI configuration)
- [ ] T107 [P] Add error tracking integration (Sentry or similar)
- [ ] T108 Code cleanup and refactoring (DRY principles, extract common patterns)
- [ ] T109 Performance optimization: query optimization, N+1 prevention
- [ ] T110 Security hardening: input sanitization, SQL injection prevention validation
- [ ] T111 Run coverage report (target: ≥ 70% for core modules)
- [ ] T112 Validate against quickstart.md setup instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (MVP)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent but benefits from US1 being complete
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 (needs plan status field)

### Within Each User Story

- Tests (TDD) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1 and US3 can start in parallel (both P1, no dependencies)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for POST /api/v1/plans in tests/contract/test_plans_api_contract.py"
Task: "Contract test for GET /api/v1/plans in tests/contract/test_plans_api_contract.py"
Task: "Contract test for GET /api/v1/plans/{planId} in tests/contract/test_plans_api_contract.py"
Task: "Integration test for complete plan creation flow in tests/integration/test_plan_creation.py"
Task: "Integration test for validation errors in tests/integration/test_plan_creation.py"

# Launch all models for User Story 1 together:
Task: "Create FitnessPlan model in src/models/fitness_plan.py"
Task: "Create Exercise model in src/models/exercise.py"

# Launch all schemas for User Story 1 together:
Task: "Create Pydantic schemas for plan creation request in src/api/schemas/plan_schemas.py"
Task: "Create Pydantic schemas for plan responses in src/api/schemas/plan_schemas.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create plans)
4. Complete Phase 4: User Story 3 (Reminders)
5. **STOP and VALIDATE**: Test US1 and US3 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP Part 1!)
3. Add User Story 3 → Test independently → Deploy/Demo (MVP Complete!)
4. Add User Story 2 → Test independently → Deploy/Demo (Enhancement)
5. Add User Story 4 → Test independently → Deploy/Demo (Enhancement)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Create plans)
   - Developer B: User Story 3 (Reminders)
   - Developers can work independently
3. Stories complete and integrate independently
4. Developer C can then pick up US2 or US4

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD Required: Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

**Total Tasks**: 112

**By Phase**:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 14 tasks (BLOCKING)
- Phase 3 (US1 - Create Plans): 22 tasks
- Phase 4 (US3 - Reminders): 25 tasks
- Phase 5 (US2 - Management): 21 tasks
- Phase 6 (US4 - Pause/Resume): 9 tasks
- Phase 7 (Polish): 13 tasks

**MVP Scope** (US1 + US3): 44 implementation tasks (T001-T069)

**Parallel Opportunities**: 45 tasks marked [P] can run concurrently with other [P] tasks

**Independent Test Criteria**:
- US1: Create a plan with exercises, view in list, view details
- US2: Edit plan name, add/remove exercises, delete plan
- US3: Set reminder, receive notification at scheduled time, disable reminder
- US4: Pause plan (no reminders), resume plan (reminders restart)
