from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification, Payment, Invoice
from grooming_session_tracker.utils import send_notification
from groom_interface.models import Appointment
from collections import defaultdict
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit
import os
from userauth.decorators import role_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# Notifications
@login_required
@role_required(['owner','groomer'])
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


# Mark Notification as Read
@login_required
@role_required(['owner','groomer'])
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marked as read')
    return redirect('notifications')  # Redirect back to the notifications page

# Mark All Notifications as Read
@login_required
@role_required(['owner','groomer'])
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read')
    return redirect('notifications')  # Redirect back to the notifications page

@login_required
@role_required(['owner'])
def pet_owner_expenses(request):
    user = request.user
    appointments = Appointment.objects.filter(pet_owner=user, status='completed')

    appointment_details = []

    for appointment in appointments:
        try:
            invoice = Invoice.objects.get(appointment=appointment)
            payments = Payment.objects.filter(invoice=invoice)
            appointment_details.append({
                'appointment': appointment,
                'invoice': invoice,
                'payments': payments,
            })
        except Invoice.DoesNotExist:
            pass

    # ✅ Pagination
    paginator = Paginator(appointment_details, 6)  # Show 6 per page
    page = request.GET.get('page')
    try:
        appointment_details = paginator.page(page)
    except PageNotAnInteger:
        appointment_details = paginator.page(1)
    except EmptyPage:
        appointment_details = paginator.page(paginator.num_pages)

    return render(request, 'pet_owner_expenses.html', {'appointment_details': appointment_details})




@login_required
@role_required(['groomer'])
def groomer_payments(request):
    user = request.user
    appointments = Appointment.objects.filter(groomer=user, status='completed').select_related("service")

    appointment_details = []
    earnings_summary = defaultdict(float)

    for appointment in appointments:
        invoice = Invoice.objects.filter(appointment=appointment).first()
        if invoice:
            payments = Payment.objects.filter(invoice=invoice)
            appointment_details.append({
                'appointment': appointment,
                'invoice': invoice,
                'payments': payments,
            })
            if invoice.status == "paid":
                earnings_summary[appointment.service.name] += float(invoice.total_amount)

    # ✅ Pagination
    paginator = Paginator(appointment_details, 6)  # Show 6 per page
    page = request.GET.get('page')
    try:
        appointment_details = paginator.page(page)
    except PageNotAnInteger:
        appointment_details = paginator.page(1)
    except EmptyPage:
        appointment_details = paginator.page(paginator.num_pages)

    context = {
        "appointment_details": appointment_details,
        "earnings_summary": dict(earnings_summary),
    }
    return render(request, "groomer_payments.html", context)



@login_required
@role_required(['groomer'])
def update_payment_status(request, appointment_id):
    # Fetch the appointment object or return a 404 error if not found
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Ensure the logged-in user is authorized to update payment for this appointment
    if request.user != appointment.groomer:
        messages.error(request, 'You are not authorized to update payment for this appointment.')
        return redirect('groomer_payments')  # Redirect to groomer's payments page
    
    # Handle POST requests (form submission)
    if request.method == 'POST':
        try:
            # Get the invoice related to the appointment
            invoice = Invoice.objects.get(appointment=appointment)
            
            # Check if the invoice is already marked as paid
            if invoice.status == 'paid':
                messages.warning(request, 'This invoice has already been marked as paid.')
                return redirect('groomer_payments')
            
            # Create the payment record
            amount = appointment.service.price  # Price of the service
            Payment.objects.create(
                invoice=invoice,
                amount=amount,
                paid_by=request.user,
            )
            
            # Update the invoice status to 'paid'
            invoice.status = 'paid'
            invoice.save()
            
            # Add a success message
            messages.success(request, 'Payment successfully recorded and invoice marked as paid.')
        except Invoice.DoesNotExist:
            messages.error(request, 'No invoice found for this appointment.')
        
        # Redirect after successful payment update
        return redirect('groomer_payments')
    
    # If the request method is not POST, redirect back to the payments page
    return redirect('groomer_payments')


def generate_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Generate HTML content for PDF
    html_content = render_to_string('invoice_pdf_template.html', {'invoice': invoice})

    # Configure pdfkit with the correct wkhtmltopdf path
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH) if os.name == "nt" else None

    # Generate the PDF
    pdf = pdfkit.from_string(html_content, False, configuration=config)

    # Create HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    return response


def view_invoice_pdf(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    html_content = render_to_string('invoice_pdf_template.html', {'invoice': invoice})

    # Configure PDF generation settings
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
    }

    # Get wkhtmltopdf path from settings or manually define it
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

    # Generate PDF in-memory
    pdf = pdfkit.from_string(html_content, False, options=options, configuration=pdfkit_config)

    # Return response with inline display instead of download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{invoice_id}.pdf"'
    return response


