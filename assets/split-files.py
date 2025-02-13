"""
Script for generating formatted PDFs and text files for Avalanche Gear
Prerequisite: pip install reportlab
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        # Header style
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a4d7c'),
            spaceAfter=20
        )
        
        # Label style
        self.label_style = ParagraphStyle(
            'LabelStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold'
        )
        
        # Value style
        self.value_style = ParagraphStyle(
            'ValueStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#000000'),
            leading=14
        )
        
        # Description style
        self.description_style = ParagraphStyle(
            'DescriptionStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#333333')
        )

    def create_order_pdf(self, content, filename):
        """Create a PDF invoice for orders."""
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Add header
        story.append(Paragraph("AVALANCHE GEAR", self.header_style))
        story.append(Paragraph("ORDER INVOICE", self.header_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Parse content into dictionary
        lines = content.strip().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        # Create order info table
        order_info = [
            [Paragraph("Order ID:", self.label_style), 
             Paragraph(data.get('Order ID', ''), self.value_style)],
            [Paragraph("Date:", self.label_style), 
             Paragraph(data.get('Date', ''), self.value_style)],
            [Paragraph("Customer ID:", self.label_style), 
             Paragraph(data.get('Customer ID', ''), self.value_style)]
        ]
        
        t = Table(order_info, colWidths=[1.5*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.white),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))
        
        # Create product info table
        product_info = [
            ['Product Details', 'Price', 'Quantity', 'Total'],
            [data.get('Product Name', ''), 
             data.get('Price', ''),
             data.get('Quantity Ordered', ''),
             data.get('Total Price', '')]
        ]
        
        t = Table(product_info, colWidths=[3*inch, 1.2*inch, 1*inch, 1.2*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a4d7c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t)
        
        doc.build(story)

    def create_shipping_pdf(self, content, filename):
        """Create a PDF shipping receipt."""
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Add header
        story.append(Paragraph("SHIPPING RECEIPT", self.header_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Parse content
        lines = content.strip().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        # Create shipping info table
        shipping_info = [
            ['Tracking Information', ''],
            ['Order ID', data.get('Order ID', '')],
            ['Shipping Date', data.get('Shipping Date', '')],
            ['Carrier', data.get('Carrier', '')],
            ['Tracking Number', data.get('Tracking Number', '')],
            ['Status', data.get('Status', '')],
            ['Location', f"{data.get('Latitude', '')}, {data.get('Longitude', '')}"]
        ]
        
        t = Table(shipping_info, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a4d7c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('SPAN', (0, 0), (1, 0)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f5f5f5')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t)
        
        doc.build(story)

    def create_product_pdf(self, content, filename):
        """Create a PDF product specification."""
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        story = []
        
        # Add header
        story.append(Paragraph("PRODUCT SPECIFICATION", self.header_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Parse content
        lines = content.strip().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        # Product name
        story.append(Paragraph(data.get('Product Name', ''), self.header_style))
        story.append(Spacer(1, 0.1 * inch))
        
        # Create product info table
        product_info = [
            ['Category', data.get('Category', '')],
            ['Price', data.get('Price', '')],
        ]
        
        t = Table(product_info, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))
        
        # Description
        story.append(Paragraph("Description:", self.label_style))
        story.append(Paragraph(data.get('Description', ''), self.description_style))
        
        doc.build(story)

def process_files():
    """Process all files and generate PDFs/text files."""
    pdf_gen = PDFGenerator()
    
    try:
        # Create output directories
        os.makedirs("product_files", exist_ok=True)
        os.makedirs("review_files", exist_ok=True)
        os.makedirs("order_files", exist_ok=True)
        os.makedirs("shipping_files", exist_ok=True)

        # Process Product Catalog
        with open("product-catalog.md", 'r') as f:
            products = f.read().strip().split("\n\n")
            for i, product in enumerate(products, 1):
                filename = os.path.join("product_files", f"product-{i:02d}.pdf")
                pdf_gen.create_product_pdf(product, filename)
        print("Successfully processed Product Catalog")

        # Process Customer Reviews (text files)
        with open("customer-reviews.md", 'r') as f:
            reviews = f.read().strip().split("\n\n")
            for i, review in enumerate(reviews, 1):
                filename = os.path.join("review_files", f"review-{i:02d}.txt")
                with open(filename, "w") as rf:
                    rf.write(review.strip())
        print("Successfully processed Customer Reviews")

        # Process Order History
        with open("order-history.md", 'r') as f:
            orders = f.read().strip().split("\n\n")
            for i, order in enumerate(orders, 1):
                filename = os.path.join("order_files", f"order-{i:02d}.pdf")
                pdf_gen.create_order_pdf(order, filename)
        print("Successfully processed Order History")

        # Process Shipping Logs
        with open("shipping-logs.md", 'r') as f:
            logs = f.read().strip().split("\n\n")
            for i, log in enumerate(logs, 1):
                filename = os.path.join("shipping_files", f"shipping-{i:02d}.pdf")
                pdf_gen.create_shipping_pdf(log, filename)
        print("Successfully processed Shipping Logs")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
    except Exception as e:
        print(f"Error processing files: {str(e)}")

if __name__ == "__main__":
    process_files()
