from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings 
import requests
import json


from .models import ChatMessage
from django.http import JsonResponse
import json

# Import your model for receiving bugs
from .models import ReceivedBugReport

# ✅ Configurations
SIMS_API_SECRET = "BetaCode_Super_Secret_Key_2026"
SIMS_BASE_URL = "https://sims-ax72.onrender.com" 

User = get_user_model()

# ==========================================
# 1. YOUR ORIGINAL BETACODE WEBSITE VIEWS
# ==========================================

def home(request):
    return render(request, 'core/home.html')

def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('developer_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('developer_dashboard')
        else:
            messages.error(request, "Invalid credentials or you do not have staff access.")
            
    return render(request, 'core/login.html')

def staff_logout(request):
    logout(request)
    return redirect('home')

@login_required(login_url='/login/')
def developer_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied. You are not a staff member.")

    # ✅ FIX: Read directly from the BetaCode database
    bugs = ReceivedBugReport.objects.all().order_by('-created_at')
    
    # Fetch all developers for the "Assign To" dropdown
    developers = User.objects.filter(is_staff=True)

    return render(request, 'core/bugs.html', {
        'bugs': bugs,
        'api_connected': True, 
        'bug_count': bugs.count(),
        'developers': developers,
    })

# ==========================================
# 2. NEW VIEWS FOR MANAGING BUGS (TICKETING)
# ==========================================

@login_required(login_url='/login/')
def update_bug(request, bug_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied.")
    
    if request.method == 'POST':
        bug = get_object_or_404(ReceivedBugReport, id=bug_id)
        
        # Update fields
        bug.status = request.POST.get('status', bug.status)
        bug.developer_notes = request.POST.get('developer_notes', bug.developer_notes)
        
        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            bug.assigned_to_id = assigned_to_id
        else:
            bug.assigned_to = None

        bug.save()
        messages.success(request, f"Bug #{bug.id} updated successfully.")
    
    return redirect('developer_dashboard')

@login_required(login_url='/login/')
def delete_bug(request, bug_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied.")
    
    if request.method == 'POST':
        bug = get_object_or_404(ReceivedBugReport, id=bug_id)
        bug.delete()
        messages.success(request, "Bug report deleted.")
    
    return redirect('developer_dashboard')

@login_required(login_url='/login/')
def notify_user_resolved(request, bug_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied.")
    
    if request.method == 'POST':
        bug = get_object_or_404(ReceivedBugReport, id=bug_id)
        
        # Tell the SIMS API to send the email to the reporter
        try:
            headers = {'X-BetaCode-Secret': SIMS_API_SECRET}
            payload = {'bug_id': bug.id, 'reporter': bug.reporter_name}
            
            response = requests.post(
                f"{SIMS_BASE_URL}/bugs/api/notify-resolved/", 
                json=payload, 
                headers=headers, 
                timeout=20
            )
            
            if response.status_code == 200:
                bug.is_user_notified = True
                bug.save()
                messages.success(request, "Notification sent to user via SIMS.")
            else:
                messages.error(request, f"SIMS failed to send notification. Status: {response.status_code}")
        except Exception as e:
            messages.error(request, f"Connection error: {e}")
            
    return redirect('developer_dashboard')

# ==========================================
# 3. EXTERNAL API ENDPOINTS
# ==========================================

@csrf_exempt
def receive_bug_from_sims(request):
    if request.method == 'POST':
        if request.headers.get('X-BetaCode-Secret') != SIMS_API_SECRET:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        try:
            data = json.loads(request.body)
            
            bug = ReceivedBugReport.objects.create(
                title=data.get('title'),
                description=data.get('description'),
                page_url=data.get('page_url'),
                reporter_name=data.get('reporter'),
                screenshot_url=data.get('screenshot'),
                voice_note_url=data.get('voice_note'),
            )
            
            return JsonResponse({'success': True, 'bug_id': bug.id}, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)



from .forms import DeveloperCreationForm
from .models import DeveloperProfile

@login_required(login_url='/login/')
def manage_developers(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied.")
    
    developers = DeveloperProfile.objects.select_related('user').all()
    
    if request.method == 'POST':
        form = DeveloperCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New developer added successfully.")
            return redirect('manage_developers')
    else:
        form = DeveloperCreationForm()

    return render(request, 'core/manage_developers.html', {
        'developers': developers,
        'form': form,
    })

@login_required(login_url='/login/')
def toggle_developer_status(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied.")
    
    profile = get_object_or_404(DeveloperProfile, user_id=user_id)
    profile.is_available = not profile.is_available
    profile.save()
    return redirect('manage_developers')





@login_required(login_url='/login/')
def chat_room(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied. Staff only.")
    
    # Fetch the last 50 messages for initial load
    messages = ChatMessage.objects.select_related('sender').all()[:50]
    return render(request, 'core/chat.html', {'chat_messages': messages})

@login_required(login_url='/login/')
def chat_api(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            msg_text = data.get('message', '').strip()
            if msg_text:
                new_msg = ChatMessage.objects.create(sender=request.user, message=msg_text)
                return JsonResponse({'status': 'success', 'message_id': new_msg.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'GET':
        # Get messages sent after a specific ID (for polling)
        last_id = request.GET.get('last_id', 0)
        new_messages = ChatMessage.objects.filter(id__gt=last_id).select_related('sender')
        
        data = []
        for msg in new_messages:
            data.append({
                'id': msg.id,
                'sender_name': msg.sender.get_full_name() or msg.sender.username,
                'message': msg.message,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'is_me': msg.sender == request.user,
            })
        return JsonResponse({'messages': data})

    return JsonResponse({'error': 'Invalid method'}, status=405)