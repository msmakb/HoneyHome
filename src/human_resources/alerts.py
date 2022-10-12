from django.contrib import messages


# Employees messages
employee_added = lambda request: messages.success(request, "Employee added successfully")
employee_photo_updated = lambda request: messages.success(request, "Employee photo successfully updated")
employee_data_updated = lambda request: messages.success(request, "Employee data successfully updated")
employee_removed = lambda request: messages.success(request, "The employee successfully removed")

# Distributors messages
distributor_added = lambda request: messages.success(request, "Distributor added successfully")
distributor_photo_updated = lambda request: messages.success(request, "Distributor photo successfully updated")
distributor_data_updated = lambda request: messages.success(request, "Distributor data successfully updated")
distributor_removed = lambda request: messages.success(request, "The distributor successfully removed")

# Tasks messages
Task_added = lambda request: messages.success(request, "Task added successfully")
Task_data_updated = lambda request: messages.success(request, "Task data successfully updated")
Task_removed = lambda request: messages.success(request, "The task successfully removed")

# Evaluation messages
evaluation_done = lambda request: messages.info(request, "Weekly evaluation has been don")
many_weeks = lambda request: messages.warning(request, "There are more than one week you have been not rated.")
deleted_weeks = lambda request, i: messages.warning(request, f"{i} unrated week/s have been deleted from database, only last unrated week left.")
inform_ceo = lambda request: messages.info(request, "message have been sent to the CEO regarding this.")
tasks_evaluation_done = lambda request: messages.success(request, "Task has been rated successfully")
no_tasks_to_rate = lambda request: messages.info(request, "There is no more tasks to rate")
