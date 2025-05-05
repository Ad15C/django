from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=get_user_model().ROLE_CHOICES, required=False, initial='client')
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'role', 'password1', 'password2')
        labels = {
            'username': 'Nom d\'utilisateur',
            'email': 'Adresse email',
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 6:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 6 caractères.")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2


class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class EditProfileForm(forms.ModelForm):
    password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False  # Make this optional
    )

    class Meta:
        model = User
        fields = ['username', 'email']  # You can keep 'username' and 'email' fields
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 6:  # Optional validation for password strength
            raise forms.ValidationError("Le mot de passe doit contenir au moins 6 caractères.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)

        # If a new password is provided, set it
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # This will hash the password and store it securely

        if commit:
            user.save()
        return user
