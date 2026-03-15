from django.core.management.base import BaseCommand
from accounts.models import CareerPath

class Command(BaseCommand):
    help = 'Populate CareerPath database with sample data'

    def handle(self, *args, **options):
        # Clear existing data
        CareerPath.objects.all().delete()
        
        career_data = [
            {
                'title': 'Software Engineer',
                'stream': 'Computer Science',
                'description': 'Design, develop, and maintain software applications and systems',
                'average_salary': '$80,000 - $150,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Computer Science or related field',
                'key_skills': 'Programming, Problem Solving, Algorithms, Data Structures, Software Development',
                'job_outlook': 'Excellent demand across all industries with strong growth prospects'
            },
            {
                'title': 'Data Scientist',
                'stream': 'Computer Science',
                'description': 'Analyze complex data to help companies make better business decisions',
                'average_salary': '$90,000 - $170,000',
                'growth_rate': 'Very High',
                'education_required': 'Bachelor\'s or Master\'s in Data Science, Statistics, or Computer Science',
                'key_skills': 'Statistics, Machine Learning, Python, R, Data Visualization, SQL',
                'job_outlook': 'Explosive growth with high demand across tech and business sectors'
            },
            {
                'title': 'Mechanical Engineer',
                'stream': 'Engineering',
                'description': 'Design and develop mechanical systems and devices',
                'average_salary': '$70,000 - $120,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Mechanical Engineering',
                'key_skills': 'CAD, Problem Solving, Mathematics, Physics, Manufacturing Processes',
                'job_outlook': 'Steady demand in manufacturing, automotive, and aerospace industries'
            },
            {
                'title': 'Civil Engineer',
                'stream': 'Engineering',
                'description': 'Design and supervise construction of infrastructure projects',
                'average_salary': '$75,000 - $130,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Civil Engineering',
                'key_skills': 'AutoCAD, Project Management, Structural Analysis, Mathematics, Construction',
                'job_outlook': 'Consistent demand for infrastructure development and maintenance'
            },
            {
                'title': 'Business Analyst',
                'stream': 'Business',
                'description': 'Analyze business processes and recommend improvements',
                'average_salary': '$65,000 - $110,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Business Administration or related field',
                'key_skills': 'Data Analysis, Communication, Problem Solving, Business Process, SQL',
                'job_outlook': 'Strong demand as companies focus on process optimization'
            },
            {
                'title': 'Marketing Manager',
                'stream': 'Business',
                'description': 'Develop and implement marketing strategies to promote products and services',
                'average_salary': '$70,000 - $130,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Marketing or Business Administration',
                'key_skills': 'Marketing Strategy, Communication, Analytics, Digital Marketing, Leadership',
                'job_outlook': 'Strong demand in digital marketing and brand management'
            },
            {
                'title': 'Doctor',
                'stream': 'Medicine',
                'description': 'Diagnose and treat illnesses and injuries',
                'average_salary': '$150,000 - $300,000',
                'growth_rate': 'High',
                'education_required': 'Medical Degree (MD) + Residency',
                'key_skills': 'Medical Knowledge, Diagnosis, Patient Care, Communication, Critical Thinking',
                'job_outlook': 'Consistently high demand with excellent job security'
            },
            {
                'title': 'Nurse',
                'stream': 'Medicine',
                'description': 'Provide patient care and support medical treatments',
                'average_salary': '$60,000 - $90,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Nursing or Associate Degree in Nursing',
                'key_skills': 'Patient Care, Medical Knowledge, Communication, Empathy, Critical Thinking',
                'job_outlook': 'Very high demand with excellent job prospects'
            },
            {
                'title': 'Graphic Designer',
                'stream': 'Arts',
                'description': 'Create visual concepts using computer software or by hand',
                'average_salary': '$45,000 - $80,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Graphic Design or related field',
                'key_skills': 'Adobe Creative Suite, Creativity, Typography, Color Theory, Communication',
                'job_outlook': 'Good demand in digital media and marketing sectors'
            },
            {
                'title': 'UX Designer',
                'stream': 'Arts',
                'description': 'Design user interfaces and experiences for digital products',
                'average_salary': '$70,000 - $120,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Design or related field',
                'key_skills': 'User Research, Wireframing, Prototyping, Figma, User Psychology',
                'job_outlook': 'High demand in tech industry with strong growth prospects'
            },
        ]
        
        created_count = 0
        for career in career_data:
            CareerPath.objects.create(**career)
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} career paths!')
        )
