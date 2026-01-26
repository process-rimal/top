# sales/utils.py - PDF Receipt & Utility Functions

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from django.conf import settings
import barcode
from barcode.writer import ImageWriter

def generate_receipt_pdf(sale):
    """Generate PDF receipt for a sale"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(3.5*inch, 8*inch), topMargin=0.2*inch, bottomMargin=0.2*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Shop Header
    shop_name = Paragraph('<b>SHOP NAME</b>', ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=14))
    shop_address = Paragraph('Kathmandu, Nepal', ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=8))
    shop_phone = Paragraph('Ph: +977-1-XXXXXXX', ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=8))
    
    elements.append(shop_name)
    elements.append(shop_address)
    elements.append(shop_phone)
    elements.append(Spacer(1, 0.1*inch))
    
    # Sale Info
    sale_info = f"Receipt No: {sale.sale_number}\\nDate: {sale.sale_date.strftime('%Y-%m-%d %H:%M')}"
    if sale.customer:
        sale_info += f"\\nCustomer: {sale.customer.customer_name}"
    
    elements.append(Paragraph(sale_info, ParagraphStyle(name='left', alignment=TA_LEFT, fontSize=8)))
    elements.append(Spacer(1, 0.1*inch))
    
    # Items Table
    data = [['Item', 'Qty', 'Rate', 'Amount']]
    
    for item in sale.items.all():
        data.append([
            item.product.product_name[:15],
            str(item.quantity),
            f"{item.unit_price:.2f}",
            f"{item.line_total:.2f}"
        ])
    
    # Totals
    data.append(['', '', 'Subtotal:', f"{sale.subtotal:.2f}"])
    if sale.discount > 0:
        data.append(['', '', 'Discount:', f"-{sale.discount:.2f}"])
    if sale.tax > 0:
        data.append(['', '', 'VAT (13%):', f"{sale.tax:.2f}"])
    data.append(['', '', 'TOTAL:', f"{sale.total_amount:.2f}"])
    
    table = Table(data, colWidths=[1.3*inch, 0.5*inch, 0.6*inch, 0.6*inch])
    table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Payment Method
    payment_info = f"Payment: {sale.get_payment_method_display()}"
    if sale.payment_status != 'paid':
        payment_info += f"\\nDue: {sale.due_amount():.2f}"
    
    elements.append(Paragraph(payment_info, ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=8)))
    elements.append(Spacer(1, 0.1*inch))
    
    # Footer
    footer = "Thank You!\\nVisit Again"
    elements.append(Paragraph(footer, ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=8)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_barcode_image(sku):
    """Generate barcode image for product SKU"""
    try:
        barcode_format = barcode.get_barcode_class('code128')
        barcode_obj = barcode_format(str(sku), writer=ImageWriter())
        
        buffer = BytesIO()
        barcode_obj.write(buffer)
        buffer.seek(0)
        return buffer
    except:
        return None

def calculate_sale_totals(items_data):
    """Calculate subtotal, discount, tax, and total"""
    subtotal = sum([item['unit_price'] * item['quantity'] for item in items_data])
    discount = subtotal * (items_data[0].get('discount_percent', 0) / 100) if items_data else 0
    amount_after_discount = subtotal - discount
    tax = amount_after_discount * (settings.VAT_PERCENT / 100)
    total = amount_after_discount + tax
    
    return {
        'subtotal': subtotal,
        'discount': discount,
        'tax': tax,
        'total': total
    }

def process_credit_sale(customer, amount):
    """Process credit sale and update customer balance"""
    from customers.models import Customer, CreditTransaction
    
    try:
        customer.current_credit += amount
        customer.save()
        
        CreditTransaction.objects.create(
            customer=customer,
            transaction_type='purchase',
            amount=amount,
            balance_after=customer.current_credit,
            description='Sale on credit'
        )
        return True
    except:
        return False

def process_payment(customer, amount):
    """Process payment against customer credit"""
    from customers.models import Customer, CreditTransaction
    
    try:
        customer.current_credit -= amount
        if customer.current_credit < 0:
            customer.current_credit = 0
        customer.save()
        
        CreditTransaction.objects.create(
            customer=customer,
            transaction_type='payment',
            amount=amount,
            balance_after=customer.current_credit,
            description='Payment received'
        )
        return True
    except:
        return False
