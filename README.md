# Django CRM

Multi-tenant CRM system built with Django using role-based access control (RBAC).

## Features

- Multi-company architecture
- Team-based structure
- Role-based permissions
- Soft deactivation
- Team isolation between companies

---

# Roles

## Manager
- Create, view and update own leads
- Create, view and update deals related to own leads
- Create and view comments for own leads and deals

## Operator
- Create and view leads for own team
- Update only `NEW` leads created by him
- Assign leads to managers inside the team

## Team Admin
- View and update leads inside the team
- Manage users inside the team
- Can manage only:
  - managers
  - operators

## Company Admin
- Manage teams inside the company
- Manage only `team_admin` users

## System Admin
- Manage companies
- Manage only `company_admin` users

---

# Tech Stack

- Python
- Django
- PostgreSQL
- HTML/CSS/JS

---

# Business Logic

## Lead Lifecycle

```text
NEW → CONTACTED → QUALIFIED → REJECTED
```

- Only qualified leads can participate in deals

---

## Deal Lifecycle

```text
NEW → IN_PROGRESS → WON / LOST
```

- Deals cannot be created directly in a final status
- Managers can work only with deals related to their own leads

---

# Installation

## Clone repository

```bash
git clone https://github.com/MilkyHouse11/django_crm.git
cd django_crm
```

## Create virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configure environment variables

Create `.env` file using `.env.example`.

Example:

```env
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_HOST=
DB_PORT=
SECRET_KEY=
```

---

## Apply migrations

```bash
python manage.py migrate
```

---

## Create superuser

```bash
python manage.py createsuperuser
```

---

## Run development server

```bash
python manage.py runserver
```

---
## Basic credentials

- system_admin@email.com, 123
- company_adminc1@email.com, 123
- team_adminc1t1@email.com, 123
- managerc1t1@email.com, 123
- operatorc1t1@email.com, 123

---
## Screenshots

### Leads List

![Leads List](screenshots/leads_list.png)

### Editing Form

![Deal Editing](screenshots/deal_editing.png)

### Creation Form

![Lead Creation](screenshots/lead_creation.png)

---

# Notes

- Django admin is used only for technical and emergency operations
- Business logic is implemented through application roles and permissions
- Users, teams, leads and companies are deactivated instead of physically deleted
- The project is focused on backend architecture and access control