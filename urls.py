from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    # Authentication & Navigation
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),  # <-- MUST HAVE name='signup'
    path("logout/", views.logout_view, name="logout"),
    # Dashboards
    path("student/", views.student_view, name="student"),
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("institution/", views.institution_dashboard, name="institution_dashboard"),
    path('submission/<int:pk>/review/', views.review_submission, name='review_submission'),
    # Password Reset Routes
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="main/password_reset.html",
            email_template_name="main/password_reset_email.html",
            subject_template_name="main/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="main/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="main/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="main/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Submission detail
    path("submission/<int:submission_id>/", views.submission_detail, name="submission_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
