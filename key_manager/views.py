import uuid
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AccessKey
from users.models import CustomUser
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator


@login_required
def home(request):
    if request.user.is_staff:
        keys = AccessKey.objects.all().order_by('user__email')
        paginator = Paginator(keys, 10)  # Show 10 keys per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        grouped_keys = {}
        for key in page_obj:
            email = key.user.email
            if email not in grouped_keys:
                grouped_keys[email] = []
            grouped_keys[email].append(key)

        context = {
            'grouped_keys': grouped_keys,
            'page_obj': page_obj,
        }
    else:
        now = timezone.now()
        expired_keys = AccessKey.objects.filter(expiry_date__lt=now, status='active')

        for key in expired_keys:
            key.status = 'expired'
            key.save()  
            
        keys = AccessKey.objects.filter(user=request.user).order_by('-date_of_procurement')
        context = {
            'keys': keys,
        } 
    return render(request, 'key_manager/home.html', context) 
            

@login_required
@user_passes_test(lambda u: u.is_staff)
def revoke_key(request, key_id):
    key = get_object_or_404(AccessKey, id=key_id)
    key.revoke()
    messages.success(request, 'The key has been revoked successfully.')
    return redirect('home')

@login_required
def request_key(request):
    if AccessKey.objects.filter(user=request.user, status='active').exists():
        messages.error(request, 'You already have an active key and cannot request another.')
    else:
        new_key = AccessKey.objects.create(
            user=request.user,
            key=str(uuid.uuid4()),  # Generating a random alphanumeric key
            expiry_date=timezone.now() + timezone.timedelta(days=4*30)  # Approx. 4 months
        )
        messages.success(request, 'A new key has been granted.')
    
    return redirect('home')





@user_passes_test(lambda u: u.is_staff)
def revoke_key_view(request, key_id):
    access_key = get_object_or_404(AccessKey, id=key_id)
    access_key.status = 'revoked'
    access_key.save()
    return redirect('home')

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
def check_active_key(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Email parameter is required'}, status=400)

        try:
            user = get_object_or_404(CustomUser, email=email)
            access_key = AccessKey.objects.filter(user=user, status='active').first()
            if access_key:
                return JsonResponse({
                    'key': access_key.key,
                    'status': access_key.status,
                    'date_of_procurement': access_key.date_of_procurement,
                    'expiry_date': access_key.expiry_date
                }, status=200)
            else:
                return JsonResponse({'error': 'No active key found for this email'}, status=404)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User with this email does not exist'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request, exception):
    return render(request, '500.html', status=500)
