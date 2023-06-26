#!/usr/bin/env python3
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.platypus import BaseDocTemplate, Frame, Image, PageTemplate, NextPageTemplate, Table, \
    TableStyle, Paragraph, Spacer, PageBreak

from helper import list2table, calculate_percentage, price_format, resource_path


class PdfGenerator(BaseDocTemplate):
    def __init__(self, api_data, input_data, **kwargs):
        super().__init__(f"{api_data['car_id']}.pdf", page_size=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                         bottomMargin=0.75 * cm,
                         _pageBreakQuick=0, **kwargs)

        self.api_data = api_data
        self.input_data = input_data
        self.img_root_path = 'images'
        print(f"{api_data['car_id']}.pdf")
        self.styles = getSampleStyleSheet()
        pdfmetrics.registerFont(TTFont('calibri', 'Calibri.ttf'))

        # Setting up the frames
        cover_pg_frame = Frame(0, 0, self.width + self.leftMargin * 2, 0,
                               id='cover_pg_frame', showBoundary=0)

        images_pages_frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='images_pages_frame',
                                   showBoundary=0)

        car_details_pg_frame = Frame(x1=self.leftMargin, y1=self.bottomMargin * 3, width=self.width,
                                     height=self.height - (self.topMargin * 2 + 70),
                                     id='later_pages_frame', showBoundary=0)

        later_pages_frame = Frame(x1=self.leftMargin, y1=self.bottomMargin * 3, width=self.width,
                                  height=self.height - self.topMargin + 30,
                                  id='later_pages_frame', showBoundary=0)

        # Creating the page templates
        first_page = PageTemplate(id='FirstPage', frames=[cover_pg_frame],
                                  onPage=self.setBackground, onPageEnd=self.cover_page)

        images_pages = PageTemplate(id='ImagesPages', frames=[images_pages_frame], onPage=self.header_and_footer)

        car_details_pg = PageTemplate(id='car_details_pg', frames=[car_details_pg_frame], onPage=self.header_and_footer,
                                      onPageEnd=self.car_specifications)

        later_pages = PageTemplate(id='LaterPages', frames=[later_pages_frame], onPage=self.header_and_footer)

        self.addPageTemplates([first_page, images_pages, car_details_pg, later_pages])

        # add pdf contents
        story = [NextPageTemplate(['ImagesPages']), PageBreak(), self.images_table()]

        story.extend([NextPageTemplate(['car_details_pg']), PageBreak(), self.car_features])

        story.extend([NextPageTemplate("LaterPages"), PageBreak()])

        style = ParagraphStyle(name="CustomStyle", fontSize=16, alignment=TA_LEFT)

        story.extend([Spacer(0, 35), Paragraph("Financial Offer:", style), Spacer(0, 25), self.financial_pg()[0],
                      self.financial_pg()[1],
                      Spacer(0, 100),
                      Paragraph("Payment terms:", style),
                      Spacer(0, 6),
                      ])

        for i in range(4):
            story.extend([Paragraph(f"{i + 1}-", style), Spacer(0, 6)])
        story.append(PageBreak())

        export_guide = Paragraph("EXPORT GUIDE", ParagraphStyle(name="CustomStyle", fontSize=22, alignment=TA_CENTER,
                                                                fontName='Helvetica'))

        thank_you = Paragraph("THANK YOU", ParagraphStyle(name="CustomStyle", fontSize=18, alignment=TA_CENTER,
                                                          fontName='Helvetica'))

        story.extend([export_guide, Spacer(0, 80)])
        story.extend(self.export_guide_pg())
        story.extend([Spacer(0, 70), thank_you])

        self.build(story)

    def header(self, canvas, doc):
        # Helvetica, Courier, Times Roman)

        # seller_name = self.input_data.get("seller_name", 'Mr.')

        table_data = [("G&O GmbH Kfz export service", ''),
                      ("", '')]
        table_style = [('GRID', (0, 0), (-1, -1), 1, colors.white),
                       ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                       ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                       ('FONTSIZE', (0, 0), (-1, -1), 12)
                       ]

        header_content = Table(data=table_data, colWidths=380, style=table_style, hAlign="LEFT")
        canvas.saveState()
        w, h = header_content.wrap(doc.width, doc.topMargin)
        header_content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - 50)
        canvas.restoreState()

    def footer(self, canvas, doc):
        logo = resource_path('footer_logo.jpg')
        footer_logo = Image(logo)
        footer_logo._restrictSize(60, 60)

        date = self.input_data.get('date', datetime.today().strftime('%d.%m.%Y'))
        quotation_num = self.input_data.get('quotation_num', 'XX')

        table_data = [(footer_logo, f'Quotation No. {quotation_num}'),
                      ('TEST', f"Date: {date}")]

        table_style = [
            # ('GRID', (0, 0), (-1, -1), 1, colors.gray),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (-1, 0), (-1, -1), 8),  # SECOND COLUMN
            ('SPAN', (0, 0), (0, -1)),  # Merge FIRST COLUMN
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
        ]

        header_content = Table(data=table_data, style=table_style, colWidths=(doc.width / 2 + 155, 100), rowHeights=15)

        canvas.saveState()
        w, h = header_content.wrap(doc.width, doc.bottomMargin)
        header_content.drawOn(canvas, doc.leftMargin, doc.bottomMargin)
        canvas.restoreState()

    def header_and_footer(self, canvas, doc):
        self.header(canvas, doc)
        self.footer(canvas, doc)

    def cover_page(self, canvas, doc):
        PAGE_HEIGHT = canvas._pagesize[1]
        PAGE_WIDTH = canvas._pagesize[0]
        image_width = doc.width

        image_x = (PAGE_WIDTH - image_width) / 2

        canvas.saveState()

        canvas.drawImage(resource_path("cover_pg_logo.jpg"), doc.width / 2 - doc.leftMargin, doc.height - 160, 180, 180,
                         preserveAspectRatio=True)

        canvas.drawImage(resource_path("cover_pg_background.jpg"), image_x, PAGE_HEIGHT / 4, 500, 500,
                         preserveAspectRatio=True)

        table1 = Table([['Vehicle Purchase Quotation'], ['Presented by G&O-KFZ'],
                        ['Berlin, Germany.']],
                       style=TableStyle([
                           ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                           ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                           # ('GRID', (0, 0), (-1, -1), 1, colors.red),
                           ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),

                           ('FONTSIZE', (0, 0), (0, 0), 24),
                           ('VALIGN', (0, 0), (0, 0), 'TOP'),

                           ('FONTSIZE', (0, 1), (0, -1), 10),
                           ('VALIGN', (0, 1), (0, -1), 'TOP'),
                           # ('TEXTCOLOR', (0, 1), (0, -1), colors.red),

                       ]), rowHeights=(37, 15, 15))

        w, h = table1.wrap(doc.width, doc.topMargin)
        table1.drawOn(canvas, x=doc.leftMargin, y=200)

        seller_name = self.input_data.get("seller_name", 'Mr.')
        seller_phone = self.input_data.get('purchaser_phone', 'xxxxxxxxxxx')
        purchaser_name = self.input_data.get('purchaser_name', '(PURCHASER NAME)')
        purchaser_phone = self.input_data.get('purchaser_phone', '(PHONE NO)')
        purchaser_email = self.input_data.get('purchaser_email', '(EMAIL)')

        table_data = [
            ['To:', 'G&O-KFZ'],
            [purchaser_name, 'Uhlandstrasse 82, 10717'],
            [purchaser_phone, 'Berlin, Germany'],
            [purchaser_email, seller_name],
            ['', seller_phone],
            ['', 'www.go-kfz.com'],
        ]

        table_style = TableStyle([
            # ('GRID', (0, 0), (-1, -1), 1, colors.red),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),

        ])

        table = Table(table_data, style=table_style, colWidths=(doc.width / 2 + 80, doc.width / 2), rowHeights=15)
        table.wrap(doc.width, doc.bottomMargin)
        table.drawOn(canvas, x=doc.leftMargin, y=doc.bottomMargin * 2)

        canvas.restoreState()

    def car_specifications(self, canvas, doc):
        table_data = self.api_data['car_specifications']

        table_style = TableStyle([
            # ('GRID', (0, 0), (-1, -1), 0.25, colors.gray),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ])

        table = Table(table_data, style=table_style, colWidths=(140, 100))

        canvas.saveState()
        table.wrap(doc.width, doc.bottomMargin)
        table.drawOn(canvas, x=doc.width / 2 - 98, y=(doc.height / 2) + doc.topMargin * 3 + 20)
        canvas.restoreState()

    @property
    def car_features(self):
        bullet_style = ParagraphStyle(name="CustomStyle", leftIndent=13, leading=12, fontName="Helvetica", fontSize=12,
                                      bulletFontSize=14)
        x = [Paragraph(f'<bullet>&bull;</bullet> {item}', bullet_style) for item in self.api_data['car_features']]
        table_data = list2table(x)

        table_style = TableStyle([
            # ('GRID', (0, 1), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        table_data.insert(0, ["Austattungen", ''])
        features_table = Table(table_data, repeatRows=1,
                               style=table_style)

        return features_table

    def images_table(self):
        table_grid = self.create_images()
        image_table = Table(table_grid, colWidths=self.width / 2,
                            style=TableStyle([
                                # ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),

                                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                            ]))
        return image_table

    def create_images(self):
        table_images = []

        image_list = [f'{self.img_root_path}/{i}' for i in os.listdir(self.img_root_path) if
                      'main' not in i and i.endswith('.jpg')]

        for idx, img in enumerate(image_list):
            im = Image(img)
            im._restrictSize(230, 230)
            im.hAlign = 'CENTER'
            im.vAlign = 'CENTER'
            table_images.append(im)

        return list2table(table_images)

    def financial_pg(self):
        car_net_price = self.api_data.get('car_price', 0)
        shipping_fees = self.input_data.get('shipping_fees', 0)
        customs = self.input_data.get('customs', 0)
        logistics_fees = self.input_data.get('logistics_fees', 0)

        subtotal = sum([float(car_net_price), float(shipping_fees), float(customs), float(logistics_fees)])
        company_fees = calculate_percentage(self.input_data.get('company_fees', 7), subtotal)
        total = subtotal + company_fees

        table_data = [
            ['S.NO.', 'DETAILS', 'TOTAL PRICE €'],
            ['1.', 'Car Net Price', f"€{price_format(car_net_price)}"],
            ['2.', 'Shipping Fees', f'€{price_format(shipping_fees)}'],
            ['3.', 'Customs', f'€{price_format(customs)}'],
            ['4.', 'Clearance and shipping to Cairo', f'€{price_format(logistics_fees)}'],
        ]

        table1_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

            ('BOX', (0, 0), (1, 4), 1, colors.black),
            ('BOX', (2, 0), (-1, 4), 1, colors.black),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),

            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),

            ('ALIGN', (2, 1), (-1, 4), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),

            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('LEFTPADDING', (2, 0), (2, 0), 25),
            ('LEFTPADDING', (0, 0), (0, 0), 9)

        ])
        table1 = Table(table_data, style=table1_style, colWidths=(35, 238, 238), rowHeights=26)

        table2_data = [
            ['', 'Subtotal', f'€{price_format(subtotal)}'],
            ['', f'G&O fees (%{self.input_data.get("company_fees", 7)})', f'€{price_format(company_fees)}'],
            ['', 'Grand Total', f'€{price_format(total)}']
        ]

        table2_style = TableStyle([
            ('GRID', (1, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (1, -1), (-1, -1), colors.lightgrey),

            ('BOX', (1, 0), (-1, -1), 1, colors.black),

            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTSIZE', (0, -1), (-1, -1), 14),

            ('ALIGN', (-1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')

        ])
        table2 = Table(table2_data, style=table2_style, colWidths=(273, 238 / 2, 238 / 2), rowHeights=26)

        return table1, table2

    def export_guide_pg(self):
        line = Table([['']], style=TableStyle([('LINEABOVE', (0, 0), (0, 1), 0.5, colors.lightgrey)]), colWidths=510)

        data = []
        heading = ['Discover your ideal car', 'Confirm availability', 'Sign contract', 'Complete payment',
                   'Shipping & customs clearance']
        heading_style = ParagraphStyle(name="CustomStyle", fontName="Helvetica", fontSize=14, spaceAfter=18,
                                       spaceBefore=12,
                                       bulletFontSize=20)

        heading = [Paragraph(f'<bullet>&bull;</bullet> <b>{item}</b>', heading_style) for item in heading]

        paragraph = [
            """Select your desired car from reputable marketplaces such as <u><a href="https://www.mobile.de/" color="blue">Mobile.de</a></u> or <u><a href="https://www.autoscout24.de/" color="blue">AutoScout24.de</a></u>, and our team of specialists will assist you in the selection process, ensuring that you make an informed decision.""",
            """Our representative will contact the seller on your behalf to confirm the availability and condition of the car. We take every measure to ensure that you receive a car that meets your expectations and requirements.""",
            """We work closely with the Egyptian Embassy in Berlin to prepare an official binding Contract, verified by a German Notar and the Egyptian Embassy. This ensures that the transaction is legally binding, secure, and transparent.""",
            """Once the full payment is made, we will arrange for the car to be picked up by a reputable transporter and shipped to Alexandria, Egypt. We ensure that your car is shipped safely and securely, and we provide regular updates on the shipping status.""",
            """Our team of representatives in Egypt will handle all the necessary customs clearance procedures, ensuring that your car is cleared for import into Egypt. We will then arrange for the delivery of your car to your doorstep in Egypt, providing you with a seamless and hassle-free experience."""]

        paragraph_style = ParagraphStyle(name="CustomStyle", fontName="calibri", fontSize=10, leading=14,
                                         leftIndent=19, alignment=TA_JUSTIFY)

        paragraph = [Paragraph(f'{item}', paragraph_style) for item in paragraph]

        closing = """Thank you for considering our car export services. We are confident that we can meet your requirements and deliver a seamless experience. Should you have any questions or need further clarification, please do not hesitate to contact our dedicated customer support team. We look forward to the opportunity of working with you and ensuring a successful car export.<br/><br/>Sincerely,"""
        closing = Paragraph(closing,
                            ParagraphStyle(name="CustomStyle", fontSize=10, leftIndent=19,
                                           alignment=TA_JUSTIFY))

        for i in range(5):
            data.extend([heading[i], paragraph[i]])

        data.extend([Spacer(0, 15), line, closing])
        data.insert(0, line)
        # data.insert(-1, line)

        return data

    def setBackground(self, canvas, doc):
        color = colors.black
        canvas.setFillColor(color)
        canvas.rect(0, 0, doc.width + doc.leftMargin + doc.rightMargin, doc.height + doc.topMargin + doc.bottomMargin,
                    fill=True, stroke=False)
