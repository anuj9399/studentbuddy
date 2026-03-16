from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.models import StudentProfile
from django.conf import settings






@login_required
def dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    # default career card text (shown on dashboard)
    career_title = "Career Guide"

    if profile.stream:
        career_title = "Suggested Career"

    return render(request, "dashboard.html", {
        "career_title": career_title,
        "profile": profile
    })


@login_required
def career(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    stream = (profile.stream or "").lower()

    career_map = {
        "mechanical": [
            "Mechanical Design Engineer",
            "Automobile Engineer",
            "Robotics Engineer",
            "Manufacturing Engineer",
            "CAD Specialist",
        ],
        "computer": [
            "Software Developer",
            "Data Scientist",
            "AI Engineer",
            "Cybersecurity Specialist",
            "Cloud Engineer",
        ],
        "civil": [
            "Structural Engineer",
            "Construction Manager",
            "Urban Planner",
            "Site Engineer",
        ],
        "electrical": [
            "Power Systems Engineer",
            "Electronics Engineer",
            "Control Systems Engineer",
        ],
    }

    suggestions = []

    for key in career_map:
        if key in stream:
            suggestions = career_map[key]

    if not suggestions:
        suggestions = [
            "Project Manager",
            "Entrepreneur",
            "Research Assistant",
            "Higher Studies (M.Tech / MBA)",
        ]

    return render(request, "career.html", {
        "suggestions": suggestions,
        "profile": profile
    })



from datetime import datetime
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def study_planner(request):
    plan = None

    if request.method == "POST":
        subject = request.POST.get("subject")
        exam_date = request.POST.get("exam_date")

        # convert exam date to days left
        exam = datetime.strptime(exam_date, "%Y-%m-%d")
        today = datetime.today()
        days_left = (exam - today).days

        prompt = f"""
Create exactly 6 study phases.

Each phase must be ONE short sentence.
No paragraphs.
No bullet points.
Only 6 lines total.

Subject: {subject}
Days left: {days_left}
"""

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://studentbuddy-v5ah.onrender.com",
            "X-Title": "StudentBuddy",
        }

        data = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()

        raw_plan = result["choices"][0]["message"]["content"]

        # split and keep only 6 lines
        lines = [line.strip() for line in raw_plan.split("\n") if line.strip()]
        plan = lines[:6]

    return render(request, "planner.html", {"plan": plan})


