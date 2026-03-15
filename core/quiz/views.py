import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg, Max, Count
from .models import Quiz, QuizQuestion

SUBJECTS = [
    'Computer Science',
    'Data Structures & Algorithms',
    'Database Management',
    'Operating Systems',
    'Computer Networks',
    'Machine Learning',
    'Artificial Intelligence',
    'Web Development',
    'Python Programming',
    'Java Programming',
    'C Programming',
    'Mathematics',
    'Physics',
    'Chemistry',
    'English',
    'Other',
]

@login_required
def quiz_home(request):
    recent_quizzes = Quiz.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-created_at')[:6]

    stats = Quiz.objects.filter(
        user=request.user,
        status='completed'
    ).aggregate(
        total=Count('id'),
        avg_score=Avg('score'),
        best_score=Max('score'),
    )

    total = stats['total'] or 0
    avg_percentage = 0
    best_percentage = 0

    if total > 0:
        completed_quizzes = Quiz.objects.filter(
            user=request.user,
            status='completed'
        )
        total_percentage = sum(q.get_percentage() for q in completed_quizzes)
        avg_percentage = round(total_percentage / total)
        best_percentage = max(q.get_percentage() for q in completed_quizzes)

    context = {
        'recent_quizzes': recent_quizzes,
        'total_quizzes': total,
        'avg_percentage': avg_percentage,
        'best_percentage': best_percentage,
        'subjects': SUBJECTS,
    }
    return render(request, 'quiz/home.html', context)

@login_required
def create_quiz(request):
    if request.method == 'POST':
        # Capture new form fields
        university = request.POST.get('university', '')
        stream = request.POST.get('stream', '')
        branch = request.POST.get('branch', '')
        year = request.POST.get('year', '')
        pattern = request.POST.get('pattern', '')
        subject = request.POST.get('subject', '').strip()
        topic = request.POST.get('topic', '').strip()
        difficulty = request.POST.get('difficulty', 'medium')
        total_questions = int(request.POST.get('total_questions', 10))

        # Validation
        if not subject or not topic:
            return render(request, 'quiz/create.html', {
                'error': 'Subject and Topic are required fields.',
                'subjects': SUBJECTS,
            })

        # Create quiz record
        quiz = Quiz.objects.create(
            user=request.user,
            topic=f"{subject} - {topic}",
            subject=subject,
            difficulty=difficulty,
            total_questions=total_questions,
            status='generating',
            university=university,
            stream=stream,
            branch=branch,
            year=year,
            pattern=pattern,
            chapter=topic
        )

        # Generate questions with improved AI prompt
        prompt = f"""You are an expert professor for {university} university.
You are creating an exam question paper for:

University: {university}
Stream: {stream}
Branch: {branch}
Year: {year}
Pattern: {pattern}
Subject: {subject}
Topic/Chapter: {topic}
Difficulty: {difficulty}

Generate exactly {total_questions} multiple choice questions strictly about 
the subject "{subject}" and specifically the topic "{topic}" as taught in 
{university} {branch} {year} syllabus.

STRICT RULES:
- Questions must be ONLY from the subject "{subject}"
- Questions must be specifically about "{topic}" chapter/unit
- Questions must match {university} {pattern} exam style
- Questions must be appropriate for {year} {branch} students
- Do NOT give general knowledge questions
- Do NOT mix topics from other subjects
- Questions should match actual university exam pattern

Return ONLY a JSON array in this exact format, no other text:
[
  {{
    "question": "Question text here?",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct": "A",
    "explanation": "Brief explanation of why this is correct in 1-2 sentences."
  }}
]

Return exactly {total_questions} questions.
Return ONLY the JSON array, no markdown, no extra text."""

        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'openai/gpt-4o-mini',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 3000,
                },
                timeout=30
            )

            data = response.json()
            content = data['choices'][0]['message']['content'].strip()

            # Clean JSON
            content = content.replace('```json', '').replace('```', '').strip()
            if content.startswith('['):
                questions_data = json.loads(content)
            else:
                start = content.find('[')
                end = content.rfind(']') + 1
                questions_data = json.loads(content[start:end])

            # Save questions
            for i, q in enumerate(questions_data[:total_questions], 1):
                QuizQuestion.objects.create(
                    quiz=quiz,
                    question_number=i,
                    question_text=q.get('question', ''),
                    option_a=q.get('option_a', ''),
                    option_b=q.get('option_b', ''),
                    option_c=q.get('option_c', ''),
                    option_d=q.get('option_d', ''),
                    correct_option=q.get('correct', 'A').upper(),
                    explanation=q.get('explanation', '')
                )

            quiz.status = 'ready'
            quiz.save()

            return redirect('quiz:attempt', quiz_id=quiz.id)

        except Exception as e:
            quiz.status = 'failed'
            quiz.save()
            return render(request, 'quiz/create.html', {
                'error': f'Failed to generate quiz: {str(e)}',
                'subjects': SUBJECTS,
            })

    return render(request, 'quiz/create.html', {'subjects': SUBJECTS})

@login_required
def quiz_attempt(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)

    if quiz.status == 'failed':
        return redirect('quiz:home')

    if quiz.status == 'completed':
        return redirect('quiz:results', quiz_id=quiz_id)

    if quiz.status == 'generating':
        return render(request, 'quiz/attempt.html', {
            'quiz': quiz,
            'generating': True
        })

    # Get current question
    current_q_num = quiz.current_question + 1
    try:
        question = QuizQuestion.objects.get(
            quiz=quiz,
            question_number=current_q_num
        )
    except QuizQuestion.DoesNotExist:
        return redirect('quiz:results', quiz_id=quiz_id)

    # Timer per question based on difficulty
    timer_seconds = {
        'easy': 30,
        'medium': 45,
        'hard': 60,
    }.get(quiz.difficulty, 45)

    context = {
        'quiz': quiz,
        'question': question,
        'question_number': current_q_num,
        'total_questions': quiz.total_questions,
        'progress_percent': int(((current_q_num - 1) / quiz.total_questions) * 100),
        'timer_seconds': timer_seconds,
        'generating': False,
    }
    return render(request, 'quiz/attempt.html', context)

@login_required
def submit_answer(request, quiz_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    data = json.loads(request.body)

    question_number = data.get('question_number')
    selected_option = data.get('selected_option', '').upper()
    time_spent = data.get('time_spent', 0)

    try:
        question = QuizQuestion.objects.get(
            quiz=quiz,
            question_number=question_number
        )
    except QuizQuestion.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)

    # Save answer
    question.selected_option = selected_option
    question.is_correct = (selected_option == question.correct_option)
    question.time_spent = time_spent
    question.save()

    # Update quiz
    if question.is_correct:
        quiz.score += 1

    quiz.current_question = question_number
    quiz.time_taken += time_spent

    # Check if last question
    is_last = question_number >= quiz.total_questions

    if is_last:
        quiz.status = 'completed'
        quiz.completed_at = timezone.now()

    quiz.save()

    return JsonResponse({
        'is_correct': question.is_correct,
        'correct_option': question.correct_option,
        'explanation': question.explanation,
        'is_last': is_last,
        'score': quiz.score,
    })

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    questions = quiz.questions.all().order_by('question_number')

    percentage = quiz.get_percentage()

    # Verdict
    if percentage >= 80:
        verdict = 'Excellent! 🏆'
        verdict_color = '#16a34a'
        verdict_bg = '#dcfce7'
        verdict_message = 'Outstanding performance! You have mastered this topic.'
    elif percentage >= 60:
        verdict = 'Good Job! 👍'
        verdict_color = '#0369a1'
        verdict_bg = '#e0f2fe'
        verdict_message = 'Good understanding! Review the incorrect answers to improve.'
    elif percentage >= 40:
        verdict = 'Keep Practicing! 📈'
        verdict_color = '#d97706'
        verdict_bg = '#fef9c3'
        verdict_message = 'You are getting there! Focus on the explanations below.'
    else:
        verdict = 'Need More Study! 💪'
        verdict_color = '#dc2626'
        verdict_bg = '#fff1f2'
        verdict_message = 'Do not give up! Read the explanations and try again.'

    # Time formatting
    mins = quiz.time_taken // 60
    secs = quiz.time_taken % 60
    time_display = f"{mins}m {secs}s"

    correct_count = questions.filter(is_correct=True).count()
    wrong_count = questions.filter(is_correct=False).count()
    skipped_count = questions.filter(selected_option='').count()

    context = {
        'quiz': quiz,
        'questions': questions,
        'percentage': percentage,
        'verdict': verdict,
        'verdict_color': verdict_color,
        'verdict_bg': verdict_bg,
        'verdict_message': verdict_message,
        'time_display': time_display,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'skipped_count': skipped_count,
    }
    return render(request, 'quiz/results.html', context)
