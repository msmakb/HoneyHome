# ------------------------------------ private ------------------------------------ #
import ast as _ast
from collections import namedtuple as _NT
from pathlib import Path as _path
from typing import Final

with open(_path(__file__).resolve().parent.parent / 'countries.txt', 'r') as _file:
    _countries = _ast.literal_eval(_file.read())
_main_app__templates_folder: Final[str] = '.'
_ceo_templates_folder: Final[str] = 'ceo'
_distributor_templates_folder: Final[str] = 'distributor'
_warehouse_admin_templates_folder: Final[str] = 'warehouse_admin'
_human_resources_templates_folder: Final[str] = 'human_resources'
_social_media_manager_templates_folder: Final[str] = 'social_media_manager'
_accounting_manager_templates_folder: Final[str] = 'accounting_manager'
print("Declaring Constants...")
# ---------------------------------- public --------------------------------------- #
BASE_MODEL_FIELDS: Final[tuple[str, ...]] = ('created', 'created_by',
                                             'updated', 'updated_by')
COUNTRY: Final[dict[str, str]] = _countries
HTML_TAGS_PATTERN: Final[str] = '<.*?>((.|\n)*)<\/.*?>'
MAIN_STORAGE_ID: Final[int] = 1
MAIN_STORAGE_NAME: Final[str] = 'Main Storage'
PERSONAL_PHOTOS_FOLDER: Final[str] = 'photographs'
GET_METHOD: Final[str] = 'GET'
POST_METHOD: Final[str] = 'POST'
DELETE_METHOD: Final[str] = 'DELETE'
ROWS_PER_PAGE: Final[int] = 10
SYSTEM_CRON_NAME: Final[str] = "System Cron"
SYSTEM_MIDDLEWARE_NAME: Final[str] = 'Middleware System'
SYSTEM_NAME: Final[str] = 'System'
SYSTEM_SIGNALS_NAME: Final[str] = 'System Signals'
ACCESS_TYPE = _NT('str', [
    'No_ACCESS',
    'ADMIN_ACCESS',
    'FULL_ACCESS'
])(
    '0',
    '1',
    '2'
)
ACTION = _NT('str', [
    'FIRST_VISIT',
    'LOGGED_IN',
    'LOGGED_OUT',
    'LOGGED_FAILED',
    'NORMAL_POST',
    'SUSPICIOUS_POST',
    'ATTACK_ATTEMPT',
])(
    'First Visit',
    'User logged in',
    'User logged out',
    'User logged failed',
    'Normal post',
    'Suspicious post',
    'Attack attempt',
)
ADMIN_SITE = _NT('str', [
    'SITE_HEADER',
    'SITE_TITLE',
    'INDEX_TITLE',
])(
    'Honey Home Administration',
    'Honey Home',
    'Admin Dashboard',
)
DATA_TYPE = _NT('str', [
    'STRING',
    'INTEGER',
    'FLOAT',
    'BOOLEAN'
])(
    '0',
    '1',
    '2',
    '3'
)
CRON_AT = _NT('str', [
    'EVERY_MINUTE',
    'EVERY_HOUR',
    'FIRST_MINUTE_ON_SUNDAY',
])(
    '*/1 * * * *',
    '0 * * * *',
    '1 0 * * 0',
)
CRON_DIR = _NT('str', [
    'MAIN',
    'HUMAN_RESOURCES',
])(
    'main.cron',
    'human_resources.cron',
)
BLOCK_TYPES = _NT('str', [
    'UNBLOCKED',
    'TEMPORARY',
    'INDEFINITELY',
])(
    'Unblocked',
    'Temporary',
    'Indefinitely',
)
ITEM_STATUS = _NT('str', [
    'GOOD',
    'DAMAGED',
    'FROZEN',
])(
    'Good',
    'Damaged',
    'Frozen',
)
LOGGERS = _NT('str', [
    'MAIN',
    'HUMAN_RESOURCES',
    'MIDDLEWARE',
    'MODELS',
])(
    'HoneyHome.Main',
    'HoneyHome.HumanResources',
    'HoneyHome.Middleware',
    'HoneyHome.Models',
)
ROLES = _NT('str', [
    'CEO',
    'HUMAN_RESOURCES',
    'WAREHOUSE_ADMIN',
    'ACCOUNTING_MANAGER',
    'SOCIAL_MEDIA_MANAGER',
    'DESIGNER',
    'DISTRIBUTOR'
])(
    'CEO',
    'Human Resources',
    'Warehouse Admin',
    'Accounting Manager',
    'Social Media Manager',
    'Designer',
    'Distributor'
)
TASK_STATUS = _NT('str', [
    'IN_PROGRESS',
    'ON_TIME',
    'LATE_SUBMISSION',
    'OVERDUE',
])(
    'In-Progress',
    'On-Time',
    'Late-Submission',
    'Overdue',
)
GENDER = _NT('str', [
    'MALE',
    'FEMALE'
])(
    'Male',
    'Female'
)
CHOICES = _NT('tuple', [
    'ACCESS_TYPE',
    'DATA_TYPE',
    'BLOCK_TYPE',
    'COUNTRY',
    'GENDER',
    'POSITIONS',
    'TASK_STATUS',
    'ITEM_STATUS',
])(
    [(access_type, access_type) for access_type in ACCESS_TYPE],
    [(data_type, data_type) for data_type in DATA_TYPE],
    [(block_type, block_type) for block_type in BLOCK_TYPES],
    [(country, country) for country in COUNTRY.values()],
    [(gender, gender) for gender in GENDER],
    [(role, role) for role in ROLES if role != ROLES.DISTRIBUTOR],
    [(status, status) for status in TASK_STATUS],
    [(status, status) for status in ITEM_STATUS],
)
RESPONSE_STATUS_CODE = _NT('int', [
    'SUCCESS',
    'REDIRECT',
    'FORBIDDEN'
])(
    200,
    302,
    403
)
TEMPLATES = _NT('str', [
    # Main templates
    'INDEX_TEMPLATE',
    'ABOUT_TEMPLATE',
    'UNAUTHORIZED_TEMPLATE',
    'DASHBOARD_TEMPLATE',
    'CREATE_USER_TEMPLATE',
    'TASKS_TEMPLATE',
    # Human resources templates
    'HUMAN_RESOURCES_DASHBOARD_TEMPLATE',
    'EMPLOYEES_TEMPLATE',
    'ADD_EMPLOYEE_TEMPLATE',
    'EMPLOYEE_RECORD_TEMPLATE',
    'UPDATE_EMPLOYEE_TEMPLATE',
    'DELETE_EMPLOYEE_TEMPLATE',
    'DISTRIBUTORS_TEMPLATE',
    'ADD_DISTRIBUTOR_TEMPLATE',
    'DISTRIBUTOR_RECORD_TEMPLATE',
    'UPDATE_DISTRIBUTOR_TEMPLATE',
    'DELETE_DISTRIBUTOR_TEMPLATE',
    'EMPLOYEES_TASKS_TEMPLATE',
    'ADD_TASK_TEMPLATE',
    'DETAILED_TASK_TEMPLATE',
    'UPDATE_TASK_TEMPLATE',
    'DELETE_TASK_TEMPLATE',
    'EVALUATION_TEMPLATE',
    'WEEKLY_EVALUATION_TEMPLATE',
    'TASK_EVALUATION_TEMPLATE',

    # CEO templates
    'CEO_DASHBOARD_TEMPLATE',
    # Warehouse admin templates
    'WAREHOUSE_ADMIN_DASHBOARD_TEMPLATE',
    'MAIN_STORAGE_GOODS_TEMPLATE',
    'DETAIL_ITEM_CARD_TEMPLATE',
    'ADD_GOODS_TEMPLATE',
    'BATCHES_TEMPLATE',
    'ADD_BATCH_TEMPLATE',
    'SEND_GOODS_TEMPLATE',
    'REGISTERED_ITEMS_TEMPLATE',
    'REGISTER_ITEM_TEMPLATE',
    'DISTRIBUTED_GOODS_TEMPLATE',
])(
    # Main templates
    f'{_main_app__templates_folder}/index.html',
    f'{_main_app__templates_folder}/about.html',
    f'{_main_app__templates_folder}/unauthorized.html',
    f'{_main_app__templates_folder}/Dashboard.html',
    f'{_main_app__templates_folder}/create_user.html',
    f'{_main_app__templates_folder}/tasks.html',
    # Human resources templates
    f'{_human_resources_templates_folder}/dashboard.html',
    f'{_human_resources_templates_folder}/employees.html',
    f'{_human_resources_templates_folder}/add_employee.html',
    f'{_human_resources_templates_folder}/employee.html',
    f'{_human_resources_templates_folder}/update_employee.html',
    f'{_human_resources_templates_folder}/delete_employee.html',
    f'{_human_resources_templates_folder}/distributors.html',
    f'{_human_resources_templates_folder}/add_distributor.html',
    f'{_human_resources_templates_folder}/distributor.html',
    f'{_human_resources_templates_folder}/update_distributor.html',
    f'{_human_resources_templates_folder}/delete_distributor.html',
    f'{_human_resources_templates_folder}/tasks.html',
    f'{_human_resources_templates_folder}/add_task.html',
    f'{_human_resources_templates_folder}/task.html',
    f'{_human_resources_templates_folder}/update_task.html',
    f'{_human_resources_templates_folder}/delete_task.html',
    f'{_human_resources_templates_folder}/evaluation.html',
    f'{_human_resources_templates_folder}/weekly_rate.html',
    f'{_human_resources_templates_folder}/task_evaluation.html',

    # CEO templates
    f'{_ceo_templates_folder}/dashboard.html',
    # Warehouse admin templates
    f'{_warehouse_admin_templates_folder}/dashboard.html',
    f'{_warehouse_admin_templates_folder}/main_storage_goods.html',
    f'{_warehouse_admin_templates_folder}/detail_item_cards.html',
    f'{_warehouse_admin_templates_folder}/add_goods.html',
    f'{_warehouse_admin_templates_folder}/batches.html',
    f'{_warehouse_admin_templates_folder}/add_batch.html',
    f'{_warehouse_admin_templates_folder}/send_goods.html',
    f'{_warehouse_admin_templates_folder}/registered_items.html',
    f'{_warehouse_admin_templates_folder}/register_item.html',
    f'{_warehouse_admin_templates_folder}/distributed_goods.html',
)
PAGES = _NT('str', [
    # Accounting manager pages
    'ACCOUNTING_MANAGER_DASHBOARD',
    'SALES_PAGE',
    'ADD_SALES_PAGE',
    'PRICING_PAGE',
    'EXPENSES_PAGE',
    'ADD_EXPENSES_PAGE',
    'UPDATE_EXPENSES_PAGE',
    'DELETE_EXPENSES_PAGE',
    'APPROVE_PAYMENTS_PAGE',
    'APPROVE_PAYMENT_PAGE',
    # CEO pages
    'CEO_DASHBOARD',
    # Distributors pages
    'DISTRIBUTOR_DASHBOARD',
    'GOODS_PAGE',
    'SEND_PAYMENT_PAGE',
    'FREEZE_ITEMS_PAGE',
    'RETURN_ITEMS_PAGE',
    'HISTORY_PAGE',
    # Human resources pages
    'HUMAN_RESOURCES_DASHBOARD',
    'EMPLOYEES_PAGE',
    'ADD_EMPLOYEE_PAGE',
    'EMPLOYEE_RECORD_PAGE',
    'UPDATE_EMPLOYEE_PAGE',
    'DELETE_EMPLOYEE_PAGE',
    'DISTRIBUTORS_PAGE',
    'ADD_DISTRIBUTOR_PAGE',
    'DISTRIBUTOR_RECORD_PAGE',
    'UPDATE_DISTRIBUTOR_PAGE',
    'DELETE_DISTRIBUTOR_PAGE',
    'EMPLOYEES_TASKS_PAGE',
    'ADD_TASK_PAGE',
    'DETAILED_TASK_PAGE',
    'UPDATE_TASK_PAGE',
    'DELETE_TASK_PAGE',
    'EVALUATION_PAGE',
    'WEEKLY_EVALUATION_PAGE',
    'TASK_EVALUATION_PAGE',
    # Main pages
    'INDEX',
    'LOGOUT',
    'DASHBOARD',
    'UNAUTHORIZED_PAGE',
    'ABOUT_PAGE',
    'CREATE_USER_PAGE',
    'TASKS_PAGE',
    # Warehouse admin pages
    'WAREHOUSE_ADMIN_DASHBOARD',
    'MAIN_STORAGE_GOODS_PAGE',
    'DETAIL_ITEM_CARDS_PAGE',
    'ADD_GOODS_PAGE',
    'REGISTERED_ITEMS_PAGE',
    'REGISTER_NEW_ITEM_PAGE',
    'BATCHES_PAGE',
    'ADD_BATCH_PAGE',
    'DISTRIBUTED_GOODS_PAGE',
    'DISTRIBUTOR_STOCK_PAGE',
    'SEND_GOODS_PAGE',
    'GOODS_MOVEMENT_PAGE',
    'DAMAGED_GOODS_PAGE',
    'ADD_DAMAGED_GOODS_PAGE',
    'TRANSFORMED_GOODS_PAGE',
    'APPROVE_TRANSFORMED_GOODS_PAGE',
    'RETAIL_GOODS_PAGE',
    'CONVERT_TO_RETAIL_PAGE',
    'ADD_RETAIL_GOODS_PAGE',
])(
    # Accounting manager pages
    'AccountingManagerDashboard',
    'SalesPage',
    'AddSalesPage',
    'PricingPage',
    'ExpensesPage',
    'AddExpensesPage',
    'UpdateExpensePage',
    'DeleteExpensePage',
    'ApprovePaymentsPage',
    'ApprovePayment',
    # CEO pages
    'CEODashboard',
    # Distributors pages
    'DistributorDashboard',
    'GoodsPage',
    'SendPaymentPage',
    'FreezeItemPage',
    'ReturnItemPage',
    'HistoryPage',
    # Human resources pages
    'HumanResourcesDashboard',
    'EmployeesPage',
    'AddEmployeePage',
    'EmployeePage',
    'UpdateEmployeePage',
    'DeleteEmployeePage',
    'DistributorsPage',
    'AddDistributorPage',
    'DistributorPage',
    'UpdateDistributorPage',
    'DeleteDistributorPage',
    'TasksPage',
    'AddTaskPage',
    'TaskPage',
    'UpdateTaskPage',
    'DeleteTaskPage',
    'EvaluationPage',
    'WeeklyEvaluationPage',
    'TaskEvaluationPage',
    # Main pages
    'Index',
    'Logout',
    'Dashboard',
    'Unauthorized',
    'About',
    'CreateUserPage',
    'Tasks',
    # Warehouse admin pages
    'WarehouseAdminDashboard',
    'MainStorageGoodsPage',
    'DetailItemCardsPage',
    'AddGoodsPage',
    'RegisteredItemsPage',
    'RegisterItemPage',
    'BatchesPage',
    'AddBatchPage',
    'DistributedGoodsPage',
    'DistributorStockPage',
    'SendGoodsPage',
    'GoodsMovementPage',
    'DamagedGoodsPage',
    'AddDamagedGoodsPage',
    'TransformedGoodsPage',
    'ApproveTransformedGoods',
    'RetailGoodsPage',
    'ConvertToRetailPage',
    'AddRetailGoodsPage',
)
PARAMETERS = _NT('str', [
    "ALLOWED_LOGGED_IN_ATTEMPTS",
    "ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
    "MAX_TEMPORARY_BLOCK",
    "TEMPORARY_BLOCK_PERIOD",
    "TIME_OUT_PERIOD",
    "BETWEEN_POST_REQUESTS_TIME",
    "MAGIC_NUMBER",
    "WEEKLY_RATE_TASK_NAME",
    "WEEKLY_RATE_TASK_DESCRIPTION",
    "WEEKLY_RATE_TASK_PERIOD"
])(
    "ALLOWED_LOGGED_IN_ATTEMPTS",
    "ALLOWED_LOGGED_IN_ATTEMPTS_RESET",
    "MAX_TEMPORARY_BLOCK",
    "TEMPORARY_BLOCK_PERIOD",
    "TIME_OUT_PERIOD",
    "BETWEEN_POST_REQUESTS_TIME",
    "MAGIC_NUMBER",
    "WEEKLY_RATE_TASK_NAME",
    "WEEKLY_RATE_TASK_DESCRIPTION",
    "WEEKLY_RATE_TASK_PERIOD"
)
