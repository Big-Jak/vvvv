# Setup Guide for Writing Feedback Portal with MySQL

## Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MySQL Database

#### Option A: Using the provided SQL schema
```bash
mysql -u root -p < database_schema.sql
```

#### Option B: Manual setup
```sql
CREATE DATABASE writing_feedback CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON writing_feedback.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure Environment Variables
Copy the example environment file and update it with your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your actual database and email credentials:
```
DB_NAME=writing_feedback
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=true
```

### 4. Run Django Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

## Email Configuration

### For Gmail:
1. Enable 2-Factor Authentication on your Google Account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this app password in `EMAIL_HOST_PASSWORD`

### For other email providers:
Update the `.env` file with your provider's SMTP settings.

## Database Connection Details

The application now uses MySQL instead of SQLite. The connection settings are in `project/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "writing_feedback"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),
        ...
    }
}
```

## Features Implemented

### Signup Page Enhancements:
1. ✅ Password validation (greater than 8 characters, at least one number)
2. ✅ Role picker (student, teacher, institution)
3. ✅ Password visibility toggle for both password and confirmation fields
4. ✅ Email system that sends welcome email after account creation
5. ✅ Redirect to login page after successful signup (instead of auto-login)

### Database:
1. ✅ MySQL database schema provided in `database_schema.sql`
2. ✅ Database connection configured for MySQL
3. ✅ Dependencies added to `requirements.txt`

## Troubleshooting

### MySQL Connection Issues
If you encounter connection errors:
1. Verify MySQL is running: `mysql -u root -p`
2. Check database credentials in `.env`
3. Ensure the database exists: `SHOW DATABASES;`
4. Verify user permissions: `SHOW GRANTS FOR 'your_user'@'localhost';`

### Email Issues
If emails are not sending:
1. Check email credentials in `.env`
2. Verify SMTP settings for your email provider
3. Check Django logs for error messages
4. For testing, emails will be printed to console if EMAIL_HOST is not set

### Migration Issues
If migrations fail:
1. Drop and recreate the database
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`

## Security Notes
- Never commit `.env` file to version control
- Use strong database passwords
- Use app-specific passwords for email accounts
- Update `SECRET_KEY` in production
- Set `DEBUG = False` in production
