import os

from flask_mail import Message
from app import mail

from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet


def create_estimate_pdf(service_request):
    """
    Creates a PDF estimate and returns the file path.
    """

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    pdf_folder = os.path.join(
        project_root,
        "generated_pdfs"
    )

    os.makedirs(pdf_folder, exist_ok=True)

    filename = f"estimate_{service_request.id}.pdf"

    filepath = os.path.join(
        pdf_folder,
        filename
    )

    doc = SimpleDocTemplate(filepath)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph("<b>THE GO TO PLUMBER</b>", styles["Title"])
    )

    story.append(Spacer(1, 0.25 * inch))

    story.append(
        Paragraph(
            f"<b>Estimate #{service_request.id}</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            f"Customer: {service_request.name}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Phone: {service_request.phone}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Address: {service_request.address}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Service: {service_request.service_type}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.25 * inch))

    estimate = service_request.estimate

    if estimate:

        story.append(
            Paragraph(
                f"Labor: ${estimate.labor_cost:.2f}",
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                f"Parts: ${estimate.parts_cost:.2f}",
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                f"Tax: ${estimate.tax_amount:.2f}",
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Total: ${estimate.total:.2f}</b>",
                styles["Heading2"]
            )
        )

        story.append(Spacer(1, 0.2 * inch))

        if estimate.notes:

            story.append(
                Paragraph(
                    "<b>Notes</b>",
                    styles["Heading3"]
                )
            )

            story.append(
                Paragraph(
                    estimate.notes,
                    styles["BodyText"]
                )
            )

    doc.build(story)

    return filepath

def send_estimate_email(service_request):
    """
    Generates the estimate PDF and emails it to the customer.
    """

    pdf_path = create_estimate_pdf(service_request)

    estimate = service_request.estimate

    message = Message(
        subject=f"Estimate #{service_request.id} - The Go To Plumber",
        recipients=[service_request.email]
    )

    message.body = f"""
Hello {service_request.name},

Thank you for choosing The Go To Plumber.

Attached is your estimate for the requested service.

Estimated Total:
${estimate.total:.2f}

Thank you,
The Go To Plumber
"""

    with open(pdf_path, "rb") as pdf:
        message.attach(
            filename=f"Estimate_{service_request.id}.pdf",
            content_type="application/pdf",
            data=pdf.read()
        )

    mail.send(message)