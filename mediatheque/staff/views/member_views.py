from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django import forms
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from mediatheque.staff.decorators import role_required

User = get_user_model()


# Formulaire pour créer un membre
class MemberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']


# Liste des membres avec pagination
@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_view_members', raise_exception=True)
def member_list(request):
    # Exclure pk null ou 0, puis ordonner par username (ou un autre champ pertinent)
    members = User.objects.exclude(pk__isnull=True).exclude(pk=0).exclude(pk=request.user.pk).order_by('username')
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(members, 10)  # 10 membres par page
    page_obj = paginator.get_page(page_number)
    return render(request, 'staff/members/member_list.html', {'page_obj': page_obj})


# Créer un membre
@login_required
@role_required(User.STAFF)
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
@login_required
@role_required(User.STAFF)
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
@login_required
def member_detail(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if pk == 0:
        return redirect('staff:liste_membres')

    if not request.user.has_perm('authentification.can_view_members'):
        return HttpResponseForbidden()

    member = get_object_or_404(User, pk=pk)
    return render(request, 'staff/members/member_detail.html', {'member': member})


@login_required
@role_required(User.STAFF)
@permission_required('authentification.can_delete_member', raise_exception=True)
def delete_member(request, pk):
    member = get_object_or_404(User, id=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, "Membre supprimé avec succès !")
        return redirect('staff:liste_membres')
    return render(request, 'staff/members/confirm_delete.html', {'member': member})
