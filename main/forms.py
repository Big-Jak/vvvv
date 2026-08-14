import re

from django import forms
from django.contrib.auth.models import User

from main.models import UserProfile


class BaseAccountForm(forms.Form):
    """Shared username/password validation used by both self-signup and
    institution-created accounts."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    confirm_password = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            return password

        if len(password) <= 8:
            raise forms.ValidationError("Password must be greater than 8 characters.")

        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one number.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        return cleaned_data


class SignUpForm(BaseAccountForm):
    """Public self-service signup. Anyone can pick their own role."""

    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(),
    )

    def save(self):
        role = self.cleaned_data["role"]
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            is_staff=(role in ("teacher", "institution")),
        )
        UserProfile.objects.create(user=user, role=role)
        return user


class InstitutionCreateUserForm(BaseAccountForm):
    """Used by an institution admin to create a teacher or student account
    directly from the institution dashboard. Deliberately does not allow
    creating another institution account."""

    role = forms.ChoiceField(
        choices=[c for c in UserProfile.ROLE_CHOICES if c[0] != "institution"],
        widget=forms.Select(),
    )

    def save(self):
        role = self.cleaned_data["role"]
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            is_staff=(role == "teacher"),
        )
        UserProfile.objects.create(user=user, role=role)
        return user
