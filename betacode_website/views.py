from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
import requests

# Must match the secret in SIMS
SIMS_API_SECRET = "BetaCode_Super_Secret_Key_2026"
# Replace this with your current SIMS ngrok URL or domain
SIMS_BASE_URL = "https://6bb2-154-162-6-116.ngrok-free.app" 

def home(request):
    """The main landing page for the BetaCode website."""
    return render(request, 'core/home.html')

@staff_member_required
def developer_dashboard(request):
    """Fetch bug reports from SIMS and display on BetaCode."""
    bugs = []
    try:
        headers = {'X-BetaCode-Secret': SIMS_API_SECRET}
        response = requests.get(f"{SIMS_BASE_URL}/bugs/api/reports/", headers=headers)
        if response.status_code == 200:
            bugs = response.json().get('bugs', [])
        else:
            messages.error(request, f"Failed to load bugs. Status: {response.status_code}")
    except Exception as e:
        messages.error(request, f"Could not connect to SIMS server: {e}")

    return render(request, 'core/dashboard.html', {'bugs': bugs})

@staff_member_required
def resolve_bug_remote(request, bug_id):
    """Send a request to SIMS to mark a bug as resolved."""
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