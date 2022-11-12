from django.contrib import messages

"""============================= Main Messages ============================="""
BLOCK_WARNING = lambda request: messages.warning(
    request, "WARNING!! The system logged you out for spamming, "
    + "next time you will be blocked")
CREATE_NEW_ACCOUNT = lambda request: messages.success(
    request, f"Please create new account with your personal information.")
INCORRECT_INFO = lambda request: messages.error(
    request, "Username or Password is incorrect")
LOGIN_WITH_NEW_ACCOUNT = lambda request: messages.info(
    request, "Please sing in with your new account")
SOMETHING_WRONG = lambda request: messages.warning(
    request, "Ops!! something went wrong...")
TEMPORARY_ACCOUNT = lambda request: messages.success(
    request, f"This account you singed in is a temporary account.")
TIME_OUT = lambda request: messages.info(
    request, "Your session has timed out. Please login again.")
WELCOME_MESSAGE = lambda request, first_name: messages.success(
    request, f"Hello, {first_name}. Welcome to Honey Home System.")

"""======================== Human Resources Messages ========================"""
DISTRIBUTOR_ADDED = lambda request: messages.success(
    request, "Distributor added successfully")
DISTRIBUTOR_DATA_UPDATED = lambda request: messages.success(
    request, "Distributor data successfully updated")
DISTRIBUTOR_PHOTO_UPDATED = lambda request: messages.success(
    request, "Distributor photo successfully updated")
DISTRIBUTOR_REMOVED = lambda request: messages.success(
    request, "The distributor successfully removed")
EMPLOYEE_ADDED = lambda request: messages.success(
    request, "Employee added successfully")
EMPLOYEE_DATA_UPDATED = lambda request: messages.success(
    request, "Employee data successfully updated")
EMPLOYEE_PHOTO_UPDATED = lambda request: messages.success(
    request, "Employee photo successfully updated")
EMPLOYEE_REMOVED = lambda request: messages.success(
    request, "The employee successfully removed")
EVALUATION_DONE = lambda request: messages.info(
    request, "Weekly evaluation has been don")
INFORM_CEO = lambda request: messages.info(
    request, "message have been sent to the CEO regarding this.")
MANY_WEEKS = lambda request: messages.warning(
    request, "There are more than one week you have been not rated.")
RATE_TASKS_DONE = lambda request: messages.info(
    request, "There is no more tasks to rate")
TASK_ADDED = lambda request: messages.success(
    request, "Task added successfully")
TASK_DATA_UPDATED = lambda request: messages.success(
    request, "Task data successfully updated")
TASK_REMOVED = lambda request: messages.success(
    request, "The task successfully removed")
TASKS_EVALUATION_DONE = lambda request: messages.success(
    request, "Task has been rated successfully")
WEEKS_DELETED = lambda request, i: messages.warning(
    request, f"{i} unrated week/s have been deleted from"
    + " database, only last unrated week left.")
