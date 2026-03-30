# The Creative Nexus

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)
![Django REST Framework](https://img.shields.io/badge/DRF-3.15-A30000?style=for-the-badge&logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap)

A digital community platform designed to connect, empower, and inspire the youth of Ghana through technology and the creative arts.

---

## Mission

My mission is to inspire and empower the youth of Ghana through technology and the creative arts. In the context of Africa, the creative sector, otherwise known as the “orange economy” is often and heavily overlooked, but in recent years has proven that it has the potential to drive economic growth not only in Ghana but in Africa. Despite this, this sector of the economy remains heavily underfunded and largely informal. This project establishes a structured digital community where like-minded individuals can interact, share skills and collaborate. By providing a bridge between the raw talent that the youth possess and industry standards, the platform fosters a thriving arts ecosystem that promotes youth self-employment and digital literacy in Ghana.

## Problem Statement

The creative economy in Ghana represents a significant but under-funded and overlooked frontier for youth development. Emerging artists and creative students face a critical problem: the lack of infrastructure that facilitates skill-sharing, mentorship, and professional growth. Global platforms often have high barriers to entry and payment incompatibilities. The Creative Nexus aims to solve this by providing a localized, culturally relevant digital community that bridges these gaps, helping Ghanaian creators monetize their skills and compete in a global economy.

## Key Features

### Backend
- **User Authentication:** Custom user model with email verification and 4 distinct roles (Creator, Client, Mentor, Admin).
- **User Profiles:** Role-based profiles with customizable bio, skills, location, and profile pictures.
- **Portfolio Management:** Creators can build and manage portfolios, uploading various work types (Digital Art, Graphic Design, Animation, etc.).
- **Collaboration System:** Send, accept, or reject collaboration requests with details on skills, timeline, and budget.
- **Project Management:** Automatically create projects from accepted collaborations with status tracking (Draft, In Progress, Completed).
- **Notification System:** Users receive email and in-app notifications for key events like collaboration requests and project updates.
- **Rating System:** A 1-5 star rating system with reviews for completed collaborations.
- **Audit Trail:** Immutable logs for all major transactions and status changes.

### Frontend
- **Modern UI/UX:** A responsive, Instagram-inspired aesthetic built with Bootstrap 5, using a consistent design system based on CSS variables and Lucide icons.
- **Public Pages:** A beautiful home page with a gallery preview and an explore page to discover creators.
- **User Dashboard:** A central hub for users to view stats, manage their works, and track collaborations and notifications.
- **Interactive Portfolios:** Gallery displays with like/view functionality and modals for collaboration and work uploads.
- **Full Password Reset Flow:** Secure, email-based password reset functionality.
- **Custom Error Pages:** Styled 404 and 500 pages to maintain a professional user experience.

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** SQLite3 (for development), PostgreSQL (for production)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **File Storage:** Local storage (for development), AWS S3 (for production)
- **Icons:** Lucide Icons

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.10+
- `pip` package manager

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/The-Creative-Nexus.git
    cd The-Creative-Nexus
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the project root directory (where `manage.py` is) and add the following variables. Use the `.env.example` as a template.

    ```dotenv
    # Django settings
    SECRET_KEY='your-django-secret-key'
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Email settings (for Gmail SMTP)
    EMAIL_HOST_PASSWORD='your-google-app-password'
    ```
    > **Note:** For `EMAIL_HOST_PASSWORD`, you must generate a 16-character "App Password" from your Google Account settings.

4.  **Apply database migrations:**
    ```bash
    python3 manage.py migrate
    ```

5.  **Populate the database with sample data (Optional but Recommended):**
    This command creates sample users, portfolios, and creative works.
    ```bash
    python3 manage.py populate_db --clear
    ```

6.  **Run the development server:**
    ```bash
    python3 manage.py runserver
    ```
    The application will be available at `http://localhost:8000/`.

## Usage

- **Admin Panel:** `http://localhost:8000/admin/`
- **API Documentation:** `http://localhost:8000/api/docs/`

### Creating a Superuser
To access the admin panel with full permissions, create a superuser account:
```bash
python3 manage.py createsuperuser
```
Follow the prompts to set your username, email, and password.

### Test Accounts
If you used the `populate_db` command, you can log in with the following credentials:
- **Creators/Clients/Mentors:** Any of the sample users with the password `testpass123`.

## Testing

The project includes a comprehensive test suite with **58 tests** covering API endpoints and template view integrations.

To run the full test suite:
```bash
python3 manage.py test --verbosity=2
```

All tests should pass with a 100% success rate.

## Project Structure

```
The_creative_nexus/
├── accounts/              # User authentication & profiles
│   ├── models.py         # CustomUser, UserProfile
│   ├── views.py          # Auth views & APIs
│   └── ...
├── core/                  # Main app features
│   ├── models.py         # Portfolio, Works, Collab, Project
│   ├── views.py          # API views
│   ├── template_views.py # Template rendering views
│   └── ...
├── templates/             # HTML templates
│   ├── base.html
│   ├── accounts/
│   └── core/
├── static/                # CSS, JS, images
├── the_creative_nexus/    # Project settings
│   ├── settings.py
│   └── urls.py
├── .env                   # Environment variables (ignored by Git)
├── manage.py              # Django CLI
└── db.sqlite3             # Database
```

## 🎨 Design System

The frontend is built with a cohesive, Instagram-inspired design system that relies on:
- **CSS Variables:** For consistent colors, spacing, border-radius, and shadows.
- **Lucide Icons:** A modern, lightweight icon set used throughout the application.
- **Bootstrap 5:** For a responsive grid system and core components.

This ensures a clean, professional, and maintainable user interface that is fully responsive across mobile, tablet, and desktop devices.

---

*This README was generated by combining information from the project's development and testing reports.*