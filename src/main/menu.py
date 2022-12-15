from django.http import HttpRequest

from main.utils import getUserRole

from .constants import PAGES, ROLES


ACCOUNTING_MANAGER_MENU: dict[str, str] = {
    "Dashboard": PAGES.ACCOUNTING_MANAGER_DASHBOARD,
    "Sales": PAGES.SALES_PAGE,
    "Pricing": PAGES.PRICING_PAGE,
    "Expenses": PAGES.EXPENSES_PAGE,
    "Approve Payments": PAGES.APPROVE_PAYMENTS_PAGE,
    "My Tasks": PAGES.TASKS_PAGE,
}

CEO_MENU: dict[str, str] = {
    "Dashboard": PAGES.CEO_DASHBOARD,
    "Sales": PAGES.SALES_PAGE,
    "Pricing": PAGES.PRICING_PAGE,
    "Expenses": PAGES.EXPENSES_PAGE,
    "Approve Payments": PAGES.APPROVE_PAYMENTS_PAGE,
    "Main Storage Goods": PAGES.MAIN_STORAGE_GOODS_PAGE,
    "Distributed Goods": PAGES.DISTRIBUTED_GOODS_PAGE,
    "Retail Goods": PAGES.RETAIL_GOODS_PAGE,
    "Damaged Goods": PAGES.DAMAGED_GOODS_PAGE,
    "Transformed Goods": PAGES.TRANSFORMED_GOODS_PAGE,
    "Goods Movement": PAGES.GOODS_MOVEMENT_PAGE,
    "Registered Items": PAGES.REGISTERED_ITEMS_PAGE,
    "Batches": PAGES.BATCHES_PAGE,
    "Employees": PAGES.EMPLOYEES_PAGE,
    "Distributors": PAGES.DISTRIBUTORS_PAGE,
    "Employees' Tasks": PAGES.EMPLOYEES_TASKS_PAGE,
    "Evaluation": PAGES.EVALUATION_PAGE,
    # "Customers": "",
    # "Questionnaires": "",
}

DISTRIBUTOR_MENU: dict[str, str] = {
    "Dashboard": PAGES.DISTRIBUTOR_DASHBOARD,
    "Goods": PAGES.GOODS_PAGE,
    "Send Payment": PAGES.SEND_PAYMENT_PAGE,
    "Freeze Item": PAGES.FREEZE_ITEMS_PAGE,
    "Send/Return Item": PAGES.RETURN_ITEMS_PAGE,
    "History": PAGES.HISTORY_PAGE,
}

HUMAN_RESOURCES_MENU: dict[str, str] = {
    "Dashboard": PAGES.HUMAN_RESOURCES_DASHBOARD,
    "Employees": PAGES.EMPLOYEES_PAGE,
    "Distributors": PAGES.DISTRIBUTORS_PAGE,
    "Employees' Tasks": PAGES.EMPLOYEES_TASKS_PAGE,
    "Evaluation": PAGES.EVALUATION_PAGE,
    "My Tasks": PAGES.TASKS_PAGE,
}
SOCIAL_MEDIA_MANAGER_MENU: dict[str, str] = {
    "Dashboard": 'SocialMediaManagerDashboard',
    "Customers": 'CustomersPage',
    "Questionnaires": 'QuestionnairesPage',
    # "File Manager": '',
    "My Tasks": PAGES.TASKS_PAGE,
}
WAREHOUSE_ADMIN_MENU: dict[str, str] = {
    "Dashboard": PAGES.WAREHOUSE_ADMIN_DASHBOARD,
    "Main Storage Goods": PAGES.MAIN_STORAGE_GOODS_PAGE,
    "Distributed Goods": PAGES.DISTRIBUTED_GOODS_PAGE,
    "Retail Goods": PAGES.RETAIL_GOODS_PAGE,
    "Damaged Goods": PAGES.DAMAGED_GOODS_PAGE,
    "Transformed Goods": PAGES.TRANSFORMED_GOODS_PAGE,
    "Goods Movement": PAGES.GOODS_MOVEMENT_PAGE,
    "Registered Items": PAGES.REGISTERED_ITEMS_PAGE,
    "Batches": PAGES.BATCHES_PAGE,
    "My Tasks": PAGES.TASKS_PAGE,
}


def getUserMenu(request: HttpRequest) -> dict[str, str]:
    role: str = getUserRole(request)
    if role is None:
        raise ValueError("Role must not be None")

    match role:
        case ROLES.ACCOUNTING_MANAGER:
            return ACCOUNTING_MANAGER_MENU
        case ROLES.CEO:
            return CEO_MENU
        case ROLES.DISTRIBUTOR:
            return DISTRIBUTOR_MENU
        case ROLES.HUMAN_RESOURCES:
            return HUMAN_RESOURCES_MENU
        case ROLES.SOCIAL_MEDIA_MANAGER:
            return SOCIAL_MEDIA_MANAGER_MENU
        case ROLES.WAREHOUSE_ADMIN:
            return WAREHOUSE_ADMIN_MENU

    raise NotImplementedError(f"The menu is not implemented "
                              + "for this role '{role}'.")
