from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings 
import requests
import json

# Import your new model for receiving bugs
from .models import ReceivedBugReport

# ✅ Configurations
SIMS_API_SECRET = "BetaCode_Super_Secret_Key_2026"
# ✅ Change this to 127.0.0.1:8000 while testing locally, and your Render URL when live
SIMS_BASE_URL = "http://127.0.0.1:8000" 

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

    bugs = []
    api_connected = False  
    error_msg = ""

    try:
        headers = {'X-BetaCode-Secret': SIMS_API_SECRET}
        response = requests.get(f"{SIMS_BASE_URL}/bugs/api/reports/", headers=headers, timeout=5)
        
        if response.status_code == 200:
            bugs = response.json().get('bugs', [])
            api_connected = True
        else:
            error_msg = f"SIMS API returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to the SIMS server. Is it running on port 8000?"
    except Exception as e:
        error_msg = str(e)

    if error_msg:
        messages.error(request, error_msg)

    return render(request, 'core/bugs.html', {
        'bugs': bugs,
        'api_connected': api_connected, 
        'bug_count': len(bugs)
    })

@login_required(login_url='/login/')
def resolve_bug_remote(request, bug_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access Denied.")

    try:
        headers = {'X-BetaCode-Secret': SIMS_API_SECRET}
        response = requests.post(
            f"{SIMS_BASE_URL}/bugs/api/reports/", 
            headers=headers, 
            json={'bug_id': bug_id}
        )
        if response.status_code == 200:
            messages.success(request, "Bug marked as resolved in SIMS.")
        else:
            messages.error(request, "Failed to update bug status.")
    except Exception as e:
        messages.error(request, f"Connection error: {e}")
        
    return redirect('developer_dashboard')


# ==========================================
# 2. NEW API ENDPOINT TO RECEIVE BUGS FROM SIMS
# ==========================================

@csrf_exempt
def receive_bug_from_sims(request):
    if request.method == 'POST':
        # 1. Verify the request is actually from your SIMS app
        if request.headers.get('X-BetaCode-Secret') != SIMS_API_SECRET:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        try:
            # 2. Read the JSON data sent by SIMS
            data = json.loads(request.body)
            
            # 3. Save it to the BetaCode database
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