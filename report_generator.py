import os
from datetime import datetime, timedelta

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)


class ReportGenerator:
    def __init__(self, output_dir='reports'):
        """
        Initialize the report generator
        """
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        
        # Create custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12
        ))
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def generate_medication_report(self, user_data, medications, start_date, end_date):
        """
        Generate a PDF report of medication history
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'medication_report_{timestamp}.pdf'
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Create content
            content = []
            
            # Add title
            content.append(Paragraph(
                f"Medication Report for {user_data['name']}",
                self.styles['CustomTitle']
            ))
            
            # Add date range
            content.append(Paragraph(
                f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}",
                self.styles['Normal']
            ))
            
            content.append(Spacer(1, 20))
            
            # Add current medications
            content.append(Paragraph("Current Medications", self.styles['CustomHeading']))
            
            # Create medication table
            medication_data = [['Medication', 'Dosage', 'Frequency', 'Start Date']]
            for med in medications:
                medication_data.append([
                    med['name'],
                    med['dosage'],
                    med['frequency'],
                    med['start_date'].strftime('%Y-%m-%d')
                ])
            
            medication_table = Table(medication_data)
            medication_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(medication_table)
            content.append(Spacer(1, 20))
            
            # Add medication history
            content.append(Paragraph("Medication History", self.styles['CustomHeading']))
            
            # Create history table
            history_data = [['Date', 'Medication', 'Action', 'Notes']]
            for entry in user_data.get('medication_history', []):
                if start_date <= entry['date'] <= end_date:
                    history_data.append([
                        entry['date'].strftime('%Y-%m-%d'),
                        entry['medication'],
                        entry['action'],
                        entry.get('notes', '')
                    ])
            
            history_table = Table(history_data)
            history_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(history_table)
            
            # Build PDF
            doc.build(content)
            
            return filepath
        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")

    def generate_prescription_report(self, user_data, prescriptions):
        """
        Generate a PDF report of prescriptions
        """
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'prescription_report_{timestamp}.pdf'
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Create content
            content = []
            
            # Add title
            content.append(Paragraph(
                f"Prescription Report for {user_data['name']}",
                self.styles['CustomTitle']
            ))
            
            content.append(Spacer(1, 20))
            
            # Add prescriptions
            content.append(Paragraph("Active Prescriptions", self.styles['CustomHeading']))
            
            # Create prescription table
            prescription_data = [['Doctor', 'Date', 'Medication', 'Status']]
            for prescription in prescriptions:
                prescription_data.append([
                    prescription['doctor_name'],
                    prescription['date_prescribed'].strftime('%Y-%m-%d'),
                    prescription['medication'],
                    prescription['status']
                ])
            
            prescription_table = Table(prescription_data)
            prescription_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(prescription_table)
            
            # Build PDF
            doc.build(content)
            
            return filepath
        except Exception as e:
            raise Exception(f"Error generating prescription report: {str(e)}")

# Example usage:
if __name__ == "__main__":
    # Initialize report generator
    report_gen = ReportGenerator()
    
    # Sample user data
    user_data = {
        'name': 'John Doe',
        'medication_history': [
            {
                'date': datetime.now() - timedelta(days=5),
                'medication': 'Amoxicillin',
                'action': 'Started',
                'notes': 'Prescribed for infection'
            }
        ]
    }
    
    # Sample medications
    medications = [
        {
            'name': 'Amoxicillin',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'start_date': datetime.now() - timedelta(days=5)
        }
    ]
    
    # Generate medication report
    report_path = report_gen.generate_medication_report(
        user_data,
        medications,
        datetime.now() - timedelta(days=30),
        datetime.now()
    )
    
    print(f"Report generated at: {report_path}") 