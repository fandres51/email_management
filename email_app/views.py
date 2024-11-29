from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Email

TRUSTED_COMPANIES = [
    "Company A",
    "Company B",
    "Company C",
    "Company D",
    "Company E"
]

def email_list(request):
    query = request.GET.get('q')
    emails = Email.objects.all()

    if query:
        emails = emails.filter(content__icontains=query)

    paginator = Paginator(emails, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'email_list.html', {
        'emails': page_obj.object_list,
        'page_obj': page_obj,
        'query': query
    })

def delete_email(request, email_id):
    try:
        email = Email.objects.get(id=email_id)
        email.delete()
        return redirect('email_list')
    except Email.DoesNotExist:
        return JsonResponse({'error': 'Email not found.'}, status=404)

def send_error(message, status=400):
    return JsonResponse({'error': message}, status=status)

def validate_trusted_company(company_name):
    if company_name not in TRUSTED_COMPANIES:
        return False, f"Untrusted company: {company_name}. Only emails from trusted companies are allowed."
    return True, None

def process_email_item(item):
    try:
        # Validate required fields
        required_fields = ['recipient', 'sender', 'date', 'company_of_sender', 'content', 'unique_email_code']
        for field in required_fields:
            if field not in item:
                return False, f"Missing required field: {field}"

        # Validate the company
        is_valid, error_message = validate_trusted_company(item['company_of_sender'])
        if not is_valid:
            return False, error_message

        # Create Email object
        email = Email(
            recipient=item['recipient'],
            sender=item['sender'],
            date=item['date'],
            company_of_sender=item['company_of_sender'],
            content=item['content'],
            unique_email_code=item['unique_email_code']
        )

        return True, email

    except Exception as e:
        return False, str(e)

@csrf_exempt
def upload_emails(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))

            if not isinstance(data, list):
                return send_error('Invalid JSON format. Expected a list of objects.')

            emails_to_create = []
            error_messages = []
            
            for item in data:
                success, result = process_email_item(item)

                if not success:
                    # Collect the error messages without stopping the process
                    error_messages.append(result)
                else:
                    # Add valid emails to the list for bulk creation
                    emails_to_create.append(result)

            # Bulk create emails
            if emails_to_create:
                Email.objects.bulk_create(emails_to_create)

            # If there are any errors, return them along with the success message
            if error_messages:
                return JsonResponse({
                    'message': f'{len(emails_to_create)} emails added successfully.',
                    'errors': error_messages
                })

            return JsonResponse({'message': f'{len(emails_to_create)} emails added successfully.'})

        except json.JSONDecodeError:
            return send_error('Invalid JSON data.')

    return send_error('Invalid request. Use POST with raw JSON data.')
