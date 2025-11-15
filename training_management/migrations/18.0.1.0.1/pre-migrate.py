# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Re-add certificate columns that were dropped
    """
    # Re-add certificate columns to training_course
    cr.execute("""
        ALTER TABLE training_course 
        ADD COLUMN IF NOT EXISTS issue_certificate boolean DEFAULT true;
    """)
    
    cr.execute("""
        ALTER TABLE training_course 
        ADD COLUMN IF NOT EXISTS certificate_template_id integer;
    """)
    
    # Add foreign key constraint
    cr.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint 
                WHERE conname = 'training_course_certificate_template_id_fkey'
            ) THEN
                ALTER TABLE training_course 
                ADD CONSTRAINT training_course_certificate_template_id_fkey 
                FOREIGN KEY (certificate_template_id) 
                REFERENCES training_certificate_template(id) 
                ON DELETE SET NULL;
            END IF;
        END$$;
    """)
