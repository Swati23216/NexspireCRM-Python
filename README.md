# NexspireCRM 🚀

**NexspireCRM** is a full-stack Customer Relationship Management (CRM) application designed to help organizations manage customers, leads, opportunities, follow-ups, tickets, users, activities, and business operations from a centralized workspace.

The application is built with **Python, FastAPI, MongoDB, HTML, CSS, and Vanilla JavaScript**, with a RESTful backend, authentication, role-based access control, and a responsive web interface.

---

## 🌟 Project Overview

NexspireCRM provides a centralized platform for managing the complete customer lifecycle — from lead management and customer interactions to follow-ups, opportunities, tickets, notifications, and reporting.

The project demonstrates practical implementation of:

* REST API development using **FastAPI**
* **MongoDB** database integration
* JWT-based authentication
* Role-Based Access Control (RBAC)
* Permission-based API authorization
* CRUD operations
* Admin and user management
* Frontend-backend integration
* Secure configuration using environment variables
* API validation using Pydantic
* Modular backend architecture

---

## ✨ Key Features

### 🔐 Authentication & Security

* User registration and login
* JWT-based authentication
* Access and refresh token support
* Password security and authentication dependencies
* Protected API endpoints
* Role-based authorization
* Environment-based configuration for sensitive credentials

### 👥 Customer Management

* Create and manage customer records
* View customer information
* Update customer details
* Delete customer records
* Customer-related activity tracking

### 🎯 Lead Management

* Create and manage leads
* Track lead information and status
* Update lead details
* Convert qualified leads into customers
* Permission-controlled lead operations

### 💼 Opportunity Management

* Manage business opportunities
* Track opportunity information
* Organize opportunities within the CRM workflow

### 📅 Follow-Up Management

* Schedule customer and lead follow-ups
* Maintain separate subject, scheduled date, and notes
* Update and manage follow-up records
* Permission-controlled follow-up operations

### 🎫 Ticket Management

* Create and manage support tickets
* Track ticket-related information
* Centralize customer support activities

### 📊 Dashboard & Reports

* CRM dashboard
* Business activity overview
* Reports and analytics endpoints
* Centralized workspace for CRM operations

### 👤 User & Role Management

* Admin user management
* Create and manage team members
* Create custom roles
* Configure role permissions
* Built-in CRM roles
* Permission-based access to workspace modules

### 🔎 Search & Notifications

* Search functionality across CRM data
* Notification management
* Activity tracking

### 🌐 Public Company Website

* Public Nexspire Technologies website
* Company information pages
* Login and registration access
* Seamless transition between public website and CRM workspace

---

## 🛡️ Role-Based Access Control

NexspireCRM implements **Role-Based Access Control (RBAC)** at the API level.

Permissions are enforced by the backend and also used by the frontend to control which modules and actions are available to users.

Supported permission categories include:

```text
dashboard.view

leads.view
leads.create
leads.update
leads.delete
leads.convert

customers.view
customers.create
customers.update
customers.delete

followups.view
followups.create
followups.update
followups.delete
```

The built-in **Admin** role retains full access to the workspace.

The first registered account becomes the workspace Admin, while subsequent public registrations receive the Viewer role by default.

---

## 🏗️ Technology Stack

### Backend

* **Python**
* **FastAPI**
* **Pydantic**
* **JWT Authentication**
* **Uvicorn**

### Database

* **MongoDB**

### Frontend

* **HTML5**
* **CSS3**
* **Vanilla JavaScript**

### Development Tools

* **Git**
* **GitHub**
* **VS Code**
* **Python Virtual Environment**

---

## 📁 Project Structure

```text
NexspireCRM-Python/
│
├── app/
│   ├── core/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── permissions.py
│   │   └── security.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   │
│   └── main.py
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── company.html
│   ├── home.html
│   ├── index.html
│   └── login.html
│
├── .github/
├── .gitignore
├── requirements.txt
├── test_auth.py
├── check_db.py
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Swati23216/NexspireCRM-Python.git
cd NexspireCRM-Python
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=your_database_name
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **Important:** Never commit your `.env` file or database credentials to GitHub.

### 5. Start the application

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

## 🌐 Application Flow

```text
Public Website
      │
      ▼
Login / Registration
      │
      ▼
Authentication
      │
      ▼
CRM Dashboard
      │
      ├── Dashboard
      ├── Leads
      ├── Customers
      ├── Opportunities
      ├── Follow-Ups
      ├── Tickets
      ├── Notifications
      ├── Reports
      └── Admin Center
```

The public website is available at:

```text
/
```

The login and registration page is available at:

```text
/login.html
```

After successful authentication, users are directed to:

```text
/index.html
```

The company website is also available at:

```text
/company.html
```

---

## 🧪 Testing & Validation

Authentication and API functionality can be validated using:

```powershell
.\.venv\Scripts\python.exe test_auth.py
```

Database connectivity can be checked using:

```powershell
.\.venv\Scripts\python.exe check_db.py
```

---

## 🔌 API Documentation

When the FastAPI server is running, interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Alternative API documentation:

```text
http://127.0.0.1:8000/redoc
```

These interfaces can be used to explore and test the available REST API endpoints.

---

## 🔒 Security Considerations

The project uses environment variables for sensitive configuration such as:

* MongoDB connection strings
* Secret keys
* Authentication configuration

Sensitive files such as `.env`, virtual environments, cache files, and local databases are excluded through `.gitignore`.

---

## 🎯 Learning & Development Highlights

This project was developed to gain practical experience in building a complete full-stack application and applying software development concepts in a real-world CRM use case.

### Technical areas demonstrated

* Backend API development
* RESTful architecture
* Authentication and authorization
* Database design and integration
* CRUD operations
* Role and permission management
* Frontend integration
* Error handling and validation
* Modular application structure
* Git and GitHub version control

---

## 🚀 Future Enhancements

Potential improvements include:

* Advanced CRM analytics and visual dashboards
* Email and notification integrations
* Automated follow-up reminders
* Advanced search and filtering
* Customer interaction history
* Exportable reports
* Deployment using cloud infrastructure
* Automated testing with a dedicated test framework
* CI/CD pipeline integration

---

## 👩‍💻 Developer

**Swati Janawade**

MCA Graduate | Python Developer | Full-Stack Developer

Interested in building scalable web applications, REST APIs, and data-driven software solutions.

### GitHub

https://github.com/Swati23216

---

## 📄 License

This project is intended for educational, portfolio, and demonstration purposes.
