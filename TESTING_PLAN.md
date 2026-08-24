# TESTING_PLAN.md

## Purpose
Define the testing approach for the prototype and provide evidence for Chapter Five and the dissertation appendices.

## Testing Principles
- Test every critical business rule.
- Test authentication and authorization rigorously.
- Test both successful and unsuccessful workflows.
- Run regression tests after each increment.
- Maintain a clear link between requirements and tests.
- Do not treat manual clicking alone as sufficient verification.

## Automated Test Categories

### 1. Application Startup Tests
Verify:
- Application factory creates the app.
- Test configuration loads correctly.
- Test database initializes.

### 2. Model Tests
Verify:
- Required fields.
- Unique constraints.
- Relationships.
- Status defaults.
- Ownership assumptions.

### 3. Authentication Tests
Test:
- Valid registration.
- Duplicate email rejection.
- Password hashing.
- Valid login.
- Invalid login.
- Logout.
- Inactive account behavior.
- Administrator cannot self-register publicly.

### 4. Authorization Tests
For each protected feature, test:
- Anonymous user denied.
- Wrong role denied.
- Correct role allowed.
- Non-owner denied from modifying another user's record.

### 5. Course Tests
Test:
- Admin course/category/lesson management.
- Unpublished course visibility.
- Enrolment.
- Duplicate enrolment prevention.
- Lesson access.
- Lesson completion.
- Progress calculation.

### 6. Portfolio Tests
Test:
- Portfolio creation.
- Project CRUD.
- Ownership.
- Public/authorized viewing.

### 7. Opportunity Tests
Test:
- Client creation.
- Ownership on edit/close.
- Active catalogue.
- Closed opportunity behavior.
- Search/filter.

### 8. Application Tests
Test:
- Valid application.
- Duplicate prevention.
- Closed opportunity rejection.
- Client review of own applicants.
- Status updates.
- Freelancer application tracking.
- Notifications.

### 9. Mentorship Tests
Test:
- Mentor directory.
- Request creation.
- Wrong recipient access denial.
- Accept/reject.
- Duplicate active mentorship prevention.
- Notifications.

### 10. Notification Tests
Test:
- Correct recipient.
- Read/unread behavior.
- User cannot read another user's private notifications through direct modification routes.

### 11. Admin Tests
Test:
- Admin dashboard access.
- Non-admin denial.
- User activation/deactivation.
- Content management permissions.
- Statistics return expected counts.

## Manual System Testing
Before final deployment, run full scenarios:

### Scenario A: Learner Journey
1. Register.
2. Log in.
3. Complete profile.
4. Add skills.
5. Browse and enrol in a course.
6. Complete lessons.
7. Build portfolio.
8. Browse opportunity.
9. Apply.
10. Browse mentor and request mentorship.
11. Review notifications.

### Scenario B: Client Journey
1. Register/login as client.
2. Complete profile.
3. Post opportunity.
4. View applicants.
5. Review portfolio.
6. Update application status.

### Scenario C: Mentor Journey
1. Log in as mentor.
2. Complete mentor profile.
3. Review pending request.
4. Accept or reject.
5. View active mentees.

### Scenario D: Administrator Journey
1. Log in as admin.
2. View statistics.
3. Manage users.
4. Manage course content.
5. Review opportunities.
6. Review mentorship records.

## Usability Testing
Assess:
- Navigation clarity.
- Form clarity.
- Dashboard readability.
- Responsiveness.
- Task completion.
- Error-message usefulness.

## Test Evidence Format
Each manual/system test should record:
- Test ID.
- Requirement ID.
- Preconditions.
- Steps.
- Expected result.
- Actual result.
- Pass/Fail.
- Evidence/screenshot reference.
- Notes.

## Suggested Test ID Prefixes
- AUTH
- ROLE
- PROFILE
- COURSE
- PORTFOLIO
- JOB
- APP
- MENTOR
- NOTIFY
- ADMIN
- SYS
- UX

## Final Exit Criteria
- All critical automated tests pass.
- No known authorization bypass exists.
- Core user journeys complete successfully.
- Regression suite passes.
- Manual system-test checklist is completed.
- Known limitations are documented.
