-- Script to uninstall highland_training module completely
-- Run this in pgAdmin or psql

-- 1. Delete module record
DELETE FROM ir_module_module WHERE name = 'highland_training';

-- 2. Delete module data
DELETE FROM ir_model_data WHERE module = 'highland_training';

-- 3. Delete models
DELETE FROM ir_model WHERE model LIKE 'training.%';

-- 4. Delete fields
DELETE FROM ir_model_fields WHERE model LIKE 'training.%';

-- 5. Delete access rights
DELETE FROM ir_model_access WHERE name LIKE '%training%';

-- 6. Delete menu items
DELETE FROM ir_ui_menu WHERE name LIKE '%Highland%' OR name LIKE '%training%';

-- 7. Delete views
DELETE FROM ir_ui_view WHERE name LIKE 'training.%';

-- 8. Delete actions
DELETE FROM ir_actions_act_window WHERE res_model LIKE 'training.%';

-- 9. Commit
COMMIT;

-- Now you can reinstall the module fresh
