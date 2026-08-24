# PLATFORM_DESIGN_SYSTEM.md

## Digital Skills and Freelancing Platform
### Product Design, UI/UX and Frontend Implementation Specification

## 1. Purpose
This document defines the complete visual, interaction, navigation, responsive, and component design system for the Digital Skills and Freelancing Platform. It guides Codex so that all pages, dashboards, forms, tables, cards, and user journeys remain consistent.

Read it together with `AGENTS.md`, `PROJECT_SPECIFICATION.md`, `DATABASE_DESIGN.md`, `UI_UX_SPECIFICATION.md`, `TESTING_PLAN.md`, `REQUIREMENTS_TRACEABILITY.md`, `DECISIONS.md`, and `CURRENT_INCREMENT.md`.

## 2. Design Vision
The platform should feel modern, professional, youth-focused, trustworthy, simple to learn, responsive, accessible, practical for low-to-medium bandwidth environments, and suitable for both academic demonstration and realistic prototype use.

It should combine the strengths of a learning management system, professional portfolio platform, freelance opportunity marketplace, and mentorship network without feeling like disconnected applications.

## 3. Core Design Principles
- **Clarity first:** users should know where they are, what they can do, and what happens next.
- **Consistency:** the same type of action, status, form, and component should look and behave the same throughout the platform.
- **Progressive disclosure:** dashboards summarize. Deeper pages handle details.
- **Mobile responsiveness:** layouts must adapt rather than simply shrink.
- **Trust and professionalism:** avoid childish styling, excessive decoration, and distracting animation.


## 4. Visual Identity

### Colour Direction
Use a restrained professional palette:
- Primary: deep blue or indigo for navigation, primary buttons, links, and active states.
- Accent: teal or emerald for learning progress, positive highlights, and mentorship accents.
- Neutral: white, gray, slate, and dark gray.
- Semantic status colours: green for success, amber for warning, red for danger, blue for information, gray for neutral.

Do not use status colours decoratively.

### Typography
Use Inter if available, otherwise a clean system sans-serif stack. Maintain a clear hierarchy for page titles, section headings, card titles, body text, and helper text.

### Shape and Depth
- Inputs: `rounded-lg`
- Cards: `rounded-xl`
- Buttons: `rounded-lg`
- Avatars: `rounded-full`
- Use subtle shadows only where they improve separation.


## 5. Layout System

### Public Layout
Desktop navigation:
`Logo | Home | Courses | Opportunities | Mentors | About | Login | Register`

Mobile navigation:
- Logo
- Menu button
- Collapsible menu

### Authenticated Layout
```text
┌─────────────────────────────────────────────────────────────────────┐
│ Header                                                              │
│ Logo / Page Context        Search        Notifications       Avatar │
├──────────────────┬──────────────────────────────────────────────────┤
│ Sidebar          │                                                  │
│ Dashboard        │  Page Heading                                    │
│ Profile          │  Breadcrumb / Description                        │
│ Courses          │                                                  │
│ Portfolio        │  Main Content                                    │
│ Opportunities    │                                                  │
│ Mentorship       │                                                  │
│ Notifications    │                                                  │
│ Settings         │                                                  │
└──────────────────┴──────────────────────────────────────────────────┘
```

On mobile, the sidebar becomes a drawer or off-canvas menu.


## 6. Role Navigation

### Freelancer/Learner
Dashboard, Profile, Skills, My Courses, Learning Progress, Portfolio, Browse Opportunities, My Applications, Mentors, Mentorship Requests, Notifications, Settings.

### Mentor
Dashboard, Mentor Profile, Mentorship Requests, My Mentees, Notifications, Settings.

### Client
Dashboard, Client Profile, Post Opportunity, My Opportunities, Applications, Notifications, Settings.

### Administrator
Dashboard, Users, Skills, Categories, Courses, Lessons, Opportunities, Applications, Mentors, Mentorships, Notifications, Statistics, Settings.

Only display navigation relevant to the authenticated role.


## 7. Public Website

### Home
Recommended sections:
1. Hero with headline, supporting text, Get Started CTA, and Explore Courses CTA.
2. Four value cards: Learn Digital Skills, Build Your Portfolio, Find Freelance Work, Get Mentorship.
3. Featured Courses.
4. Latest Opportunities.
5. Mentorship section.
6. Final registration CTA.

Suggested hero message:
**Build Skills. Build Your Portfolio. Find Opportunities.**

### Course Catalogue
Each course card should show image, title, category, difficulty, short description, and View Course action.

### Opportunity Catalogue
Use a clean list/card hybrid displaying job title, client, category, budget, deadline, required skills, and View Details action.

### Mentor Directory
Each mentor card should show photo, name, professional title, expertise, availability summary, and View Profile action.


## 8. Freelancer/Learner Dashboard

The dashboard should immediately summarize learning, portfolio, applications, mentorship, and notifications.

```text
Welcome back, [Name]

┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Courses        │ │ Applications   │ │ Portfolio      │ │ Mentorship     │
│ 3 Enrolled     │ │ 4 Submitted    │ │ 6 Projects     │ │ 1 Active       │
└────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘

┌─────────────────────────────────────┐ ┌──────────────────────────────┐
│ Continue Learning                   │ │ Recent Notifications         │
│ Web Development Fundamentals        │ │ • Application updated       │
│ ███████████████░░░ 75%              │ │ • Mentor accepted request   │
│ [Continue Course]                   │ │                              │
└─────────────────────────────────────┘ └──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ Recent Opportunities                                                │
└─────────────────────────────────────────────────────────────────────┘
```

Do not label anything "recommended" unless recommendation logic actually exists.


## 9. Profile and Skills

### Profile
Desktop: two-column layout. Left side can contain image, name, role, location, and skills. Right side contains biography and profile details. Mobile layout stacks vertically.

### Skills
Use chips or compact cards. Suggested proficiency values:
- Beginner
- Intermediate
- Advanced

Users should clearly see existing skills and how to add or remove them.


## 10. Digital Learning Experience

### My Courses
Each card shows title, category, progress, completion status, and Continue Learning action.

### Course Learning Screen
```text
┌─────────────────────┬──────────────────────────────────────────────┐
│ Course Lessons      │ Lesson Title                                 │
│ ✓ Introduction      │                                              │
│ ✓ HTML Basics       │ Lesson content                               │
│ ○ CSS Basics        │ Video / text / resource links                │
│ ○ Final Exercise    │                                              │
│ Progress 50%        │ [Previous]                  [Mark Complete]   │
└─────────────────────┴──────────────────────────────────────────────┘
```

On mobile, lesson navigation should collapse into a drawer or selector.

Progress should use text plus a progress bar. Do not rely on colour alone.


## 11. Portfolio Design

The portfolio should feel like a professional showcase, not a plain database table.

Portfolio header:
- Name
- Professional headline
- About
- Skills

Project grid:
- Project image
- Project title
- Skills used
- Short description
- Project link

Owner sees Add, Edit, Delete actions. Clients or visitors do not see owner controls.


## 12. Freelance Marketplace

### Opportunity Details
Main section:
- Job title
- Client/organisation
- Description
- Required skills
- Budget
- Deadline
- Category

Side card:
- Status
- Posted date
- Apply action
- Existing application status if already applied

### Apply Form
Fields:
- Cover message
- Proposed amount

### My Applications
Desktop table or responsive cards:
- Opportunity
- Client
- Submitted date
- Proposed amount
- Status
- View action


## 13. Application Status Vocabulary
Use these exact display states consistently:
- Pending
- Under Review
- Accepted
- Rejected

Opportunity states:
- Active
- Closed
- Expired

Learning states:
- In Progress
- Completed

Mentorship request states:
- Pending
- Accepted
- Rejected


## 14. Mentor Experience

### Mentor Dashboard
Summary cards:
- Pending Requests
- Active Mentees
- Notifications

### Mentorship Request Card
Show learner photo/name, interest area, message, and Accept/Reject actions.

### My Mentees
Show name, relevant skills, start date, and mentorship status.

Real-time chat is not part of the prototype unless explicitly approved later.


## 15. Client Experience

### Client Dashboard
Summary cards:
- Active Opportunities
- Total Applications
- Pending Reviews
- Closed Opportunities

### Post Opportunity
Fields:
- Title
- Description
- Category
- Required skills where implemented
- Budget
- Deadline

### Applicant Review
Display applicant profile summary, skills, portfolio link, cover message, proposed amount, and application status controls.


## 16. Administrator Experience

### Admin Dashboard
Suggested statistics:
- Total Users
- Freelancers
- Mentors
- Clients
- Courses
- Active Opportunities
- Applications
- Active Mentorships

Also show recent users, recent opportunities, recent applications, and mentorship activity.

### Management Tables
Provide search, filters where useful, status badges, pagination when needed, and concise action menus. Avoid overcrowding rows with many buttons.


## 17. Component Library

### Buttons
- Primary: Save, Submit, Enrol, Apply, Continue
- Secondary: Cancel, View, Back
- Danger: Delete, Deactivate, destructive rejection actions
- Disabled: visibly non-interactive

### Forms
Each field should include label, input, optional help text, and validation error.

### Reusable Components
- Cards
- Badges
- Alerts
- Progress bars
- Tables
- Pagination
- Empty states
- Modals
- Search fields
- Dropdowns

Use modals sparingly, mainly for confirmation. Do not place long forms in modals.


## 18. Form and Interaction Rules
- Required fields should be obvious.
- Validation messages appear near the relevant field.
- Preserve safe user-entered values after validation failure.
- Use Post/Redirect/Get after successful state-changing forms.
- Protect forms with CSRF.
- Never use GET for destructive actions.
- Require confirmation for delete, deactivate, and close actions.
- Keep forms usable on mobile.


## 19. Search and Filtering
Courses may filter by category and difficulty.

Opportunities may filter by category, date, status where appropriate, and skill if implemented.

Mentors may filter by expertise and availability where practical.

No-results states should explain that no matches were found and offer a way to clear filters.


## 20. Notifications
Header:
- Bell icon
- Unread-count badge

Notification centre:
- Newest first
- Read/unread distinction
- Timestamp
- Mark as read

Events include:
- Course enrolment
- New application received
- Application status change
- Mentorship request
- Mentorship response


## 21. Responsive Behaviour

### Desktop
- Persistent sidebar
- Multi-column dashboards
- Full data tables

### Tablet
- Narrow/collapsible sidebar
- Two-column cards
- Horizontal table scroll when necessary

### Mobile
- Off-canvas navigation
- Single-column content
- Stacked action buttons
- Tables converted to cards where practical
- Comfortable touch targets


## 22. Accessibility
- Use semantic HTML.
- Associate labels with inputs.
- Maintain visible keyboard focus.
- Do not communicate status using colour alone.
- Provide meaningful alt text.
- Maintain readable contrast.
- Use logical heading hierarchy.
- Make validation messages clear.


## 23. Low-Bandwidth Considerations
- Compress images.
- Avoid large decorative media.
- Do not autoplay video.
- Prefer server-rendered pages.
- Avoid heavy JavaScript frameworks.
- Paginate large lists.
- Avoid loading large datasets on one page.
- Keep animation minimal.


## 24. Tailwind Implementation Guidelines
Create reusable patterns instead of inconsistent class strings.

Recommended reusable categories:
- `.btn-primary`
- `.btn-secondary`
- `.btn-danger`
- `.form-input`
- `.form-label`
- `.form-error`
- `.card`
- `.badge`
- `.stat-card`

Do not introduce a second unrelated design framework.


## 25. Suggested Template Hierarchy
```text
templates/
├── base.html
├── components/
│   ├── alerts.html
│   ├── badges.html
│   ├── pagination.html
│   └── empty_state.html
├── layouts/
│   ├── dashboard.html
│   └── public.html
├── main/
├── auth/
├── users/
├── courses/
├── portfolio/
├── opportunities/
├── mentorship/
├── notifications/
├── admin/
└── errors/
```

Preserve an already-clean equivalent rather than restructuring working code unnecessarily.


## 26. Design QA Checklist
Before marking a page complete:
- [ ] Correct role layout is used.
- [ ] Navigation is correct.
- [ ] Heading hierarchy is clear.
- [ ] Primary action is obvious.
- [ ] Forms have labels and validation feedback.
- [ ] Empty state exists where needed.
- [ ] Success/error feedback exists.
- [ ] Unauthorized controls are hidden.
- [ ] Server-side authorization still exists.
- [ ] Mobile layout works.
- [ ] Status wording is consistent.
- [ ] No fake functionality is presented as active.


## 27. Codex Design Rules
Codex must:
1. Read this file before building major UI.
2. Reuse established components.
3. Avoid redesigning completed pages without approval.
4. Avoid unapproved UI libraries.
5. Keep Tailwind usage consistent.
6. Provide mobile behavior for every new page.
7. Avoid fake metrics or recommendations unless clearly marked as demo data.
8. Never display unimplemented functionality as working.
9. Preserve accessibility and validation patterns.
10. Keep visual changes aligned with the approved role journeys.


## 28. Priority Screens for Visual Review
1. Home Page
2. Registration/Login
3. Freelancer Dashboard
4. Course Catalogue
5. Course Learning Screen
6. Portfolio
7. Opportunity Catalogue
8. Opportunity Details
9. Application Form
10. Mentor Directory
11. Mentor Dashboard
12. Client Dashboard
13. Applicant Review
14. Administrator Dashboard
15. User Management
16. Mobile Navigation


## 29. Design Development Sequence

### Increment 1
Base public layout, navigation shell, home page, error pages, Tailwind foundation.

### Increment 2
Authentication forms, authenticated layout, role dashboard shells.

### Increment 3
Profile and skills interfaces.

### Increment 4
Course catalogue, My Courses, learning screen, progress components.

### Increment 5
Portfolio interfaces.

### Increment 6
Opportunity marketplace.

### Increment 7
Application interfaces.

### Increment 8
Mentor directory and mentorship pages.

### Increment 9
Notifications, admin dashboard, management tables.

### Increment 10
Responsive refinement, accessibility review, UI consistency review, final screenshot capture.


## 30. Final User Journeys

### Freelancer/Learner
`Register → Complete Profile → Add Skills → Enrol in Course → Build Portfolio → Browse Opportunities → Apply → Track Application → Find Mentor → Request Mentorship`

### Client
`Register → Complete Profile → Post Opportunity → Receive Applications → Review Applicant → View Portfolio → Update Application Status`

### Mentor
`Login → Complete Mentor Profile → Receive Request → Review Learner → Accept/Reject → View Mentees`

### Administrator
`Login → View Platform Overview → Manage Users → Manage Learning Content → Monitor Opportunities → Monitor Mentorship Activity`

All journeys must share one visual language, one navigation philosophy, and one reusable component system.
