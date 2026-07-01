from django import forms
from django.contrib.auth.forms import AuthenticationForm


class EmailAuthenticationForm(AuthenticationForm):
    """
    Authentication form that uses email as the USERNAME_FIELD for login.
    """

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"autofocus": True, "class": "form-control form-control-custom"}
        ),
    )
