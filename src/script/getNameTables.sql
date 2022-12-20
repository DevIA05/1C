SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- "auth_group",
-- "auth_group_permissions",
-- "auth_permission",
-- "auth_user",
-- "auth_user_groups",
-- "auth_user_user_permissions",
-- "country",
-- "detailfacture",
-- "django_admin_log",
-- "django_content_type",
-- "django_migrations",
-- "django_session",
-- "invoice",
-- "product"
-- "tempcountry"
-- "tempdetailfacture"
-- "tempinvoice"
-- "tempproduct"