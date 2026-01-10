from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from books.models import Book
from circulation.models import BorrowRecord
import json

@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
    
    data = json.loads(request.body)
    user_message = data.get('message', '').lower()
    user = request.user
    
    response_text = "I'm sorry, I didn't quite catch that. You can ask me about book availability, your due dates, or for recommendations!"

    # 1. Availability Check (e.g., "is Harry Potter available?")
    if "available" in user_message or "check" in user_message:
        # Extract potential title (this is a simple parser)
        # In a real app, use NLP or better extraction.
        # For now, let's just search for any word in the message that matches a book title.
        books = Book.objects.all()
        found_books = []
        for book in books:
            if book.title.lower() in user_message:
                status = "Available" if book.available_copies > 0 else f"Out of stock (Next expected: {book.borrow_duration} days max)"
                found_books.append(f"{book.title}: {status}")
        
        if found_books:
            response_text = "Here is what I found:\n" + "\n".join(found_books)
        else:
            response_text = "Which book would you like me to check the availability for?"

    # 2. Due Date Check (e.g., "when is my book due?")
    elif "due" in user_message or "my book" in user_message:
        if not user.is_authenticated:
            response_text = "Please log in to check your due dates."
        else:
            active_borrows = BorrowRecord.objects.filter(user=user, status='ISSUED')
            if active_borrows.exists():
                items = [f"'{b.book.title}' is due on {b.due_date.strftime('%B %d, %Y')}" for b in active_borrows]
                response_text = "Your active loans:\n" + "\n".join(items)
            else:
                response_text = "You don't have any active loans at the moment."

    # 3. Recommendations
    elif "recommend" in user_message or "suggestion" in user_message:
        # Recommend top 3 popular books
        popular = Book.objects.all()[:3]
        items = [f"'{b.title}' by {b.author.name}" for b in popular]
        response_text = "I recommend checking out these popular titles:\n" + "\n".join(items)

    # 4. Help / FAQ
    elif "help" in user_message or "hi" in user_message or "hello" in user_message:
        response_text = "Hello! I am your Library Assistant. You can ask me:\n- 'Is [Title] available?'\n- 'When is my book due?'\n- 'Can you recommend a book?'"

    return JsonResponse({'response': response_text})
