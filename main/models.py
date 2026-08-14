from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('institution', 'Institution'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class EssaySubmission(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_IN_REVIEW = 'in_review'
    STATUS_REVIEWED = 'reviewed'
    STATUS_CHOICES = (
        (STATUS_SUBMITTED, 'Awaiting review'),
        (STATUS_IN_REVIEW, 'In review'),
        (STATUS_REVIEWED, 'Reviewed'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='essays')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='essays/pdfs/', blank=True, null=True)

    # AI-generated evaluation (set once, at submission time)
    score = models.IntegerField(default=0, help_text="AI-generated score out of 100")
    feedback = models.TextField(blank=True, null=True, help_text="AI-generated feedback")

    # Teacher override (optional, set from the review screen)
    teacher_score = models.IntegerField(blank=True, null=True, help_text="Teacher-assigned score out of 100")
    teacher_feedback = models.TextField(blank=True, null=True, help_text="Teacher's written assessment")
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_essays'
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.username}"

    @property
    def display_score(self):
        """The score that should be shown to the student: teacher override wins."""
        return self.teacher_score if self.teacher_score is not None else self.score

    @property
    def display_feedback(self):
        """The feedback that should be shown to the student: teacher override wins."""
        return self.teacher_feedback if self.teacher_feedback else self.feedback


class Comment(models.Model):
    """A single note in the ongoing feedback thread on a submission."""
    submission = models.ForeignKey(EssaySubmission, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submission_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.submission.title}"
