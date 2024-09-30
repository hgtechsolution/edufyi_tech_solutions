import smtplib
import traceback
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pdfkit

path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)


def send_payment_receipt(receipt_content, email, course_name):
    try:
        # Create receipt content

        # Convert the receipt to a PDF
        receipt_html = f"<html><body>{receipt_content.replace('\n', '<br>')}</body></html>"
        pdf = pdfkit.from_string(receipt_html, False, configuration=config)

        # Email setup
        sender_email = "scarlet@epicculinaryexperiences.com"
        receiver_email = email
        password = "qJ7fHrS!rs"

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"Payment Receipt for {course_name}"

        # Attach the text part
        msg.attach(MIMEText(receipt_content, "plain"))

        # Attach the PDF receipt
        pdf_attachment = MIMEApplication(pdf, _subtype="pdf")
        pdf_attachment.add_header('Content-Disposition', 'attachment',
                                  filename="payment_receipt.pdf")
        msg.attach(pdf_attachment)

        # Sending the email via SMTP
        with smtplib.SMTP('mail.creativedreamlabs.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f"Payment receipt sent to {email}")

    except Exception as e:
        print(f"Failed to send payment receipt: {e}")
        error_ex = traceback.format_exc()
        print(error_ex)


def course_transaction_receipt_format(name, course_name, payment_record):
    receipt_content = f"""
            Dear Customer,

            Thank you for your purchase of {course_name}!
            Name : {name}
            Email: {payment_record['email']}
            Phone Number: {payment_record['contact']}

            Here are the details of your transaction:
            - Payment ID: {payment_record['payment_id']}
            - Bank: {payment_record['bank']}
            - Bank Transaction ID: {payment_record['acquirer_data']['bank_transaction_id']}
            - Amount: {payment_record['amount']} INR
            - Status: {payment_record['status']}
            - Method: {payment_record['method']}

            Regards,
            Your Company Name
            """
    return receipt_content


def registration_transaction_receipt_format(name, payment_record):
    receipt_content = f"""
            Dear Customer,

            Thank you for registration!
            Name : {name}
            Email: {payment_record['email']}
            Phone Number: {payment_record['contact']}

            Here are the details of your transaction:
            - Payment ID: {payment_record['payment_id']}
            - Bank: {payment_record['bank']}
            - Bank Transaction ID: {payment_record['acquirer_data']['bank_transaction_id']}
            - Amount: {payment_record['amount']} INR
            - Status: {payment_record['status']}
            - Method: {payment_record['method']}

            Regards,
            Your Company Name
            """
    return receipt_content
