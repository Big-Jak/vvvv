from django.contrib import admin
from main.models import EssaySubmission, UserProfile, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("author", "created_at")


@admin.register(EssaySubmission)
class EssaySubmissionAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "status", "score", "teacher_score", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "student__username")
    inlines = [CommentInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)


admin.site.register(Comment)
