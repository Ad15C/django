from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django import forms
from django.core.paginator import Paginator

User = get_user_model()


# Formulaire pour créer un membre
class MemberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']


# Liste des membres avec pagination
@permission_required('authentification.can_view_members', raise_exception=True)
def member_list(request):
    members = User.objects.all()
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(members, 10)  # 10 membres par page
    page_obj = paginator.get_page(page_number)
    return render(request, 'staff/members/member_list.html', {'page_obj': page_obj})


# Créer un membre
@permission_required('authentification.can_add_member', raise_exception=True)
def create_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Membre créé avec succès!")
            return redirect('staff:liste_membres')  # redirection vers la liste des membres
        else:
            messages.error(request, "Erreur lors de la création du membre.")
    else:
        form = MemberForm()
    return render(request, 'staff/members/create_member.html', {'form': form})


# Mettre à jour un membre
@permission_required('authentification.can_update_member', raise_exception=True)
def update_member(request, pk):
    member = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Membre mis à jour avec succès!")
            return redirect('staff:liste_membres')  # redirection vers la liste des membres
        else:
            messages.error(request, "Erreur lors de la mise à jour du membre.")
    else:
        form = MemberForm(instance=member)
    return render(request, 'staff/members/update_member.html', {'form': form, 'member': member})


# Voir les détails d'un membre
@permission_required('authentification.can_view_members', raise_exception=True)
def member_detail(request, pk):
    member = get_object_or_404(User, pk=pk)
    return render(request, 'staff/members/member_detail.html', {'member': member})
