from django.core.management.base import BaseCommand
from accounts.models import CareerPath, CareerSkill, CareerJourney

class Command(BaseCommand):
    help = 'Populate career paths and related data'

    def handle(self, *args, **options):
        self.stdout.write('Populating career paths...')
        
        # Computer Science Careers
        cs_careers = [
            {
                'title': 'Software Engineer',
                'stream': 'Computer Science',
                'description': 'Design, develop, and maintain software systems and applications.',
                'average_salary': '₹8,00,000 - ₹25,00,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Computer Science or related field',
                'key_skills': 'Programming, Problem Solving, Algorithms, Data Structures, Software Development, Git, Testing',
                'job_outlook': 'Excellent demand across all industries with strong growth projected for the next decade.',
                'industries': 'Technology, Finance, Healthcare, E-commerce, Gaming, Government'
            },
            {
                'title': 'Data Scientist',
                'stream': 'Computer Science',
                'description': 'Analyze complex data to help organizations make better decisions.',
                'average_salary': '₹10,00,000 - ₹35,00,000',
                'growth_rate': 'Very High',
                'education_required': 'Bachelor\'s in Computer Science, Statistics, or related field (Master\'s preferred)',
                'key_skills': 'Python, R, Machine Learning, Statistics, Data Visualization, SQL, Deep Learning',
                'job_outlook': 'Exceptional growth as companies increasingly rely on data-driven decision making.',
                'industries': 'Technology, Finance, Healthcare, Retail, Consulting, Research'
            },
            {
                'title': 'Cybersecurity Analyst',
                'stream': 'Computer Science',
                'description': 'Protect organizations from digital threats and security breaches.',
                'average_salary': '₹6,00,000 - ₹20,00,000',
                'growth_rate': 'Very High',
                'education_required': 'Bachelor\'s in Computer Science, Information Security, or related field',
                'key_skills': 'Network Security, Ethical Hacking, Risk Assessment, Security Tools, Incident Response',
                'job_outlook': 'Critical demand as cyber threats continue to evolve and increase.',
                'industries': 'Technology, Finance, Government, Healthcare, Defense, Consulting'
            },
            {
                'title': 'Machine Learning Engineer',
                'stream': 'Computer Science',
                'description': 'Build and deploy machine learning models and AI systems.',
                'average_salary': '₹12,00,000 - ₹40,00,000',
                'growth_rate': 'Very High',
                'education_required': 'Bachelor\'s/Master\'s in Computer Science, AI, or related field',
                'key_skills': 'Machine Learning, Deep Learning, Python, TensorFlow, PyTorch, MLOps',
                'job_outlook': 'Explosive growth as AI and ML become central to business operations.',
                'industries': 'Technology, Healthcare, Finance, Automotive, E-commerce, Research'
            },
            {
                'title': 'DevOps Engineer',
                'stream': 'Computer Science',
                'description': 'Bridge development and operations to streamline software deployment.',
                'average_salary': '₹8,00,000 - ₹22,00,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Computer Science or related field',
                'key_skills': 'CI/CD, Docker, Kubernetes, Cloud Services, Automation, Linux',
                'job_outlook': 'Strong demand as companies adopt DevOps practices for faster deployment.',
                'industries': 'Technology, Finance, E-commerce, Healthcare, Consulting'
            },
            {
                'title': 'Full Stack Developer',
                'stream': 'Computer Science',
                'description': 'Develop both front-end and back-end web applications.',
                'average_salary': '₹6,00,000 - ₹18,00,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Computer Science or related field',
                'key_skills': 'JavaScript, React, Node.js, Python, Databases, Web APIs',
                'job_outlook': 'Consistent high demand as web applications continue to dominate.',
                'industries': 'Technology, E-commerce, Finance, Healthcare, Startups'
            }
        ]
        
        # Engineering Careers
        eng_careers = [
            {
                'title': 'Mechanical Engineer',
                'stream': 'Engineering',
                'description': 'Design and develop mechanical systems and devices.',
                'average_salary': '₹4,00,000 - ₹12,00,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Mechanical Engineering',
                'key_skills': 'CAD, Physics, Mathematics, Problem Solving, Project Management, Manufacturing',
                'job_outlook': 'Steady demand in manufacturing, automotive, and aerospace industries.',
                'industries': 'Manufacturing, Automotive, Aerospace, Energy, Robotics, Construction'
            },
            {
                'title': 'Civil Engineer',
                'stream': 'Engineering',
                'description': 'Design and supervise construction of infrastructure projects.',
                'average_salary': '₹3,50,000 - ₹10,00,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Civil Engineering',
                'key_skills': 'AutoCAD, Project Management, Structural Analysis, Surveying, Mathematics',
                'job_outlook': 'Consistent demand due to infrastructure development and maintenance needs.',
                'industries': 'Construction, Government, Transportation, Environmental, Urban Planning'
            },
            {
                'title': 'Electrical Engineer',
                'stream': 'Engineering',
                'description': 'Design and develop electrical systems and equipment.',
                'average_salary': '₹4,50,000 - ₹15,00,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Electrical Engineering',
                'key_skills': 'Circuit Design, Power Systems, Electronics, MATLAB, Project Management',
                'job_outlook': 'Strong demand in renewable energy and electronics sectors.',
                'industries': 'Energy, Electronics, Telecommunications, Automotive, Manufacturing'
            },
            {
                'title': 'Aerospace Engineer',
                'stream': 'Engineering',
                'description': 'Design aircraft, spacecraft, satellites, and missiles.',
                'average_salary': '₹8,00,000 - ₹25,00,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Aerospace Engineering',
                'key_skills': 'Aerodynamics, Propulsion Systems, Materials Science, CAD, Simulation',
                'job_outlook': 'Growing demand in commercial space and defense sectors.',
                'industries': 'Aerospace, Defense, Aviation, Government, Research'
            }
        ]
        
        # Business Careers
        business_careers = [
            {
                'title': 'Business Analyst',
                'stream': 'Business',
                'description': 'Analyze business processes and recommend improvements.',
                'average_salary': '₹5,00,000 - ₹15,00,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Business, Finance, or related field',
                'key_skills': 'Data Analysis, Communication, Problem Solving, Excel, SQL, Business Intelligence',
                'job_outlook': 'Strong growth as companies seek to optimize operations and make data-driven decisions.',
                'industries': 'Finance, Consulting, Technology, Healthcare, Retail, Government'
            },
            {
                'title': 'Marketing Manager',
                'stream': 'Business',
                'description': 'Develop and execute marketing strategies to promote products and services.',
                'average_salary': '₹6,00,000 - ₹18,00,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Marketing, Business, or related field',
                'key_skills': 'Digital Marketing, Analytics, Communication, Strategy, Social Media, Content Creation',
                'job_outlook': 'Good demand with evolution toward digital and data-driven marketing.',
                'industries': 'Technology, Retail, Entertainment, Healthcare, Finance, Consulting'
            },
            {
                'title': 'Financial Analyst',
                'stream': 'Business',
                'description': 'Analyze financial data and provide investment recommendations.',
                'average_salary': '₹6,00,000 - ₹16,00,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s in Finance, Economics, or related field',
                'key_skills': 'Financial Modeling, Excel, Data Analysis, Risk Assessment, Investment Knowledge',
                'job_outlook': 'Steady demand in banking, investment, and corporate finance sectors.',
                'industries': 'Banking, Investment, Insurance, Corporate Finance, Consulting'
            },
            {
                'title': 'Product Manager',
                'stream': 'Business',
                'description': 'Oversee product development from concept to launch.',
                'average_salary': '₹8,00,000 - ₹25,00,000',
                'growth_rate': 'High',
                'education_required': 'Bachelor\'s in Business, Engineering, or related field',
                'key_skills': 'Product Strategy, Project Management, User Research, Analytics, Communication',
                'job_outlook': 'High demand as companies focus on product-led growth.',
                'industries': 'Technology, E-commerce, Finance, Healthcare, Startups'
            },
            {
                'title': 'Management Consultant',
                'stream': 'Business',
                'description': 'Advise companies on improving performance and efficiency.',
                'average_salary': '₹8,00,000 - ₹30,00,000',
                'growth_rate': 'Medium',
                'education_required': 'Bachelor\'s/Master\'s in Business, Economics, or related field',
                'key_skills': 'Strategic Thinking, Problem Solving, Data Analysis, Communication, Project Management',
                'job_outlook': 'Consistent demand for business optimization expertise.',
                'industries': 'Consulting, Finance, Technology, Healthcare, Manufacturing'
            }
        ]
        
        all_careers = cs_careers + eng_careers + business_careers
        
        for career_data in all_careers:
            career, created = CareerPath.objects.get_or_create(
                title=career_data['title'],
                stream=career_data['stream'],
                defaults=career_data
            )
            
            if created:
                self.stdout.write(f'Created career: {career.title}')
                self._create_career_skills(career)
                self._create_career_journey(career)
        
        self.stdout.write(self.style.SUCCESS('Career paths populated successfully!'))
    
    def _create_career_skills(self, career):
        """Create skills for each career path"""
        skills_data = {
            'Software Engineer': [
                ('Programming', 'essential', '6-12 months'),
                ('Problem Solving', 'essential', '3-6 months'),
                ('Algorithms', 'essential', '4-8 months'),
                ('Git', 'important', '1-2 months'),
                ('Testing', 'important', '2-4 months'),
            ],
            'Data Scientist': [
                ('Python', 'essential', '4-8 months'),
                ('Machine Learning', 'essential', '6-12 months'),
                ('Statistics', 'essential', '6-12 months'),
                ('SQL', 'important', '2-4 months'),
                ('Data Visualization', 'important', '3-6 months'),
            ],
            'Cybersecurity Analyst': [
                ('Network Security', 'essential', '6-12 months'),
                ('Ethical Hacking', 'essential', '4-8 months'),
                ('Risk Assessment', 'essential', '3-6 months'),
                ('Security Tools', 'important', '2-6 months'),
                ('Incident Response', 'important', '3-6 months'),
            ],
        }
        
        if career.title in skills_data:
            for skill_name, importance, learn_time in skills_data[career.title]:
                CareerSkill.objects.get_or_create(
                    career_path=career,
                    skill_name=skill_name,
                    defaults={
                        'importance': importance,
                        'learn_time': learn_time
                    }
                )
    
    def _create_career_journey(self, career):
        """Create career journey steps"""
        journeys_data = {
            'Software Engineer': [
                (1, 'Education Foundation', 'Complete Bachelor\'s degree in Computer Science', '4 years', 'High school diploma', 'Degree and fundamental programming knowledge'),
                (2, 'Internship Experience', 'Gain practical experience through internships', '3-6 months', 'Programming basics', 'Real-world project experience'),
                (3, 'Junior Developer', 'Start as Junior Developer', '1-2 years', 'Degree + internship', 'Professional development experience'),
                (4, 'Mid-Level Developer', 'Advance to Mid-Level position', '2-3 years', '2+ years experience', 'Technical leadership opportunities'),
                (5, 'Senior Developer', 'Reach Senior level', '3-5 years', '5+ years experience', 'Technical expertise and mentorship'),
                (6, 'Tech Lead/Architect', 'Move into leadership', '5+ years', 'Senior level experience', 'Team leadership and system design'),
            ],
            'Data Scientist': [
                (1, 'Education Foundation', 'Complete Bachelor\'s or Master\'s in relevant field', '4-6 years', 'Strong mathematics background', 'Statistical and programming foundation'),
                (2, 'Technical Skills', 'Master Python, R, and ML frameworks', '6-12 months', 'Degree completed', 'Technical toolkit for data science'),
                (3, 'Junior Data Analyst', 'Start as Data Analyst', '1-2 years', 'Technical skills', 'Business analytics experience'),
                (4, 'Data Scientist', 'Transition to Data Scientist role', '2-3 years', 'Analytics experience', 'ML model development experience'),
                (5, 'Senior Data Scientist', 'Advance to Senior level', '3-5 years', 'Data science experience', 'Advanced ML and leadership'),
                (6, 'Principal/Lead', 'Reach leadership position', '5+ years', 'Senior level expertise', 'Strategic data science direction'),
            ],
            'Machine Learning Engineer': [
                (1, 'Education Foundation', 'Bachelor\'s/Master\'s in Computer Science or AI', '4-6 years', 'Strong math and CS background', 'AI/ML theoretical foundation'),
                (2, 'ML Skills Development', 'Master ML frameworks and algorithms', '6-12 months', 'CS degree completed', 'Practical ML implementation skills'),
                (3, 'Junior ML Engineer', 'Start in ML role', '1-2 years', 'ML skills + portfolio', 'Real-world ML project experience'),
                (4, 'ML Engineer', 'Full ML Engineer role', '2-4 years', 'ML experience', 'End-to-end ML system development'),
                (5, 'Senior ML Engineer', 'Lead ML projects', '3-5 years', 'ML expertise', 'Advanced ML systems and team leadership'),
                (6, 'ML Architect', 'Design ML systems', '5+ years', 'Senior ML experience', 'ML strategy and architecture design'),
            ],
            'DevOps Engineer': [
                (1, 'Education Foundation', 'Bachelor\'s in Computer Science or IT', '4 years', 'CS/IT fundamentals', 'System administration knowledge'),
                (2, 'DevOps Tools', 'Learn CI/CD, Docker, Kubernetes', '6-12 months', 'Basic sysadmin skills', 'DevOps tool proficiency'),
                (3, 'Junior DevOps', 'Start DevOps role', '1-2 years', 'DevOps skills', 'Production deployment experience'),
                (4, 'DevOps Engineer', 'Full DevOps responsibilities', '2-4 years', 'DevOps experience', 'Infrastructure automation expertise'),
                (5, 'Senior DevOps', 'Lead DevOps initiatives', '3-5 years', 'DevOps expertise', 'DevOps strategy and team leadership'),
                (6, 'DevOps Architect', 'Design DevOps systems', '5+ years', 'Senior DevOps experience', 'Enterprise DevOps architecture'),
            ],
            'Full Stack Developer': [
                (1, 'Education Foundation', 'Bachelor\'s in Computer Science', '4 years', 'Programming fundamentals', 'Web development basics'),
                (2, 'Full Stack Skills', 'Master front-end and back-end technologies', '6-12 months', 'Programming basics', 'Complete web development skills'),
                (3, 'Junior Full Stack', 'Start full stack development', '1-2 years', 'Full stack skills', 'End-to-end web application experience'),
                (4, 'Full Stack Developer', 'Independent full stack work', '2-4 years', 'Full stack experience', 'Complex application development'),
                (5, 'Senior Full Stack', 'Lead full stack projects', '3-5 years', 'Full stack expertise', 'Technical leadership and architecture'),
                (6, 'Full Stack Architect', 'Design web systems', '5+ years', 'Senior full stack experience', 'Web application architecture design'),
            ],
            'Mechanical Engineer': [
                (1, 'Education Foundation', 'Bachelor\'s in Mechanical Engineering', '4 years', 'Physics and math background', 'Engineering fundamentals'),
                (2, 'CAD Skills', 'Master CAD software and design tools', '6-12 months', 'Engineering degree', 'Design software proficiency'),
                (3, 'Junior Engineer', 'Start engineering role', '1-2 years', 'CAD skills', 'Practical engineering experience'),
                (4, 'Mechanical Engineer', 'Full engineering responsibilities', '2-4 years', 'Engineering experience', 'Project design and management'),
                (5, 'Senior Engineer', 'Lead engineering projects', '3-5 years', 'Engineering expertise', 'Technical leadership role'),
                (6, 'Engineering Manager', 'Manage engineering teams', '5+ years', 'Senior engineering experience', 'Team and project management'),
            ],
            'Business Analyst': [
                (1, 'Education Foundation', 'Bachelor\'s in Business or related field', '4 years', 'Business fundamentals', 'Business analysis basics'),
                (2, 'Technical Skills', 'Master Excel, SQL, and BI tools', '6-12 months', 'Business degree', 'Data analysis skills'),
                (3, 'Junior Analyst', 'Start business analysis role', '1-2 years', 'Technical skills', 'Business process analysis'),
                (4, 'Business Analyst', 'Full BA responsibilities', '2-4 years', 'BA experience', 'Requirements analysis and solution design'),
                (5, 'Senior Analyst', 'Lead analysis projects', '3-5 years', 'BA expertise', 'Strategic business analysis'),
                (6, 'BA Manager', 'Manage BA team', '5+ years', 'Senior BA experience', 'Team leadership and strategy'),
            ],
            'Product Manager': [
                (1, 'Education Foundation', 'Bachelor\'s in Business or related field', '4 years', 'Business fundamentals', 'Product management basics'),
                (2, 'Product Skills', 'Learn product strategy and tools', '6-12 months', 'Business background', 'Product management skills'),
                (3, 'Associate PM', 'Start product role', '1-2 years', 'Product skills', 'Product development experience'),
                (4, 'Product Manager', 'Full PM responsibilities', '2-4 years', 'PM experience', 'Product strategy and execution'),
                (5, 'Senior PM', 'Lead product initiatives', '3-5 years', 'PM expertise', 'Strategic product leadership'),
                (6, 'Product Director', 'Manage product portfolio', '5+ years', 'Senior PM experience', 'Product strategy and team leadership'),
            ],
        }
        
        if career.title in journeys_data:
            for step_num, title, desc, duration, prereq, outcomes in journeys_data[career.title]:
                CareerJourney.objects.get_or_create(
                    career_path=career,
                    step_number=step_num,
                    defaults={
                        'step_title': title,
                        'step_description': desc,
                        'duration': duration,
                        'prerequisites': prereq,
                        'outcomes': outcomes
                    }
                )
