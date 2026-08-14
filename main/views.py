from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from main.models import EssaySubmission, UserProfile, Comment
from main.forms import SignUpForm, InstitutionCreateUserForm
from main.pipeline import get_feedback, format_feedback_text

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


# ==========================================
# HELPER FUNCTIONS
# ==========================================


def get_role(user):
    """Return the user's role ('student' / 'teacher' / 'institution').

    Falls back sensibly for accounts that don't have a UserProfile yet
    (e.g. a superuser created with `createsuperuser`), so admin accounts
    don't get locked out of every page.
    """
    profile = getattr(user, "profile", None)
    if profile is not None:
        return profile.role
    if user.is_superuser:
        return "institution"
    if user.is_staff:
        return "teacher"
    return "student"


def redirect_user_by_role(user):
    """Route a logged-in user to their home dashboard based on role."""
    role = get_role(user)
    if role == "institution":
        return redirect("institution_dashboard")
    if role == "teacher":
        return redirect("teacher_dashboard")
    return redirect("student")


def role_required(*roles):
    """Decorator: only let users with one of `roles` through. Everyone else
    gets bounced to their own dashboard rather than an error page."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if get_role(request.user) not in roles:
                messages.error(request, "You don't have access to that page.")
                return redirect_user_by_role(request.user)
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def notify_by_email(subject, message, recipient_email):
    """Best-effort email notification. Never raises — returns an error
    string on failure so the caller can flash a warning instead of losing
    the user's work over a broken SMTP config."""
    if not recipient_email:
        return "No email address on file for this account."
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)
    except Exception as exc:
        return str(exc)
    return None


# ==========================================
# 1. AUTHENTICATION & ROUTING VIEWS
# ==========================================


def login_view(request):
    """Handles user login and routes them to their specific portal."""
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect_user_by_role(user)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "main/login.html")


def signup_view(request):
    """Handles user account registration."""
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            error = notify_by_email(
                "Welcome to the Writing Feedback Portal",
                f"Hello {user.username},\n\nYour account has been created successfully.\n\n"
                "Best regards,\nThe Writing Feedback Portal Team",
                user.email,
            )
            if error:
                messages.warning(request, f"Account created, but the welcome email could not be sent: {error}")
            else:
                messages.success(request, "Account created successfully!")

            return redirect_user_by_role(user)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    label = field.replace("_", " ").capitalize()
                    messages.error(request, f"{label}: {error}")
    else:
        form = SignUpForm()

    return render(request, "main/signup.html", {"form": form})


def logout_view(request):
    """Logs out the user and redirects to the login screen."""
    logout(request)
    return redirect("login")


# ==========================================
# 2. STUDENT DASHBOARD
# ==========================================


@role_required("student")
def student_view(request):
    """Handles essay submission (Text or PDF) and renders past submissions."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        grading_prompt = request.POST.get("grading_prompt", "").strip()
        pdf_file = request.FILES.get("pdf_file")

        if pdf_file and not content:
            if PdfReader is None:
                messages.error(request, "PDF parsing is unavailable (pypdf not installed).")
            else:
                try:
                    reader = PdfReader(pdf_file)
                    extracted_text = ""
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
                    content = extracted_text.strip()
                    pdf_file.seek(0)
                except Exception as e:
                    messages.error(request, f"Could not read PDF file: {str(e)}")

        if title and content:
            feedback_data = get_feedback(content, grading_prompt=grading_prompt)
            feedback_text = format_feedback_text(feedback_data)
            overall_score = int(feedback_data.get("overall_score_1_to_6") or 0)
            score_0_100 = min(100, max(0, round((overall_score / 6) * 100)))

            submission = EssaySubmission.objects.create(
                student=request.user,
                title=title,
                content=content,
                pdf_file=pdf_file,
                score=score_0_100,
                feedback=feedback_text,
                status=EssaySubmission.STATUS_SUBMITTED,
            )

            error = notify_by_email(
                f"Evaluation complete for '{title}'",
                f"Hello {request.user.username},\n\n"
                f"Your essay '{title}' has been evaluated.\n\n"
                f"Score: {score_0_100}/100\n\n"
                f"Feedback:\n{feedback_text}\n\n"
                "A teacher may review this further before it's finalized.\n\n"
                "Best regards,\nThe Writing Feedback Portal Team",
                request.user.email,
            )
            if error:
                messages.warning(request, f"Essay submitted, but the notification email failed: {error}")
            else:
                messages.success(request, "Essay submitted successfully! Check back for teacher feedback.")

            return redirect("submission_detail", submission_id=submission.id)
        else:
            messages.error(request, "Please provide a title and either typed text or a valid PDF file.")

    user_essays = EssaySubmission.objects.filter(student=request.user).annotate(
        comment_count=Count("comments")
    )
    return render(request, "main/student.html", {"essays": user_essays})


# ==========================================
# 3. SUBMISSION DETAIL + COMMENTS (shared by student/teacher/institution)
# ==========================================


@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(EssaySubmission, pk=submission_id)
    role = get_role(request.user)

    if not (role in ("teacher", "institution") or submission.student == request.user):
        messages.error(request, "You don't have access to that submission.")
        return redirect_user_by_role(request.user)

    if request.method == "POST":
        if role not in ("teacher", "institution"):
            messages.error(request, "Only teachers can add comments.")
            return redirect("submission_detail", submission_id=submission.id)

        body = request.POST.get("comment_body", "").strip()
        if body:
            Comment.objects.create(submission=submission, author=request.user, body=body)
            if submission.status == EssaySubmission.STATUS_SUBMITTED:
                submission.status = EssaySubmission.STATUS_IN_REVIEW
                submission.save(update_fields=["status"])
            messages.success(request, "Comment posted.")
        return redirect("submission_detail", submission_id=submission.id)

    context = {
        "s": submission,
        "comments": submission.comments.select_related("author"),
        "can_comment": role in ("teacher", "institution"),
        "can_review": role in ("teacher", "institution"),
    }
    return render(request, "main/submission_detail.html", context)


# ==========================================
# 4. TEACHER DASHBOARD
# ==========================================


@role_required("teacher", "institution")
def teacher_dashboard(request):
    """Displays all submitted essays across all students for evaluation."""
    all_submissions = EssaySubmission.objects.select_related("student").annotate(
        comment_count=Count("comments")
    )
    context = {
        "submissions": all_submissions,
        "total_students": EssaySubmission.objects.values("student").distinct().count(),
        "pending_count": all_submissions.filter(status=EssaySubmission.STATUS_SUBMITTED).count(),
    }
    return render(request, "main/teacher_dashboard.html", context)


@role_required("teacher", "institution")
def review_submission(request, pk):
    """Let a teacher post/adjust an official score+feedback and leave
    thread comments, then notify the student."""

    submission = get_object_or_404(EssaySubmission, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "comment":
            body = request.POST.get("comment_body", "").strip()
            if body:
                Comment.objects.create(submission=submission, author=request.user, body=body)
                if submission.status == EssaySubmission.STATUS_SUBMITTED:
                    submission.status = EssaySubmission.STATUS_IN_REVIEW
                    submission.save(update_fields=["status"])
                messages.success(request, "Comment posted.")
            return redirect("review_submission", pk=pk)

        # Otherwise: saving the official review (score + feedback override)
        override_score = request.POST.get("teacher_score", "").strip()
        override_feedback = request.POST.get("teacher_feedback", "").strip()

        if override_score:
            try:
                score_val = int(override_score)
                if not (0 <= score_val <= 100):
                    raise ValueError
                submission.teacher_score = score_val
            except ValueError:
                messages.error(request, "Score must be a whole number between 0 and 100.")
                return redirect("review_submission", pk=pk)

        submission.teacher_feedback = override_feedback or None
        submission.status = EssaySubmission.STATUS_REVIEWED
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.save()

        error = notify_by_email(
            f"Your submission '{submission.title}' was reviewed by a teacher",
            f"Hello {submission.student.username},\n\n"
            f"A teacher has reviewed your submission '{submission.title}'.\n\n"
            f"Final grade: {submission.display_score}/100\n\n"
            f"Teacher remarks:\n{submission.display_feedback}\n\n"
            "Best regards,\nThe Writing Feedback Portal Team",
            submission.student.email,
        )
        if error:
            messages.warning(request, f"Review saved, but the notification email failed: {error}")
        else:
            messages.success(request, "Review saved and student notified via email.")

        return redirect("teacher_dashboard")

    context = {
        "submission": submission,
        "comments": submission.comments.select_related("author"),
    }
    return render(request, "main/review_submission.html", context)


# ==========================================
# 5. INSTITUTION DASHBOARD
# ==========================================


@role_required("institution")
def institution_dashboard(request):
    """Institution admin dashboard: org-wide metrics, user management, and
    oversight of teacher review activity."""

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_user":
            form = InstitutionCreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Account created.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return redirect("institution_dashboard")

        if action == "toggle_active":
            user_id = request.POST.get("user_id")
            target = get_object_or_404(User, pk=user_id)
            if target == request.user:
                messages.error(request, "You can't deactivate your own account.")
            else:
                target.is_active = not target.is_active
                target.save(update_fields=["is_active"])
                state = "activated" if target.is_active else "deactivated"
                messages.success(request, f"{target.username} was {state}.")
            return redirect("institution_dashboard")

    total_users = User.objects.count()
    total_teachers = UserProfile.objects.filter(role="teacher").count()
    total_students = UserProfile.objects.filter(role="student").count()
    total_submissions = EssaySubmission.objects.count()
    pending_review = EssaySubmission.objects.filter(status=EssaySubmission.STATUS_SUBMITTED).count()

    teachers = User.objects.filter(profile__role="teacher").order_by("username")
    students = User.objects.filter(profile__role="student").order_by("username")

    recent_reviews = (
        EssaySubmission.objects.filter(status=EssaySubmission.STATUS_REVIEWED)
        .select_related("student", "reviewed_by")
        .order_by("-reviewed_at")[:15]
    )

    context = {
        "total_users": total_users,
        "total_teachers": total_teachers,
        "total_students": total_students,
        "total_submissions": total_submissions,
        "pending_review": pending_review,
        "teachers": teachers,
        "students": students,
        "recent_reviews": recent_reviews,
        "create_user_form": InstitutionCreateUserForm(),
    }

    return render(request, "main/institution_dashboard.html", context)
