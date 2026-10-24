from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden
import requests

SIMS_API_SECRET = "BetaCode_Super_Secret_Key_2026"

# ✅ Change this to 127.0.0.1:8000 while testing locally
SIMS_BASE_URL = "http://127.0.0.1:8000" 

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
    api_connected = False  # ✅ Track if the API call was successful
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
        'api_connected': api_connected, # ✅ Pass to template
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