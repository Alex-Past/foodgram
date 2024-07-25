from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse


def pdf_shopping_cart(shopping_cart):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.pdf"'
    )
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont('DejaVuSerif', 14)
    p.drawString(200, 800, 'Список покупок.')
    p.setFont('DejaVuSerif', 14)
    from_bottom = 750
    for number, ingredient in enumerate(shopping_cart, start=1):
        p.drawString(
            50,
            from_bottom,
            f'{number}. {ingredient["ingredient__name"]}: '
            f'{ingredient["ingredient_value"]} '
            f'{ingredient["ingredient__measurement_unit"]}.',
        )
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            p.showPage()
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
