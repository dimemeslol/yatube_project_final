from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import (
    CreationForm,
    PasswordChangeForm,
    PasswordResetForm,
)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(CreateView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class MyPasswordReset(PasswordResetForm):
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'
