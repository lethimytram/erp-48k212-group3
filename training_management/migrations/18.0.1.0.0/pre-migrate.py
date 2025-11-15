# -*- coding: utf-8 -*-

def migrate(cr, version):
    """Remove certificate-related fields from training_course table"""
    # Check if columns exist before trying to drop them
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='training_course' 
        AND column_name IN ('certificate_template_id', 'issue_certificate', 'has_certificate')
    """)
    
    existing_columns = [row[0] for row in cr.fetchall()]
    
    if 'certificate_template_id' in existing_columns:
        cr.execute("ALTER TABLE training_course DROP COLUMN certificate_template_id")
    
    if 'issue_certificate' in existing_columns:
        cr.execute("ALTER TABLE training_course DROP COLUMN issue_certificate")
        
    if 'has_certificate' in existing_columns:
        cr.execute("ALTER TABLE training_course DROP COLUMN has_certificate")
