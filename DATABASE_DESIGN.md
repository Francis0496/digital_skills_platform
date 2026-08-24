# DATABASE_DESIGN.md

## Purpose
This file defines the relational data model for the prototype. Codex should treat names and constraints here as the default design unless an approved change is recorded in `DECISIONS.md`.

## General Rules
- Use SQLAlchemy models.
- Use integer primary keys unless there is a strong approved reason otherwise.
- Use explicit foreign keys.
- Add `created_at` timestamps where useful.
- Use unique constraints for business-rule uniqueness.
- Preserve ownership and referential integrity.
- Add migrations for schema changes.
- Prefer controlled deletion where records form part of history.

## Entities

### Role
Fields:
- `id` INTEGER PK
- `name` VARCHAR UNIQUE NOT NULL

Expected values:
- freelancer
- mentor
- client
- administrator

Relationship:
- Role 1:M User

### User
Fields:
- `id` INTEGER PK
- `full_name` VARCHAR NOT NULL
- `email` VARCHAR UNIQUE NOT NULL
- `password_hash` VARCHAR NOT NULL
- `role_id` INTEGER FK -> role.id NOT NULL
- `phone` VARCHAR NULL
- `location` VARCHAR NULL
- `bio` TEXT NULL
- `profile_image` VARCHAR NULL
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `created_at` DATETIME NOT NULL

Relationships:
- M:1 Role
- M:M Skill via UserSkill
- 1:1 Portfolio for freelancers
- 1:1 MentorProfile for mentors
- 1:M owned FreelanceOpportunity for clients
- 1:M JobApplication for freelancers
- 1:M Notifications

### Skill
Fields:
- `id` INTEGER PK
- `name` VARCHAR UNIQUE NOT NULL
- `description` TEXT NULL

### UserSkill
Fields:
- `id` INTEGER PK
- `user_id` INTEGER FK -> user.id NOT NULL
- `skill_id` INTEGER FK -> skill.id NOT NULL
- `proficiency_level` VARCHAR NULL

Constraint:
- UNIQUE(user_id, skill_id)

### CourseCategory
Fields:
- `id` INTEGER PK
- `name` VARCHAR UNIQUE NOT NULL
- `description` TEXT NULL

### Course
Fields:
- `id` INTEGER PK
- `category_id` INTEGER FK -> course_category.id NOT NULL
- `title` VARCHAR NOT NULL
- `description` TEXT NOT NULL
- `difficulty_level` VARCHAR NULL
- `image` VARCHAR NULL
- `is_published` BOOLEAN NOT NULL DEFAULT FALSE
- `created_at` DATETIME NOT NULL

Relationships:
- M:1 CourseCategory
- 1:M Lesson
- M:M User through Enrollment

### Lesson
Fields:
- `id` INTEGER PK
- `course_id` INTEGER FK -> course.id NOT NULL
- `title` VARCHAR NOT NULL
- `content` TEXT NOT NULL
- `video_url` VARCHAR NULL
- `lesson_order` INTEGER NOT NULL
- `created_at` DATETIME NOT NULL

Recommended constraint:
- UNIQUE(course_id, lesson_order)

### Enrollment
Fields:
- `id` INTEGER PK
- `user_id` INTEGER FK -> user.id NOT NULL
- `course_id` INTEGER FK -> course.id NOT NULL
- `enrolled_at` DATETIME NOT NULL
- `completion_status` VARCHAR NOT NULL DEFAULT 'in_progress'

Constraint:
- UNIQUE(user_id, course_id)

Progress percentage should preferably be calculated from LessonProgress rather than stored redundantly unless there is a justified reason.

### LessonProgress
Fields:
- `id` INTEGER PK
- `enrollment_id` INTEGER FK -> enrollment.id NOT NULL
- `lesson_id` INTEGER FK -> lesson.id NOT NULL
- `completed` BOOLEAN NOT NULL DEFAULT FALSE
- `completed_at` DATETIME NULL

Constraint:
- UNIQUE(enrollment_id, lesson_id)

### Portfolio
Fields:
- `id` INTEGER PK
- `user_id` INTEGER FK -> user.id UNIQUE NOT NULL
- `title` VARCHAR NULL
- `description` TEXT NULL

Relationship:
- 1:1 User
- 1:M PortfolioProject

### PortfolioProject
Fields:
- `id` INTEGER PK
- `portfolio_id` INTEGER FK -> portfolio.id NOT NULL
- `title` VARCHAR NOT NULL
- `description` TEXT NOT NULL
- `project_image` VARCHAR NULL
- `project_url` VARCHAR NULL
- `completion_date` DATE NULL

### FreelanceOpportunity
Fields:
- `id` INTEGER PK
- `client_id` INTEGER FK -> user.id NOT NULL
- `title` VARCHAR NOT NULL
- `description` TEXT NOT NULL
- `category` VARCHAR NULL
- `budget` DECIMAL/NUMERIC NULL
- `deadline` DATE NULL
- `status` VARCHAR NOT NULL DEFAULT 'active'
- `created_at` DATETIME NOT NULL

Recommended status values:
- active
- closed
- expired

### JobApplication
Fields:
- `id` INTEGER PK
- `opportunity_id` INTEGER FK -> freelance_opportunity.id NOT NULL
- `freelancer_id` INTEGER FK -> user.id NOT NULL
- `cover_message` TEXT NOT NULL
- `proposed_amount` DECIMAL/NUMERIC NULL
- `status` VARCHAR NOT NULL DEFAULT 'pending'
- `submitted_at` DATETIME NOT NULL

Constraint:
- UNIQUE(opportunity_id, freelancer_id)

Allowed statuses:
- pending
- under_review
- accepted
- rejected

### MentorProfile
Fields:
- `id` INTEGER PK
- `user_id` INTEGER FK -> user.id UNIQUE NOT NULL
- `professional_title` VARCHAR NULL
- `expertise` TEXT NULL
- `experience` TEXT NULL
- `availability` VARCHAR/TEXT NULL

### MentorshipRequest
Fields:
- `id` INTEGER PK
- `freelancer_id` INTEGER FK -> user.id NOT NULL
- `mentor_id` INTEGER FK -> user.id NOT NULL
- `message` TEXT NULL
- `status` VARCHAR NOT NULL DEFAULT 'pending'
- `requested_at` DATETIME NOT NULL

Allowed statuses:
- pending
- accepted
- rejected

Recommended rule:
Prevent duplicate pending requests between the same freelancer and mentor.

### Mentorship
Fields:
- `id` INTEGER PK
- `freelancer_id` INTEGER FK -> user.id NOT NULL
- `mentor_id` INTEGER FK -> user.id NOT NULL
- `start_date` DATE/DATETIME NOT NULL
- `status` VARCHAR NOT NULL DEFAULT 'active'

Recommended constraint:
- Prevent duplicate active mentorship records for the same pair.

### Notification
Fields:
- `id` INTEGER PK
- `user_id` INTEGER FK -> user.id NOT NULL
- `message` TEXT NOT NULL
- `notification_type` VARCHAR NULL
- `is_read` BOOLEAN NOT NULL DEFAULT FALSE
- `created_at` DATETIME NOT NULL

## Core Relationship Summary
- Role 1:M User
- User M:M Skill through UserSkill
- CourseCategory 1:M Course
- Course 1:M Lesson
- User M:M Course through Enrollment
- Enrollment 1:M LessonProgress
- User 1:1 Portfolio
- Portfolio 1:M PortfolioProject
- Client/User 1:M FreelanceOpportunity
- FreelanceOpportunity 1:M JobApplication
- Freelancer/User 1:M JobApplication
- Mentor/User 1:1 MentorProfile
- Freelancer/User 1:M MentorshipRequest
- Mentor/User 1:M MentorshipRequest
- User 1:M Notification

## Deletion Guidance
- Prefer deactivation of User rather than deletion.
- Deleting a Course with historical enrolments should be avoided. Prefer unpublishing.
- Closing an Opportunity is preferred to deleting one that already has applications.
- Historical JobApplication and Mentorship data should not be silently destroyed.
- PortfolioProject can be safely deleted by the owner if no external dependency exists.
