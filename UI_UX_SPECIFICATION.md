# UI_UX_SPECIFICATION.md

## Design Goal
Create a clean, modern, responsive, easy-to-understand prototype using Tailwind CSS. The interface should be practical for first-time users and consistent across roles.

## Global UI Rules
- Use a consistent header/navigation pattern.
- Use a shared base layout.
- Use clear page titles.
- Use responsive containers and spacing.
- Use clear primary and secondary actions.
- Display field-level form errors.
- Use flash messages for success and error feedback.
- Use empty states that explain the next action.
- Require confirmation for destructive actions.
- Hide controls the user cannot use, while still enforcing permissions server-side.
- Use sensible default images/placeholders.
- Avoid excessive visual complexity.

## Public Pages

### Home
Purpose:
- Introduce the platform.
- Highlight skills training, freelancing, portfolios, and mentorship.
- Provide calls to action for registration, courses, opportunities, and mentors.

### About
Purpose:
- Explain the platform's mission and prototype purpose.

### Course Catalogue
Display:
- Course cards.
- Category.
- Difficulty.
- Short description.
- Published courses only.

Actions:
- View details.
- Enrol if authenticated freelancer/learner.

### Course Details
Display:
- Title.
- Description.
- Category.
- Difficulty.
- Lesson overview.
- Enrolment state.

### Opportunity Catalogue
Display:
- Active opportunities.
- Job title.
- Category.
- Budget if available.
- Deadline.
- Client/organisation where appropriate.

Functions:
- Search.
- Filter by category/skill/date where implemented.

### Opportunity Details
Display:
- Full description.
- Requirements.
- Budget.
- Deadline.
- Status.

Actions:
- Apply if authorized and eligible.
- View own application state if already applied.

### Mentor Directory
Display:
- Mentor name.
- Professional title.
- Expertise.
- Availability summary.

### Mentor Profile
Display:
- Full mentor details.
- Expertise.
- Experience.
- Availability.

Action:
- Request mentorship if eligible.

### Login
Fields:
- Email.
- Password.

### Registration
Fields:
- Full name.
- Email.
- Password.
- Password confirmation.
- Publicly allowed role.

Rules:
- Administrator role must not be available.
- Validation errors must be clear.

## Freelancer/Learner Dashboard
Widgets:
- Enrolled courses.
- Learning progress.
- Application count/status summary.
- Mentorship status.
- Recent notifications.
- Quick links.

### Profile
- View/edit biography, contact/location, image, and relevant details.

### Skills
- Add/remove approved skills.
- Optional proficiency level.

### My Courses
- List enrolled courses and progress.

### Learning View
- Lesson navigation.
- Content.
- Mark complete.
- Progress indicator.

### Portfolio
- Portfolio title and description.
- Project cards.
- Add/edit/delete project actions.

### My Applications
- Opportunity title.
- Submission date.
- Proposed amount.
- Status.

### Mentorship Requests
- Mentor.
- Request status.
- Active mentorship summary.

### Notifications
- List own notifications.
- Read/unread state.
- Mark as read.

## Mentor Dashboard
Widgets:
- Pending requests.
- Active mentees.
- Recent notifications.

Pages:
- Mentor profile.
- Pending requests.
- Active mentees.
- Notifications.

## Client Dashboard
Widgets:
- Active opportunities.
- Total applications.
- Recent applications.
- Notifications.

Pages:
- Client profile.
- Post opportunity.
- My opportunities.
- Opportunity applications.
- Applicant profile and portfolio.
- Notifications.

## Administrator Dashboard
Widgets:
- Total users.
- Freelancers.
- Mentors.
- Clients.
- Courses.
- Opportunities.
- Applications.
- Active mentorships.

Management Pages:
- Users.
- Skills.
- Categories.
- Courses.
- Lessons.
- Opportunities.
- Applications oversight.
- Mentors.
- Mentorship records.

## Responsive Requirements
- Navigation collapses appropriately on small screens.
- Forms remain readable and usable on mobile.
- Tables should become scrollable or transform into stacked cards where needed.
- Dashboard cards wrap cleanly.
- Important actions remain accessible without horizontal page overflow.

## Error/Empty States
Examples:
- No enrolled courses: show a link to browse courses.
- No applications: show a link to opportunities.
- No portfolio projects: show an add-project action.
- No mentorship requests: explain that there are no pending requests.
- No notifications: display a neutral empty state.
