# Team Production Report (Django)

## Overview
This project is a Django-only application (no DRF) with HTML + Bootstrap. It supports three roles with distinct capabilities:

- User: add/edit projects, add attendance for projects/resources, view resources, read-only elsewhere, can view tree structure.
- Admin: full CRUD on projects, resources, attendance, tech stack, interns; can view tree structure.
- Superadmin: read-only across projects, resources, attendance, tech stack, interns; can view tree structure.

## Entry Flow
- The first page ("role selection") is served at `/` and shows two options: User and Admin.
- Selecting User sets the session role to `user` and redirects to `/dashboard/`.
- Selecting Admin goes to `/login/` where you can sign in as `admin` or `superadmin`.
- After login, all roles land on `/dashboard/`.

## Key URLs
- `/` → Role selection (no navbar)
- `/login/` → Login page (no navbar)
- `/logout/` → Logout
- `/dashboard/` → Dashboard
- `/tree/` → Project/Resource Tree Structure
- `/projects/` → Project list and CRUD
- `/resources/` → Resource list and CRUD (UI hides actions based on role)
- `/interns/` → Tech stack and interns (admin changes; superadmin read-only)

## Role Permissions (Server + UI)
- User
  - Projects: create, edit; cannot delete
  - Resources: view-only
  - Attendance: can add/edit for project and resource
  - Tree: can view (project and resource)
- Admin
  - Full CRUD for Projects, Resources, Attendance, Tech Stack, Interns
  - Tree: can view
- Superadmin
  - Read-only for Projects, Resources, Attendance, Tech Stack, Interns
  - Tree: can view

## Implementation Notes
- Navbar is hidden on the role selection and login pages by using standalone templates (not extending the base).
- Navbar content is role-aware using `request.session.role`.
- Permissions are enforced in views (`projects/views.py`, `resources/views.py`, `interns/views.py`).
- Tree Structure view is in `projects.views.tree_structure_view` and routed at `/tree/`.

## Initial Admin Users
**Automatic Setup (Recommended):**
The admin and superadmin users are automatically created when you start the application.

Default credentials:
- Username: `admin` | Password: `Admin@123`
- Username: `superadmin` | Password: `Admin@123`

**Custom Password (Docker):**
If you want to use a custom password, you can run:
```bash
docker-compose exec django python manage.py setup_users --password YourCustomPassword
```

**Manual Setup (Alternative):**
You can create them via Django shell inside the container:
```bash
docker-compose exec django python manage.py shell
```

```python
from django.contrib.auth.models import User
pwd = 'Admin@123'
for uname in ['admin','superadmin']:
    if not User.objects.filter(username=uname).exists():
        User.objects.create_user(username=uname, password=pwd, is_staff=True, is_superuser=(uname=='superadmin'))
print('Done')
```

## How to Run

### Using Docker (Recommended)
1. **Start the application:**
   ```bash
   docker-compose up
   ```
   
   This will automatically:
   - Run database migrations
   - Create admin and superadmin users
   - Start the Django server

2. **Access the application:**
   - Open `http://localhost:8000/` → role selection

### Manual Setup (Alternative)
- Install dependencies: `pip install -r requirements.txt`
- Apply migrations: `python manage.py migrate`
- **Create the users automatically:** `python manage.py setup_users`
- Run server: `python manage.py runserver`
- Open `http://localhost:8000/` → role selection

## Docker Commands
```bash
# Start the application
docker-compose up

# Start in background
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs django

# Run management commands
docker-compose exec django python manage.py setup_users
docker-compose exec django python manage.py shell
docker-compose exec django python manage.py createsuperuser
```

## What Was Changed
- Added landing, login/logout views and templates without navbar
- Root URL now points to landing, plus `dashboard/` and `tree/` routes
- Role-based permissions enforced and UI buttons hidden per role
- Projects and Resources templates adjusted for role visibility
- Tree structure wired to global route and visible from navbar
- Added management command `setup_users` for automatic user creation
- Updated Docker setup to automatically create users on startup
