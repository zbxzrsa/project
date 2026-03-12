from enum import Enum


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


class Permission(str, Enum):
    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"

    # Tenant Management
    CREATE_TENANT = "create_tenant"
    READ_TENANT = "read_tenant"
    UPDATE_TENANT = "update_tenant"
    DELETE_TENANT = "delete_tenant"

    # Project Management
    CREATE_PROJECT = "create_project"
    READ_PROJECT = "read_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"

    # Review Management
    CREATE_REVIEW = "create_review"
    READ_REVIEW = "read_review"
    DELETE_REVIEW = "delete_review"

    # Analysis
    RUN_ANALYSIS = "run_analysis"
    READ_ANALYSIS = "read_analysis"

    # Feature Flags
    MANAGE_FEATURE_FLAGS = "manage_feature_flags"

    # Audit Logs
    READ_AUDIT_LOGS = "read_audit_logs"

    # System
    SYSTEM_SETTINGS = "system_settings"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.SUPERADMIN: set(Permission),
    UserRole.ADMIN: {
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.READ_TENANT,
        Permission.UPDATE_TENANT,
        Permission.CREATE_PROJECT,
        Permission.READ_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.CREATE_REVIEW,
        Permission.READ_REVIEW,
        Permission.DELETE_REVIEW,
        Permission.RUN_ANALYSIS,
        Permission.READ_ANALYSIS,
        Permission.MANAGE_FEATURE_FLAGS,
        Permission.READ_AUDIT_LOGS,
    },
    UserRole.USER: {
        Permission.READ_USER,
        Permission.READ_TENANT,
        Permission.CREATE_PROJECT,
        Permission.READ_PROJECT,
        Permission.UPDATE_PROJECT,
        Permission.CREATE_REVIEW,
        Permission.READ_REVIEW,
        Permission.RUN_ANALYSIS,
        Permission.READ_ANALYSIS,
    },
    UserRole.READONLY: {
        Permission.READ_USER,
        Permission.READ_TENANT,
        Permission.READ_PROJECT,
        Permission.READ_REVIEW,
        Permission.READ_ANALYSIS,
    },
}


def get_role_permissions(role: UserRole) -> set[Permission]:
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
