from collections import namedtuple as _namedtuple

# ----------------------private--------------------------- #
_main_app__templates_folder = '.'                          #
_ceo_templates_folder = 'ceo'                              #
_human_resources_templates_folder = 'human_resources'      #
_warehouse_admin_templates_folder = 'warehouse_admin'      #
# -------------------------------------------------------- #

MAIN_STORAGE_ID: int = 1
PAGINATE_BY: int = 10
POST = 'POST'

CHOICES = _namedtuple('tuple', [
    'COUNTRY',
    'GENDER',
    'POSITIONS',
    'STATUS',
])(
    # COUNTRY
    (
        ('YEM', 'YEMEN'),
        ('ID', 'INDONESIA')
    ),
    # GENDER
    (
        ('Male', 'Male'),
        ('Female', 'Female')
    ),
    # POSITIONS
    (
        ('CEO', 'CEO'),
        ('Human Resources', 'Human Resources'),
        ('Warehouse Admin', 'Warehouse Admin'),
        ('Accounting Manager', 'Accounting Manager'),
        ('Social Media Manager', 'Social Media Manager'),
        ('Designer', 'Designer'),
        ('Distributor', 'Distributor')
    ),
    (
        ('In-Progress', 'In-Progress'),
        ('On-Time', 'On-Time'),
        ('Late-Submission', 'Late-Submission'),
        ('Overdue', 'Overdue')
    ),
)

TEMPLATES = _namedtuple('str', [
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
    f'{_human_resources_templates_folder}/delete_Task.html',
    f'{_human_resources_templates_folder}/evaluation.html',
    f'{_human_resources_templates_folder}/weekly_rate.html',
    f'{_human_resources_templates_folder}/task_evaluation.html',

    # CEO templates
    f'{_ceo_templates_folder}/dashboard.html',
)

PAGES = _namedtuple('str', [
    # Main pages
    'INDEX',
    'LOGOUT',
    'DASHBOARD',
    'UNAUTHORIZED_PAGE',
    'ABOUT_PAGE',
    'CREATE_USER_PAGE',
    'TASKS_PAGE',
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

    # CEO pages
    'CEO_DASHBOARD',
    'EMPLOYEES_PAGE_CEO',
    'ADD_EMPLOYEE_PAGE_CEO',
    'EMPLOYEE_RECORD_PAGE_CEO',
    'UPDATE_EMPLOYEE_PAGE_CEO',
    'DELETE_EMPLOYEE_PAGE_CEO',
    'DISTRIBUTORS_PAGE_CEO',
    'ADD_DISTRIBUTOR_PAGE_CEO',
    'DISTRIBUTOR_RECORD_PAGE_CEO',
    'UPDATE_DISTRIBUTOR_PAGE_CEO',
    'DELETE_DISTRIBUTOR_PAGE_CEO',
    'EMPLOYEES_TASKS_PAGE_CEO',
    'ADD_TASK_PAGE_CEO',
    'DETAILED_TASK_PAGE_CEO',
    'UPDATE_TASK_PAGE_CEO',
    'DELETE_TASK_PAGE_CEO',
    'EVALUATION_PAGE_CEO',
    'WEEKLY_EVALUATION_PAGE_CEO',
    'TASK_EVALUATION_PAGE_CEO',
])(
    # Main pages
    'Index',
    'Logout',
    'Dashboard',
    'Unauthorized',
    'About',
    'CreateUserPage',
    'Tasks',
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

    # CEO pages
    'CEODashboard',
    'EmployeesPage-CEO',
    'AddEmployeePage-CEO',
    'EmployeePage-CEO',
    'UpdateEmployeePage-CEO',
    'DeleteEmployeePage-CEO',
    'DistributorsPage-CEO',
    'AddDistributorPage-CEO',
    'DistributorPage-CEO',
    'UpdateDistributorPage-CEO',
    'DeleteDistributorPage-CEO',
    'TasksPage-CEO',
    'AddTaskPage-CEO',
    'TaskPage-CEO',
    'UpdateTaskPage-CEO',
    'DeleteTaskPage-CEO',
    'EvaluationPage-CEO',
    'WeeklyEvaluationPage-CEO',
    'TaskEvaluationPage-CEO',
)

ROLES = _namedtuple('str', [
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
