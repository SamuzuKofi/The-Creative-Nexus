# The Creative Nexus - Setup & Usage Guide

## 🚀 Quick Start

### Server is Running At:
```
http://localhost:8000/
```

### Admin Panel:
```
http://localhost:8000/admin/
```

### API Documentation:
```
http://localhost:8000/api/docs/
```

---

## 📋 What's Been Implemented (MVP)

### ✅ Backend Features Completed:
1. **User Authentication System**
   - Custom user model with email verification
   - 4 user roles: Creator, Client, Mentor, Admin
   - Email-based login/registration
   - Email verification tokens

2. **User Profiles**
   - Role-based profiles
   - Customizable bio, skills, location, website
   - Profile pictures with media storage
   - Profile verification system

3. **Portfolio Management**
   - Create portfolios
   - Upload creative works (images, documents, etc.)
   - Work categorization (Digital Art, Graphic Design, Animation, Photography, Video, Music, Writing)
   - View/Like tracking

4. **Collaboration System**
   - Send collaboration requests with details (skills, timeline, budget)
   - Accept/Reject requests
   - Auto-create projects when accepted
   - Collaboration notifications

5. **Project Management**
   - Project tracking with status (Draft → In Progress → Under Review → Completed)
   - Team member management
   - Project status notifications

6. **Notification System**
   - Real-time notifications for collaboration actions
   - Notification types: collaboration requests, acceptances, rejections, project updates
   - Read/unread tracking

7. **Rating System**
   - Rate collaborators after projects
   - 1-5 star ratings with reviews
   - Average rating calculations

### ✅ Frontend Features Completed:
1. **Public Pages**
   - Home page with gallery preview
   - Explore creators with filtering by role/skills
   - Featured works showcase

2. **Authentication Pages**
   - Registration with email verification
   - Login with verification requirement
   - Profile creation using API

3. **Dashboard**
   - Quick stats (views, likes, collaborations)
   - My works gallery
   - Collaboration activity
   - Recent notifications
   - Upload works modal

4. **Portfolio Page**
   - Gallery display of all works
   - Creator information
   - Skills display
   - Contact/Collaborate button

5. **Collaborations Page**
   - Sent requests (pending, accepted, rejected)
   - Received requests with accept/reject buttons
   - Status tracking

6. **Explore Page**
   - Search creators by name/skills
   - Filter by role
   - Creator cards with portfolios
   - Collaboration request modal

7. **Profile Page**
   - Edit profile information
   - Update picture
   - Manage skills and experience
   - Website links

---

## 🔑 Test Account Creation

### Via Registration Page:
1. Go to: `http://localhost:8000/register/`
2. Fill in:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `testpassword123`
   - Role: Choose one (Creator/Client/Mentor/Admin)
3. Check console email output (development email backend)
4. Copy verification link from terminal output
5. Visit the link to verify email
6. Login at: `http://localhost:8000/login/`

### Create Test Users Quickly (Django Shell):
```bash
cd The_creative_nexus
python3 manage.py shell

from accounts.models import CustomUser, UserProfile
from django.contrib.auth import get_user_model

# Create superuser
CustomUser.objects.create_superuser('admin@admin.com', 'admin', 'admin123')

# Create test user
user = CustomUser.objects.create_user(
    email='creator@test.com',
    username='creator_test',
    password='test123',
    first_name='John',
    last_name='Doe'
)
user.email_verified = True
user.save()

# Create profile
UserProfile.objects.create(
    user=user,
    role='creator',
    bio='I am a digital artist',
    skills='Graphic Design, Digital Art, Photography'
)
```

---

## 🎯 Core API Endpoints

### Authentication
- `POST /api/accounts/register/` - Register new user
- `POST /api/accounts/login/` - Login user
- `POST /api/accounts/logout/` - Logout user
- `GET /api/accounts/me/` - Get current user info
- `GET /api/accounts/verify-email/?token=xxx` - Verify email

### User Profiles
- `GET /api/accounts/profiles/` - List all profiles
- `GET /api/accounts/profiles/{id}/` - Get specific profile
- `PATCH /api/accounts/profiles/{id}/` - Update profile
- `GET /api/accounts/profiles/search/?q=skill&role=creator` - Search profiles

### Portfolios
- `GET /api/core/portfolios/` - List all portfolios
- `POST /api/core/portfolios/` - Create portfolio
- `GET /api/core/portfolios/my_portfolio/` - Get own portfolio

### Creative Works
- `GET /api/core/works/` - List all works
- `POST /api/core/works/` - Upload work
- `GET /api/core/works/my_works/` - Get own works
- `POST /api/core/works/{id}/like/` - Like a work
- `POST /api/core/works/{id}/view/` - Record view

### Collaborations
- `GET /api/core/collaborations/` - List user's collaborations
- `POST /api/core/collaborations/` - Create collaboration request
- `POST /api/core/collaborations/{id}/accept/` - Accept request
- `POST /api/core/collaborations/{id}/reject/` - Reject request

### Projects
- `GET /api/core/projects/` - List user's projects
- `POST /api/core/projects/` - Create project
- `POST /api/core/projects/{id}/add_member/` - Add team member
- `POST /api/core/projects/{id}/update_status/` - Update project status

### Notifications
- `GET /api/core/notifications/` - List notifications
- `POST /api/core/notifications/{id}/mark_as_read/` - Mark notification as read
- `GET /api/core/notifications/unread_count/` - Get unread count

### Ratings
- `GET /api/core/ratings/` - List ratings
- `POST /api/core/ratings/` - Create rating
- `GET /api/core/ratings/user_ratings/?user_id=123` - Get user's ratings

---

## 🎨 Design Features

- **Responsive Bootstrap 5 layout** - Mobile-friendly
- **Gradient color scheme** - Purple to pink gradients
- **Gallery grid system** - Auto-responsive image galleries
- **Card-based UI** - Modern, clean card layouts
- **Modal dialogs** - For forms and confirmations
- **Icon integration** - Font Awesome icons throughout
- **Data validation** - Client/server-side validation

---

## 📁 Project Structure

```
The_creative_nexus/
├── accounts/              # User authentication & profiles
│   ├── models.py         # CustomUser, UserProfile
│   ├── views.py          # Auth views & APIs
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # API routes
│   └── admin.py          # Admin interface
├── core/                 # Main app features
│   ├── models.py         # Portfolio, Works, Collab, Project
│   ├── views.py          # API views
│   ├── template_views.py # Template rendering views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # API routes
│   └── admin.py          # Admin interface
├── templates/            # HTML templates
│   ├── base.html        # Base template with Bootstrap
│   ├── accounts/
│   │   ├── register.html
│   │   ├── login.html
│   │   └── profile.html
│   └── core/
│       ├── home.html
│       ├── dashboard.html
│       ├── portfolio.html
│       ├── collaborations.html
│       └── explore.html
├── static/               # CSS, JS, images
├── the_creative_nexus/   # Project settings
│   ├── settings.py      # Django configuration
│   └── urls.py          # Main URL routing
├── manage.py            # Django CLI
└── db.sqlite3           # Database

```

---

## 🔧 Configuration

### Email Settings (in settings.py):
Currently using **console email backend** for development:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

To use Gmail SMTP:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🧪 Testing Guide

### 1. Test User Registration
- Go to `/register/`
- Fill in details with role as "Creator"
- Check Django console for verification email
- Copy token from email in console
- Visit the verification link
- Login with credentials

### 2. Test Portfolio Creation
- Login as creator
- Go to `/dashboard/`
- Create portfolio via modal
- Upload creative works

### 3. Test Collaboration
- Login as User A (creator)
- Go to `/explore/`
- Find another user
- Click "Collaborate"
- Fill in project details
- Submit request

- Logout and login as User B (who received request)
- Go to `/collaborations/`
- See received request
- Click Accept/Reject

### 4. Test API via Swagger
- Visit `/api/docs/`
- Try endpoints directly in browser
- See request/response examples

---

## 📚 Next Steps & Future Enhancements

### For Full Production:
1. **Real Email Service** - Configure Gmail SMTP or Mailgun
2. **Payment Integration** - Stripe/PayPal for project budgets
3. **Real-time Messaging** - WebSockets for live chat
4. **File Storage** - AWS S3  for production media
5. **Search Enhancement** - Elasticsearch for advanced search
6. **Notifications Queue** - Celery + Redis for async tasks
7. **API Rate Limiting** - Throttling for API endpoints
8. **Enhanced Security** - HTTPS, CORS configuration, API keys
9. **Mobile App** - React Native version
10. **Analytics** - User activity tracking and metrics

---

## 💡 Testing Checklist

- [ ] User can register with email verification
- [ ] User can create portfolio and upload works
- [ ] User can explore and search creators
- [ ] User can send collaboration requests
- [ ] Collaboration requests show in received list
- [ ] User can accept/reject collaborations
- [ ] Project auto-creates on acceptance
- [ ] Notifications appear for actions
- [ ] Can rate collaborators
- [ ] API endpoints work via Swagger docs
- [ ] Mobile responsive design works
- [ ] Admin panel shows all data

---

## ⚠️ Important Notes

1. **Development Mode**: DEBUG=True in settings.py (change for production)
2. **Database**: SQLite3 (switch to PostgreSQL for production)
3. **Email**: Console backend (check terminal for emails)
4. **Media Files**: Stored locally in `/media/` folder
5. **Static Files**: Dev server serves them automatically

---

## 🆘 Troubleshooting

### "Port 8000 already in use"
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
# Or run on different port
python3 manage.py runserver 8001
```

### "Module not found" errors
```bash
# Reinstall requirements
pip install -r requirements.txt
```

### Database errors
```bash
# Reset database
rm db.sqlite3
python3 manage.py migrate
```

### Email not sending
- Check console output (development mode sends to terminal)
- Switch to SMTP for production

---

**Created**: March 29, 2026  
**Status**: MVP Complete - Ready for Testing  
**Version**: 1.0
