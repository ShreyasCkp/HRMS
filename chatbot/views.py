from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import date
import json, re, random, difflib

from masters.models import Workspace, OfficeEvent, Department
from employee_management.models import Employee
from leave_management.models import LeaveRequest
from payroll_management.models import Payroll
from attendance_management.models import Attendance
from recruitment.models import JobPosting, Candidate
from performance_management.models import PerformanceReview

# ✅ Use OpenAI instead of local heavy models
from openai import OpenAI

client = OpenAI()

# In-memory chat history storage (per user)
CHAT_HISTORY = {}

INTENT_EXAMPLES = {
    "employee_count": ["how many employees are there", "total number of staff", "employee headcount"],
    "leaves_today": ["who is on leave today", "employees on leave", "anyone off today"],
    "payroll_status": ["show me payroll", "salary status", "payroll for this month"],
    "attendance_today": ["who came today", "attendance record", "clock-in status"],
    "job_postings": ["open job positions", "how many jobs are open", "recruitment status"],
    "performance_reviews": ["performance review count", "how many reviews", "employee performance"],
    "department_count": ["how many departments", "department count", "total departments"],
    "department_list": ["list all departments", "show department names", "department list"],
    "add_employee": ["add employee", "register new employee", "create staff"],
    "delete_employee": ["delete employee", "remove staff", "terminate employee"],
    "switch_model": ["switch model", "use another model", "change assistant"],
}

SMALL_TALK = {
    "what is your name": "My name is Sara, your virtual assistant.",
    "who invited you": "I was invited by Sai to help everyone here.",
    "where are you from": "I'm from CKP, but I live in the cloud to help you!",
    "hello": "Hello there! How can I assist you today?",
    "hi": "Hi! What would you like to know?",
    "hlo": "Hi! What would you like to know?",
    "hey": "Hey there! How can I help?",
    "thanks": "You're welcome!",
    "thank you": "Anytime!",
    "cool": "Cool indeed 😎",
    "super": "Glad you think so!",
    "why": "Because I'm built to help you!",
    "how are you": "I'm just code, but I'm happy to help!",
    "bye": "ok, bye! Have a great day!",
    "good bye": "Goodbye! Have a great future!",
    "see you": "See you later!",
    "ok bye": "Take care! Feel free to ask if you need anything else.",
}

SELF_META_QUESTIONS = {
    "who are you": "I'm Sara, your virtual HR assistant. I can help with HR, attendance, recruitment, events, and more!",
    "what is your name": "My name is Sara, your virtual assistant.",
    "will you be my assistant": "Absolutely! I'm here to assist you with HR and work-related queries.",
    "whose assistant are you": "I'm here for the entire team — HR, employees, and managers alike.",
    "why are you here": "I'm here to simplify HR tasks and answer your work-related questions.",
    "how you are helpful": "I can assist with employee records, leaves, events, job openings, and more. Just ask!",
    "what do you do": "I help manage HR queries like attendance, leave tracking, workspace info, and department details.",
    "what kind of information you provide": "I provide HR-related info like attendance, leaves, departments, job postings, events, and more.",
}

DEFAULT_UNKNOWN_RESPONSES = [
    "Sorry, I don't have that information. You may check with HR or your manager.",
    "I'm not sure about that. Try contacting your supervisor for more details.",
    "I'm here to help with HR-related queries. You might want to reach out to the appropriate department.",
    "That information isn't available to me. Please ask your manager or the relevant team.",
]

SENSITIVE_TOPICS = {
    "employee names": "I'm sorry, I can't share employee names. Please ask your manager if you need that information.",
    "revenue": "I don't have access to company revenue data. Please check with finance or leadership.",
    "profit": "I don't have access to company profit details. Please consult management.",
    "salary of ceo": "Sorry, I can't disclose individual salary details.",
    "employee salary": "Salary-related information is confidential and cannot be disclosed.",
    "individual salary": "Salary-related information is confidential and cannot be disclosed.",
    "salaries": "I'm sorry, I can't provide salary details.",
    "pay of employee": "I'm sorry, I can't provide that. Please contact HR.",
    "hr policies": "For HR policies, please refer to the official handbook or contact HR directly.",
}

# Abuse filter
ABUSIVE_WORDS = ['idiot', 'fuck', 'stupid', 'fool', 'nonsense', 'shut up', 'dumb', 'mad', 'hate', 'kill', 'bloody']


def contains_abuse(message):
    return any(word in message.lower() for word in ABUSIVE_WORDS)


# ✅ New: lightweight intent detection (no sentence-transformers)
def detect_intent(user_input: str):
    user_input = user_input.lower()
    best_intent = None
    highest_score = 0.0

    for intent, examples in INTENT_EXAMPLES.items():
        for example in examples:
            # Simple similarity + substring check
            example_lower = example.lower()
            if example_lower in user_input:
                return intent
            score = difflib.SequenceMatcher(None, user_input, example_lower).ratio()
            if score > highest_score:
                highest_score = score
                best_intent = intent

    return best_intent if highest_score > 0.6 else None


# ✅ New: use OpenAI for fallback conversational answer
def generate_personality_response(user_message: str, user_id: str) -> str:
    system_prompt = (
        "You are Sara, a witty but professional virtual HR assistant for an HRMS web app. "
        "You help with HR, attendance, leave, recruitment, events, and departments. "
        "Answer clearly, politely, and concisely in 1–3 sentences. "
        "Avoid unrelated topics and do not discuss salaries, confidential company data, or personal secrets."
    )

    history = CHAT_HISTORY.get(user_id, [])

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": user_message}
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # or any model you have access to
            messages=messages,
            max_tokens=150,
            temperature=0.6,
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        answer = random.choice(DEFAULT_UNKNOWN_RESPONSES)

    # Update history (keep it short to save tokens)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": answer})
    CHAT_HISTORY[user_id] = history[-10:]  # last 10 turns max

    return answer


@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        user_message_lower = user_message.lower()
        answer = None

        # 🚫 Abusive check
        if contains_abuse(user_message):
            return JsonResponse({'answer': "Please maintain respectful language. I'm here to help, not be abused."})

        # 🔒 Sensitive regex check
        sensitive_patterns = [
            r'\bsalary\b.*\b(employee|john|ceo|anyone)\b',
            r'\bpay\b.*\bof\b',
            r'\bsalary\b.*\btell\b',
            r'\bsalaries\b',
            r'\brevenue\b',
            r'\bprofit\b',
            r'\bcontact\b.*\bdetails\b',
            r'\bemail\b.*\bemployee\b',
        ]
        for pattern in sensitive_patterns:
            if re.search(pattern, user_message_lower):
                return JsonResponse({'answer': "Sorry, that information is confidential and cannot be shared."})

        # 1. Small Talk
        for phrase, reply in SMALL_TALK.items():
            if phrase in user_message_lower:
                answer = reply
                break

        # 1.5 Self-related Qs
        if not answer:
            for phrase, reply in SELF_META_QUESTIONS.items():
                if phrase in user_message_lower:
                    answer = reply
                    break

        # 1.6 Questions about the bot's own "salary" or persona
        if not answer:
            if any(kw in user_message_lower for kw in ["your salary", "what is your salary", "how much are you paid"]):
                answer = "I'm just a virtual assistant. I don't earn a salary 🙂"

        # 2. Hardcoded sensitive topics
        if not answer:
            for keyword, response in SENSITIVE_TOPICS.items():
                if keyword in user_message_lower:
                    answer = response
                    break

        # 3. Workspace queries
        if not answer and any(word in user_message_lower for word in ['workspace', 'room', 'cabin']):
            workspaces = Workspace.objects.all()
            available = workspaces.filter(is_available=True)
            if 'available' in user_message_lower or 'free' in user_message_lower:
                answer = (
                    f"Available workspaces: "
                    f"{', '.join([f'{w.name} ({w.get_workspace_type_display()})' for w in available]) or 'None'}"
                )
            else:
                answer = (
                    f"All workspaces: "
                    f"{', '.join([f'{w.name} ({w.get_workspace_type_display()})' for w in workspaces])}"
                )

        # 4. Event Queries
        if not answer and any(word in user_message_lower for word in ['event', 'function', 'happening']):
            today = date.today()
            events = OfficeEvent.objects.filter(date__gte=today).order_by('date')
            answer = (
                'Upcoming events: ' + ', '.join([f"{e.title} on {e.date} at {e.location}" for e in events])
                if events.exists()
                else 'No upcoming events.'
            )

        # 5. Intent Detection & Handling
        if not answer:
            intent = detect_intent(user_message_lower)

            if intent == "employee_count":
                answer = (
                    f"Total employees: {Employee.objects.count()}. "
                    f"Active: {Employee.objects.filter(is_active=True).count()}."
                )
            elif intent == "leaves_today":
                on_leave = LeaveRequest.objects.filter(
                    status='Approved',
                    start_date__lte=date.today(),
                    end_date__gte=date.today()
                ).count()
                answer = f"Employees on leave today: {on_leave}."
            elif intent == "payroll_status":
                answer = "Payroll information is confidential. Please contact HR for assistance."
            elif intent == "attendance_today":
                present = Attendance.objects.filter(
                    date=date.today(),
                    clock_in__isnull=False
                ).count()
                answer = f"Present today: {present} employees."
            elif intent == "job_postings":
                count = JobPosting.objects.filter(is_active=True).count()
                answer = f"There are {count} open job postings."
            elif intent == "performance_reviews":
                count = PerformanceReview.objects.count()
                answer = f"Total performance reviews: {count}."
            elif intent == "department_count":
                count = Department.objects.count()
                answer = f"There are {count} departments."
            elif intent == "department_list":
                names = list(Department.objects.values_list("name", flat=True))
                answer = "Departments: " + ", ".join(names) if names else "No departments defined."
            elif intent == "add_employee":
                # Extract employee name from user input
                name_match = re.search(r"(?:named\s+)?([a-zA-Z\s]+)", user_message)
                if name_match:
                    name = name_match.group(1).strip().title()
                    emp = Employee.objects.create(name=name, is_active=True)
                    answer = f"Employee '{emp.name}' added successfully with ID {emp.id}."
                else:
                    answer = "Please provide a valid employee name."
            elif intent == "delete_employee":
                # Extract employee ID
                id_match = re.search(r"employee\s+(\d+)", user_message_lower)
                if id_match:
                    emp_id = int(id_match.group(1))
                    try:
                        Employee.objects.get(id=emp_id).delete()
                        answer = f"Employee ID {emp_id} deleted successfully."
                    except Employee.DoesNotExist:
                        answer = f"No employee found with ID {emp_id}."
                else:
                    answer = "Please specify an employee ID."
            elif intent == "switch_model":
                answer = "Model switching is not enabled on this setup. Currently using an OpenAI-based assistant."

        # 5.5 Handle leave type questions manually
        if not answer:
            if any(phrase in user_message_lower for phrase in ["leave types", "types of leave", "what type of leave", "kinds of leave"]):
                answer = "I'm afraid I don't have access to leave type information. Please contact HR for the leave policy."

        # 6. Fallback to OpenAI conversational model
        if not answer:
            answer = generate_personality_response(user_message, user_id)

        return JsonResponse({'answer': answer})

    except Exception as e:
        print("Chatbot error:", e)
        return JsonResponse({'answer': "Sorry, something went wrong while processing your request."})


# Basic department detection logic
def detect_related_department(message):
    # Simple rules — you can use ML later
    keywords_to_dept = {
        "salary": "HR",
        "payroll": "Payroll",
        "leave": "HR",
        "job": "Recruitment",
        "vacancy": "Recruitment",
        "interview": "Recruitment",
        "performance": "Management",
        "promotion": "Management",
        "policy": "HR",
        "attendance": "HR",
    }

    for keyword, dept in keywords_to_dept.items():
        if keyword in message:
            return dept
    return "HR"  # default fallback


def log_escalated_question(question, user_id, department):
    # You can replace this with actual model logging / DB table
    try:
        from support.models import EscalatedQuery  # optional model

        EscalatedQuery.objects.create(
            question=question,
            user_identifier=user_id,
            department=department,
            status="Pending"
        )
        print(f"[Escalation] Question from user {user_id} sent to {department} department.")
    except ImportError:
        print("Escalation model not found; skipping logging.")


from django.core.mail import send_mail


def notify_department_email(question, department):
    emails = {
        "HR": "hr@ckpsoftware.com",
        "Payroll": "payroll@company.com",
        "Recruitment": "recruitment@company.com",
        "Management": "management@company.com",
    }
    recipient = emails.get(department, "admin@company.com")

    send_mail(
        subject=f"New Escalated Query to {department}",
        message=f"The following user query needs attention:\n\n{question}",
        from_email="noreply@smarthr.com",
        recipient_list=[recipient],
        fail_silently=True,
    )
