from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
import requests
import json
from .models import SearchHistory

@login_required
def resource_home(request):
    recent_searches = SearchHistory.objects.filter(
        user=request.user
    ).order_by('-searched_at')[:5]
    
    context = {
        'recent_searches': recent_searches,
        'universities': [
            'SPPU (Savitribai Phule Pune University)',
            'Mumbai University',
            'VTU (Visvesvaraya Technological University)',
            'RGPV',
            'GTU (Gujarat Technological University)',
            'Anna University',
            'Other'
        ],
        'streams': [
            'Engineering',
            'Commerce',
            'Science',
            'Arts',
            'Management (MBA)',
            'Pharmacy',
            'Architecture'
        ],
        'branches': [
            'Computer Engineering',
            'Information Technology',
            'Electronics & Telecommunication',
            'Mechanical Engineering',
            'Civil Engineering',
            'Electrical Engineering',
            'AIDS (AI & Data Science)',
            'AIML',
            'Chemical Engineering',
            'Other'
        ],
        'resource_types': [
            'Notes PDF',
            'Question Papers',
            'Video Lectures',
            'Reference Books',
            'Syllabus',
            'Lab Manual',
            'Assignment Solutions'
        ]
    }
    return render(request, 'resources/home.html', context)

@login_required
def search_resources(request):
    if request.method == 'POST':
        university = request.POST.get('university', '')
        stream = request.POST.get('stream', '')
        branch = request.POST.get('branch', '')
        semester = request.POST.get('semester', '')
        subject = request.POST.get('subject', '')
        resource_type = request.POST.get('resource_type', '')
        pattern = request.POST.get('pattern', '')

        # Save to search history
        SearchHistory.objects.create(
            user=request.user,
            university=university,
            stream=stream,
            branch=branch,
            semester=semester,
            subject=subject,
            resource_type=resource_type
        )

        # University patterns mapping
        university_patterns = {
            'SPPU (Savitribai Phule Pune University)': {
                'short': 'SPPU',
                'pattern': 'SPPU syllabus pattern',
            },
            'Mumbai University': {
                'short': 'Mumbai University',
                'pattern': 'Mumbai University syllabus',
            },
            'VTU (Visvesvaraya Technological University)': {
                'short': 'VTU',
                'pattern': 'VTU syllabus CBCS',
            },
            'GTU (Gujarat Technological University)': {
                'short': 'GTU',
                'pattern': 'GTU syllabus',
            },
            'RGPV': {
                'short': 'RGPV',
                'pattern': 'RGPV syllabus',
            },
            'Anna University': {
                'short': 'Anna University',
                'pattern': 'Anna University regulation syllabus',
            },
        }

        uni_info = university_patterns.get(university, {
            'short': university,
            'pattern': '',
        })

        # Build search query
        query_parts = []

        if university and university != 'Other':
            query_parts.append(f'"{uni_info["short"]}"')

        if pattern:
            query_parts.append(f'"{pattern}"')

        if subject:
            query_parts.append(subject)

        if semester:
            query_parts.append(f'semester {semester}')

        branch_short = {
            'Computer Engineering': 'computer engineering',
            'Information Technology': 'IT information technology',
            'Electronics & Telecommunication': 'EXTC electronics',
            'Mechanical Engineering': 'mechanical',
            'Civil Engineering': 'civil',
            'Electrical Engineering': 'electrical',
            'AIDS (AI & Data Science)': 'AI data science',
            'AIML': 'AIML machine learning',
        }.get(branch, branch)

        if branch:
            query_parts.append(branch_short)

        resource_keywords = {
            'Notes PDF': 'notes PDF',
            'Question Papers': 'question paper previous year exam',
            'Video Lectures': 'lecture video tutorial',
            'Reference Books': 'reference book PDF',
            'Syllabus': 'syllabus',
            'Lab Manual': 'lab manual practical',
            'Assignment Solutions': 'assignment solution',
        }

        if resource_type:
            query_parts.append(resource_keywords.get(resource_type, resource_type))

        search_query = ' '.join(query_parts)

        try:
            api_key = settings.SERPAPI_KEY
            params = {
                'api_key': api_key,
                'engine': 'google',
                'q': search_query,
                'num': 10,
            }
            response = requests.get(
                'https://serpapi.com/search',
                params=params,
                timeout=15
            )
            data = response.json()

            results = []

            if 'organic_results' in data:
                for item in data['organic_results']:
                    link = item.get('link', '')
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    display_link = item.get('displayed_link', '')

                    if 'youtube.com' in link or 'youtu.be' in link:
                        source_type = 'Video Lecture'
                        source_icon = '🎥'
                        source_color = 'card-red'
                    elif 'drive.google.com' in link:
                        source_type = 'Google Drive'
                        source_icon = '📁'
                        source_color = 'card-blue'
                    elif 'nptel.ac.in' in link:
                        source_type = 'NPTEL'
                        source_icon = '🎓'
                        source_color = 'card-green'
                    elif 'slideshare.net' in link:
                        source_type = 'SlideShare'
                        source_icon = '📊'
                        source_color = 'card-orange'
                    elif '.pdf' in link.lower() or 'pdf' in title.lower():
                        source_type = 'PDF Document'
                        source_icon = '📄'
                        source_color = 'card-purple'
                    elif 'github.com' in link:
                        source_type = 'GitHub'
                        source_icon = '💻'
                        source_color = 'card-yellow'
                    elif 'geeksforgeeks.org' in link:
                        source_type = 'GeeksForGeeks'
                        source_icon = '💡'
                        source_color = 'card-green'
                    elif 'tutorialspoint.com' in link:
                        source_type = 'Tutorial'
                        source_icon = '📖'
                        source_color = 'card-orange'
                    else:
                        source_type = 'Web Resource'
                        source_icon = '🌐'
                        source_color = 'card-blue'

                    # Relevance scoring
                    score = 0
                    uni_short = uni_info['short'].lower()
                    title_lower = title.lower()
                    snippet_lower = snippet.lower()
                    subject_lower = subject.lower()

                    if uni_short in title_lower or uni_short in snippet_lower:
                        score += 3
                    if subject_lower in title_lower:
                        score += 3
                    if subject_lower in snippet_lower:
                        score += 2
                    if semester and (f'sem {semester}' in title_lower or f'semester {semester}' in title_lower):
                        score += 2

                    trusted_domains = [
                        'nptel.ac.in', 'slideshare.net', 'drive.google.com',
                        'youtube.com', 'github.com', 'geeksforgeeks.org',
                        'tutorialspoint.com', 'scribd.com', 'academia.edu',
                        'studocu.com', 'unipune.ac.in', 'mu.ac.in', 'vtu.ac.in'
                    ]
                    for domain in trusted_domains:
                        if domain in link.lower():
                            score += 1
                            break

                    if score >= 5:
                        relevance_label = '⭐ Highly Relevant'
                        relevance_class = 'relevance-high'
                    elif score >= 3:
                        relevance_label = '✓ Relevant'
                        relevance_class = 'relevance-medium'
                    else:
                        relevance_label = '🌐 General'
                        relevance_class = 'relevance-low'

                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet,
                        'source_type': source_type,
                        'source_icon': source_icon,
                        'source_color': source_color,
                        'display_link': display_link,
                        'relevance_score': score,
                        'relevance_label': relevance_label,
                        'relevance_class': relevance_class,
                    })

                # Sort by relevance
                results.sort(key=lambda x: x['relevance_score'], reverse=True)

            elif 'error' in data:
                error_msg = data['error']
                context = {
                    'error': f'Search Error: {error_msg}',
                    'results': [],
                    'subject': subject,
                    'resource_type': resource_type,
                    'university': university,
                    'branch': branch,
                    'semester': semester,
                    'search_query': search_query,
                    'total_results': 0,
                }
                return render(request, 'resources/results.html', context)

            context = {
                'results': results,
                'search_query': search_query,
                'subject': subject,
                'resource_type': resource_type,
                'university': university,
                'branch': branch,
                'semester': semester,
                'total_results': len(results),
                'error': None,
            }

        except requests.exceptions.Timeout:
            context = {
                'error': 'Search timed out. Please try again.',
                'results': [],
                'subject': subject,
                'resource_type': resource_type,
                'university': university,
                'branch': branch,
                'semester': semester,
                'search_query': search_query,
                'total_results': 0,
            }

        except Exception as e:
            context = {
                'error': f'Something went wrong: {str(e)}',
                'results': [],
                'subject': subject,
                'resource_type': resource_type,
                'university': university,
                'branch': branch,
                'semester': semester,
                'search_query': search_query,
                'total_results': 0,
            }

        return render(request, 'resources/results.html', context)

    return redirect('resources:home')
