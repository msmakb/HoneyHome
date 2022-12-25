from django.contrib.auth.models import Group, User, AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, Http404
from django.test import SimpleTestCase, TestCase, RequestFactory
from django.test.client import Client
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.timezone import datetime, timedelta

from . import constants
from .cron import setMagicNumber
from .middleware import AllowedClientMiddleware, LoginRequiredMiddleware, AllowedUserMiddleware
from .models import AuditEntry, BlockedClient, Parameter, Person
from .parameters import getParameterValue
from .views import index, about, unauthorized, logoutUser, createUserPage, tasks
from .utils import setCreatedByUpdatedBy, getUserRole, getEmployeesTasks, getClientIp, getUserAgent, resolvePageUrl

from human_resources.models import Employee, Task

SUCCESS_RESPONSE_STATUS_CODE = 200
REDIRECT_STATUS_CODE: int = 302
RESPONSE_FORBIDDEN_STATUS_CODE = 403


class TestInitialization(TestCase):

    def test_is_roles_created(self) -> None:
        for role in constants.ROLES:
            role_in_database: str = Group.objects.get(name=role).name
            self.assertEquals(role_in_database, role)

    def test_is_default_parameters_inserted_to_database(self) -> None:
        num_of_param: int = Parameter.objects.all().count()
        self.assertGreater(num_of_param, 5)

    def test_is_superuser_ceo_created(self) -> None:
        users: QuerySet[User] = User.objects.all()
        self.assertEquals(users.count(), 1)
        employees: QuerySet[Employee] = Employee.objects.all()
        self.assertEquals(employees.count(), 1)
        ceo: Employee = employees.first()
        self.assertEquals(ceo.person.name, "CEO")
        self.assertEquals(ceo.account.first_name, "CEO")
        self.assertTrue(ceo.account.is_superuser)


class TestCron(TestCase):

    def setUp(self) -> None:
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"

    def test_magic_number_reset_login_failed_attempts(self):
        for i in range(3):
            audit_entry: AuditEntry = AuditEntry.objects.create(
                ip=self.test_ip,
                user_agent=self.user_agent,
                action=constants.ACTION.LOGGED_FAILED
            )
            audit_entry.setCreated(timezone.now() - timedelta(days=10))
        audit_entry: AuditEntry = AuditEntry.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            action=constants.ACTION.NORMAL_POST
        )
        setMagicNumber()
        self.assertEquals(getParameterValue(constants.PARAMETERS.MAGIC_NUMBER),
                          audit_entry.id)

    def test_magic_number_cleanup_unsuspicious_posts(self):
        for i in range(5):
            audit_entry: AuditEntry = AuditEntry.objects.create(
                ip=self.test_ip,
                user_agent=self.user_agent,
                action=constants.ACTION.NORMAL_POST
            )
            audit_entry.setCreated(timezone.now() - timedelta(days=10))
        AuditEntry.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            action=constants.ACTION.NORMAL_POST
        )
        setMagicNumber()
        self.assertEquals(AuditEntry.objects.all().count(), 1)

    def tearDown(self) -> None:
        for row in AuditEntry.objects.all():
            try:
                row.delete("")
            except:
                row.delete()
        return super().tearDown()


class TestAllowedClientMiddleware(TestCase):

    def setUp(self) -> None:
        self.middleware = AllowedClientMiddleware(lambda request: None)
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.anonymous_user = AnonymousUser()
        self.logged_superuser_ceo: User = User.objects.first()
        self.logged_superuser_ceo.last_login = datetime.now()

    def test_first_visit_recorded(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.__call__(request))
        first_visit: QuerySet[AuditEntry] = AuditEntry.objects.filter(
            action=constants.ACTION.FIRST_VISIT)
        self.assertIsNotNone(first_visit)
        self.assertEquals(first_visit.first().ip, self.test_ip)

    def test_spam_post_request(self):
        request: HttpRequest = self.client.get(reverse(constants.PAGES.INDEX))
        request.user = self.anonymous_user
        request.method = constants.POST_METHOD
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        self.middleware.__call__(request)
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        for i in range(3):
            self.middleware.__call__(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        request.method = constants.GET_METHOD
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, RESPONSE_FORBIDDEN_STATUS_CODE)
        self.assertEquals(BlockedClient.objects.filter(ip=self.test_ip).last().block_type,
                          constants.BLOCK_TYPES.TEMPORARY)
        request.method = constants.POST_METHOD
        for i in range(3):
            self.middleware.__call__(request)
        self.assertEquals(BlockedClient.objects.filter(ip=self.test_ip).last().block_type,
                          constants.BLOCK_TYPES.INDEFINITELY)

    def test_blocked_client(self) -> None:
        BlockedClient.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            block_type=constants.BLOCK_TYPES.TEMPORARY
        )
        request: HttpRequest = self.client.get(constants.PAGES.INDEX)
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, RESPONSE_FORBIDDEN_STATUS_CODE)

    def test_blocked_client_and_allowed_to_be_unblocked(self) -> None:
        BlockedClient.objects.create(
            ip=self.test_ip,
            user_agent=self.user_agent,
            block_type=constants.BLOCK_TYPES.TEMPORARY
        )
        BlockedClient.objects.filter().update(
            updated=timezone.now() - timedelta(days=100))
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.ABOUT_PAGE))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.__call__(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.ABOUT_PAGE))

    def test_block_client_who_filed_to_login_many_times(self) -> None:
        for i in range(5):
            AuditEntry.objects.create(
                ip=self.test_ip,
                user_agent=self.user_agent,
                action=constants.ACTION.LOGGED_FAILED
            )
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.__call__(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        response: HttpResponse = self.middleware.__call__(request)
        self.assertEquals(response.status_code, RESPONSE_FORBIDDEN_STATUS_CODE)

    def tearDown(self) -> None:
        for row in AuditEntry.objects.all():
            try:
                row.delete("")
            except:
                row.delete()
        for row in BlockedClient.objects.all():
            try:
                row.delete("")
            except:
                row.delete()
        return super().tearDown()


class TestLoginRequiredMiddleware(TestCase):

    def setUp(self) -> None:
        self.middleware = LoginRequiredMiddleware(lambda request: None)
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.anonymous_user = AnonymousUser()
        self.logged_superuser_ceo: User = User.objects.first()
        self.logged_superuser_ceo.last_login = datetime.now()

    def test_anonymous_user_trying_to_access_admin_site(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.anonymous_user
        self.assertRaises(Http404, self.middleware.process_view, request)

    def test_superuser_trying_to_access_admin_site(self):
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.process_view(request))

    def test_access_login_required_page(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(f"CEO:{constants.PAGES.CEO_DASHBOARD}"))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))

        request: HttpRequest = self.client.get(
            reverse(f"CEO:{constants.PAGES.EMPLOYEES_PAGE}"))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))

        request: HttpRequest = self.client.get(
            reverse(f"CEO:{constants.PAGES.REGISTERED_ITEMS_PAGE}"))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))

        request: HttpRequest = self.client.get(
            reverse(f"HumanResources:{constants.PAGES.EMPLOYEES_TASKS_PAGE}"))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))

        request: HttpRequest = self.client.get(
            reverse(f"WarehouseAdmin:{constants.PAGES.MAIN_STORAGE_GOODS_PAGE}"))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))

    def test_access_excluded_pages_from_login(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX))
        request.user = self.anonymous_user
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.ABOUT_PAGE))
        request.user = self.anonymous_user
        self.assertIsNone(self.middleware.process_view(request))

    def test_create_user_page_required_login(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.CREATE_USER_PAGE))
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.CREATE_USER_PAGE))
        request.user = self.anonymous_user
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))

    def test_is_user_session_timeout(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX))
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX))
        request.user = self.logged_superuser_ceo
        request.user.last_login = timezone.now() - timedelta(minutes=1500)
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))


class TestAllowedUserMiddleware(TestCase):

    def setUp(self) -> None:
        self.middleware = AllowedUserMiddleware(lambda request: None)
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.anonymous_user = AnonymousUser()
        self.logged_superuser_ceo: User = User.objects.first()
        self.logged_non_superuser: User = Employee.objects.create(
            person=Person.objects.create(name="TEST"),
            position=constants.ROLES.HUMAN_RESOURCES).account  # <- user created from signals
        self.logged_non_superuser.username = "NonSuperuser"
        self.logged_non_superuser.save()
        self.logged_superuser_ceo.last_login = datetime.now()
        self.logged_non_superuser.last_login = datetime.now()

    def test_is_allowed_to_access_admin(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_superuser_ceo
        self.assertTrue(self.middleware.isAllowedToAccessAdmin(request))
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.anonymous_user
        self.assertFalse(self.middleware.isAllowedToAccessAdmin(request))
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_non_superuser
        self.assertEquals(request.user.groups.first().name,
                          constants.ROLES.HUMAN_RESOURCES)
        self.assertFalse(self.middleware.isAllowedToAccessAdmin(request))

    def test_doing_nothing_if_user_is_not_authenticated(self) -> None:
        """This middleware for authenticated users only"""
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.ABOUT_PAGE))
        request.user = self.anonymous_user
        self.assertIsNone(self.middleware.process_view(request))

    def test_allowed_user_to_access_page(self) -> None:
        self.logged_superuser_ceo.username = "allowed-user"
        self.logged_superuser_ceo.save()

        def process_session(request: HttpRequest) -> HttpRequest:
            setattr(request, 'session', 'session')
            setattr(request, '_messages', FallbackStorage(request))
            session_middleware = SessionMiddleware(lambda request: None)
            session_middleware.process_request(request)
            request.session.save()
            return request

        request: HttpRequest = self.client.get(
            reverse("CEO:" + constants.PAGES.CEO_DASHBOARD))
        request = process_session(request)
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse("CEO:" + constants.PAGES.EMPLOYEES_TASKS_PAGE))
        request = process_session(request)
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse("CEO:" + constants.PAGES.SALES_PAGE))
        request = process_session(request)
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse("CEO:" + constants.PAGES.MAIN_STORAGE_GOODS_PAGE))
        request = process_session(request)
        request.user = self.logged_superuser_ceo
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse("HumanResources:" + constants.PAGES.EMPLOYEES_PAGE))
        request = process_session(request)
        request.user = self.logged_non_superuser
        self.assertEquals(request.user.groups.first().name,
                          constants.ROLES.HUMAN_RESOURCES)
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse("HumanResources:" + constants.PAGES.TASK_EVALUATION_PAGE))
        request = process_session(request)
        request.user = self.logged_non_superuser
        self.assertIsNone(self.middleware.process_view(request))

        request: HttpRequest = self.client.get(
            reverse("HumanResources:" + constants.PAGES.EVALUATION_PAGE))
        request = process_session(request)
        request.user = self.logged_non_superuser
        self.assertIsNone(self.middleware.process_view(request))

    def test_not_allowed_user_to_access_page(self) -> None:
        self.logged_superuser_ceo.username = "allowed-user"
        self.logged_superuser_ceo.save()

        def process_session_request_and_response(request: HttpRequest, user: User) -> tuple[HttpRequest, HttpResponse]:
            setattr(request, 'session', 'session')
            setattr(request, '_messages', FallbackStorage(request))
            session_middleware = SessionMiddleware(lambda request: None)
            session_middleware.process_request(request)
            request.session.save()
            request.user = user
            response: HttpResponse = self.middleware.process_view(request)
            response.client = Client()
            return request, response

        request: HttpRequest = self.client.get(
            reverse("HumanResources:" + constants.PAGES.HUMAN_RESOURCES_DASHBOARD))
        request, response = process_session_request_and_response(
            request, self.logged_superuser_ceo)
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=REDIRECT_STATUS_CODE)

        request: HttpRequest = self.client.get(
            reverse("WarehouseAdmin:" + constants.PAGES.WAREHOUSE_ADMIN_DASHBOARD))
        request, response = process_session_request_and_response(
            request, self.logged_superuser_ceo)
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=REDIRECT_STATUS_CODE)

        request: HttpRequest = self.client.get(
            reverse("WarehouseAdmin:" + constants.PAGES.WAREHOUSE_ADMIN_DASHBOARD))
        request, response = process_session_request_and_response(
            request, self.logged_non_superuser)
        self.assertEquals(request.user.groups.first().name,
                          constants.ROLES.HUMAN_RESOURCES)
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=REDIRECT_STATUS_CODE)

        request: HttpRequest = self.client.get(
            reverse("WarehouseAdmin:" + constants.PAGES.DISTRIBUTED_GOODS_PAGE))
        request, response = process_session_request_and_response(
            request, self.logged_non_superuser)
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=REDIRECT_STATUS_CODE)

        request: HttpRequest = self.client.get(
            reverse("AccountingManager:" + constants.PAGES.SALES_PAGE))
        request, response = process_session_request_and_response(
            request, self.logged_non_superuser)
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.UNAUTHORIZED_PAGE),
                             target_status_code=REDIRECT_STATUS_CODE)

    def test_non_superuser_trying_to_access_admin(self) -> None:
        request: HttpRequest = self.client.get(reverse("admin:index"))
        request.user = self.logged_non_superuser
        self.assertRaises(Http404, self.middleware.process_view, request)

    def test_user_is_in_unauthenticated_page_error(self) -> None:
        """
        If user in the page error that the system redirected
        him after trying to access unauthenticated page.
        """
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.UNAUTHORIZED_PAGE))
        request.user = self.logged_non_superuser
        self.assertIsNone(self.middleware.process_view(request))

    def test_user_has_no_groups(self) -> None:
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.INDEX))
        request.user = self.logged_non_superuser
        request.user.groups.clear()
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        response: HttpResponse = self.middleware.process_view(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.LOGOUT),
                             target_status_code=REDIRECT_STATUS_CODE)


class TestModels(TestCase):

    def setUp(self) -> None:
        self.test_engine_name: str = "Test Engine"
        self.person: Person = Person.objects.create(
            name="Tester"
        )

    def test_base_model_create(self) -> None:
        person: Person = Person.create(
            self.test_engine_name,
            name="Test Create Person"
        )
        self.assertEquals(person.name, "Test Create Person")
        self.assertEquals(person.created_by,
                          self.test_engine_name)
        self.assertEquals(person.updated_by,
                          self.test_engine_name)

    def test_base_model_delete(self) -> None:
        id: int = self.person.id
        self.person.delete(self.test_engine_name)
        try:
            person = Person.objects.get(id=id)
        except Person.DoesNotExist:
            person = None
        self.assertIsNone(person)

    def test_base_model_get(self) -> None:
        id: int = self.person.id
        person: Person = Person.get(id=id)
        self.assertEquals(self.person, person)
        for i in range(5):
            Person.objects.create(name="test get multiple")
        person = Person.get(name="test get multiple")
        self.assertIsNone(person)

    def test_base_model_get_all(self) -> None:
        existing_objects_count: int = Person.objects.all().count()
        for i in range(5):
            Person.objects.create(name=f"Person{i}")
        people: QuerySet[Person] = Person.getAll()
        self.assertEquals(people.count(), existing_objects_count + 5)

    def test_base_model_set_created_by_updated_by(self) -> None:
        person: Person = Person.create(
            self.test_engine_name,
            name="test created updated"
        )
        self.assertEquals(person.created_by,
                          self.test_engine_name)
        self.assertEquals(person.updated_by,
                          self.test_engine_name)
        person.setUpdatedBy("Tester")
        self.assertEquals(person.updated_by, "Tester")
        person.setContactingEmail(self.test_engine_name, "test@test.ts")
        self.assertEquals(person.created_by,
                          self.test_engine_name)
        self.assertEquals(person.updated_by,
                          self.test_engine_name)

    def test_base_model_get_all_ordered(self) -> None:
        for i in range(5):
            Person.objects.create(name=str(i))
        popple: QuerySet[Person] = Person.getAllOrdered(
            "name", reverse=True).reverse()
        for i in range(5):
            self.assertEquals(popple[i].name, str(i))

    def test_base_model_get_last_inserted_object(self) -> None:
        Person.objects.create(name="Test get last")
        person: Person = Person.getLastInsertedObject()
        self.assertEquals(person.name, "Test get last")
        for i in range(5):
            Person.objects.create(name=str(i), address="get last test")
        popple: QuerySet[Person] = Person.objects.filter(
            address="get last test").reverse()
        person: Person = Person.getLastInsertedObject(popple)
        self.assertEquals(person.name + person.address, "0get last test")

    def test_base_model_filter(self) -> None:
        for i in range(5):
            Person.objects.create(gender=constants.GENDER.MALE)
        popple: QuerySet[Person] = Person.filter(gender=constants.GENDER.MALE)
        self.assertEquals(popple.count(), 5)
        self.assertEquals(popple.first().gender, constants.GENDER.MALE)

    def test_base_model_count_all(self) -> None:
        self.assertEquals(Person.objects.all().count(), Person.countAll())

    def test_base_model_count_filtered(self) -> None:
        for i in range(5):
            Person.objects.create(nationality=constants.COUNTRY.get("YEMEN"))
        self.assertEquals(Person.countFiltered(
            nationality=constants.COUNTRY.get("YEMEN")), 5)

    def test_base_model_is_exists(self) -> None:
        Person.objects.create(name="person exists")
        self.assertTrue(Person.isExists(name="person exists"))
        self.assertFalse(Person.isExists(name="person not exists"))


class TestParameter(TestCase):

    def test_non_exciting_parameter(self) -> None:
        self.assertRaises(KeyError, getParameterValue,
                          "NON_EXISTING_PARAMETER")

    def test_string_type_parameter(self) -> None:
        string_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_STRING",
            value="TEST_STRING",
            parameter_type=constants.DATA_TYPE.STRING,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_STRING"), str)
        self.assertEquals(getParameterValue("TEST_PARAM_STRING"),
                          "TEST_STRING")
        string_param.value = "1"
        string_param.save()
        self.assertIsInstance(getParameterValue("TEST_PARAM_STRING"), str)

    def test_integer_type_parameter(self) -> None:
        integer_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_INTEGER",
            value="1",
            parameter_type=constants.DATA_TYPE.INTEGER,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_INTEGER"), int)
        self.assertEquals(getParameterValue("TEST_PARAM_INTEGER"), 1)
        integer_param.value = "Wrong data type"
        integer_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_INTEGER")
        integer_param.value = "1.03"  # float
        integer_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_INTEGER")

    def test_float_type_parameter(self) -> None:
        float_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_FLOAT",
            value="1.05",
            parameter_type=constants.DATA_TYPE.FLOAT,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_FLOAT"), float)
        self.assertEquals(getParameterValue("TEST_PARAM_FLOAT"), 1.05)
        float_param.value = "Wrong data type"
        float_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_FLOAT")

    def test_boolean_type_parameter(self) -> None:
        boolean_param: Parameter = Parameter.objects.create(
            name="TEST_PARAM_BOOLEAN",
            value="True",
            parameter_type=constants.DATA_TYPE.BOOLEAN,
        )
        self.assertIsInstance(getParameterValue("TEST_PARAM_BOOLEAN"), bool)
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"), True)
        boolean_param.value = "true"
        boolean_param.save()
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "YES"
        boolean_param.save()
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "1"
        boolean_param.save()
        self.assertTrue(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "FaLsE"
        boolean_param.save()
        self.assertFalse(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "nO"
        boolean_param.save()
        self.assertFalse(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "0"
        boolean_param.save()
        self.assertFalse(getParameterValue("TEST_PARAM_BOOLEAN"))
        boolean_param.value = "Fales"  # Wrong spilling of False
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")
        boolean_param.value = "-1"
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")
        boolean_param.value = "2"
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")
        boolean_param.value = "ya"
        boolean_param.save()
        self.assertRaises(ValueError, getParameterValue,
                          "TEST_PARAM_BOOLEAN")

    def test_non_existing_param_in_database_but_exists_in_default_param(self) -> None:
        self.assertEquals(getParameterValue("TEST"), "TEST_PARAMETER")
        self.assertIsInstance(getParameterValue("TEST"), str)


class TestUrls(SimpleTestCase):

    def test_index_is_resolved(self) -> None:
        url: str = reverse(constants.PAGES.INDEX)
        self.assertEquals(resolve(url).func, index)

    def test_about_is_resolved(self) -> None:
        url: str = reverse(constants.PAGES.ABOUT_PAGE)
        self.assertEquals(resolve(url).func, about)

    def test_unauthorized_is_resolved(self) -> None:
        url: str = reverse(constants.PAGES.UNAUTHORIZED_PAGE)
        self.assertEquals(resolve(url).func, unauthorized)

    def test_logout_user_is_resolved(self) -> None:
        url: str = reverse(constants.PAGES.LOGOUT)
        self.assertEquals(resolve(url).func, logoutUser)

    def test_create_user_page_is_resolved(self) -> None:
        url: str = reverse(constants.PAGES.CREATE_USER_PAGE)
        self.assertEquals(resolve(url).func, createUserPage)

    def test_task_is_resolved(self) -> None:
        url: str = reverse(constants.PAGES.TASKS_PAGE)
        self.assertEquals(resolve(url).func, tasks)


class TestUtils(TestCase):

    def setUp(self) -> None:
        self.test_engine_name: str = "Test Engine"
        self.request = HttpRequest()
        self.request.user: User = User.objects.first()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.request.META["REMOTE_ADDR"] = self.test_ip
        self.request.META["HTTP_USER_AGENT"] = self.user_agent

    def test_util_set_created_by_updated_by(self) -> None:
        person: Person = Person.objects.create(
            name="test created updated from utils"
        )
        setCreatedByUpdatedBy(self.test_engine_name, person)
        self.assertEquals(person.created_by,
                          self.test_engine_name)
        self.assertEquals(person.updated_by,
                          self.test_engine_name)
        setCreatedByUpdatedBy("Tester", person, change=True)
        self.assertEquals(person.updated_by, "Tester")
        self.assertEquals(person.created_by,
                          self.test_engine_name)
        setCreatedByUpdatedBy(self.request, person, change=True)
        self.assertEquals(person.updated_by, self.request.user.get_full_name())

    def test_get_user_role(self) -> None:
        role: str = getUserRole(self.request.user)
        self.assertIsNotNone(role)
        self.assertIn(role, constants.ROLES)
        role: str = getUserRole(self.request)
        self.assertIsNotNone(role)
        self.assertIn(role, constants.ROLES)

    def test_get_employee_tasks(self) -> None:
        employee: Employee = Employee.objects.get(account=self.request.user)
        for i in range(5):
            Task.objects.create(employee=employee, task=f"Test Task {i}")
        tasks: QuerySet[Task] = getEmployeesTasks(self.request)
        for i in range(5):
            self.assertEquals(tasks[i].task, f"Test Task {i}")

    def test_get_client_ip(self) -> None:
        self.assertEquals(getClientIp(self.request), self.test_ip)

    def test_get_user_agent(self) -> None:
        self.assertEquals(getUserAgent(self.request), self.user_agent)

    def test_resolve_page_url(self) -> None:
        resolved_url: str = resolvePageUrl(
            self.request, constants.PAGES.DASHBOARD)
        self.assertEquals(resolved_url, self.request.user.groups.all()[
                          0].name + ":" + constants.PAGES.DASHBOARD)


class TestViews(TestCase):

    def setUp(self) -> None:
        self.client = RequestFactory()
        self.test_ip: str = "123.123.123.123"
        self.user_agent: str = "Python"
        self.client.defaults['REMOTE_ADDR'] = self.test_ip
        self.client.defaults['HTTP_USER_AGENT'] = self.user_agent
        self.anonymous_user = AnonymousUser()
        self.logged_superuser_ceo: User = User.objects.first()

    def test_home_page_for_non_authenticated_users(self):
        request: HttpRequest = self.client.get(reverse(constants.PAGES.INDEX))
        request.user = self.anonymous_user
        response: HttpResponse = index(request)
        self.assertEquals(response.status_code, SUCCESS_RESPONSE_STATUS_CODE)

    def test_home_page_for_authenticated_users_and_redirect_them_to_correct_dashboard(self):
        request: HttpRequest = self.client.get(reverse(constants.PAGES.INDEX))
        request.user = self.logged_superuser_ceo
        response: HttpResponse = index(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(
            "CEO:" + constants.PAGES.CEO_DASHBOARD),
            target_status_code=REDIRECT_STATUS_CODE)

        request: HttpRequest = self.client.get(reverse(constants.PAGES.INDEX))
        request.user = self.logged_superuser_ceo
        request.user.groups.clear()
        Group.objects.get(name=constants.ROLES.HUMAN_RESOURCES
                          ).user_set.add(request.user)
        response: HttpResponse = index(request)
        response.client = Client()
        self.assertRedirects(response, reverse(
            "HumanResources:" + constants.PAGES.HUMAN_RESOURCES_DASHBOARD),
            target_status_code=REDIRECT_STATUS_CODE)

        request: HttpRequest = self.client.get(reverse(constants.PAGES.INDEX))
        request.user = self.logged_superuser_ceo
        request.user.groups.clear()
        Group.objects.get(name=constants.ROLES.ACCOUNTING_MANAGER
                          ).user_set.add(request.user)
        response: HttpResponse = index(request)
        response.client = Client()
        self.assertRedirects(response, reverse(
            "AccountingManager:" + constants.PAGES.ACCOUNTING_MANAGER_DASHBOARD),
            target_status_code=REDIRECT_STATUS_CODE)

    def test_about_page(self):
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.ABOUT_PAGE))
        request.user = self.anonymous_user
        response: HttpResponse = about(request)
        self.assertEquals(response.status_code, SUCCESS_RESPONSE_STATUS_CODE)

    def test_unauthorized_page(self):
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.UNAUTHORIZED_PAGE))
        request.user = self.anonymous_user
        response: HttpResponse = unauthorized(request)
        self.assertEquals(response.status_code, SUCCESS_RESPONSE_STATUS_CODE)

    def test_logout_user_page(self):
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.LOGOUT))
        request.user = self.logged_superuser_ceo
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        self.assertTrue(request.user.is_authenticated)
        response: HttpResponse = logoutUser(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertFalse(request.user.is_authenticated)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))

    def test_create_new_user_page(self):
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.CREATE_USER_PAGE))
        request.user = self.logged_superuser_ceo
        response: HttpResponse = createUserPage(request)
        self.assertEquals(response.status_code, SUCCESS_RESPONSE_STATUS_CODE)

        request: HttpRequest = self.client.post(
            reverse(constants.PAGES.CREATE_USER_PAGE), {
                'username': 'TestUserName',
                'email': 'test@test.te',
                'password1': 'VeryHaredPasswordForTE$T',
                'password2': 'VeryHaredPasswordForTE$T'
            })
        request.user = self.logged_superuser_ceo
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        session_middleware = SessionMiddleware(lambda request: None)
        session_middleware.process_request(request)
        request.session.save()
        response: HttpResponse = createUserPage(request)
        response.client = Client()
        self.assertEquals(response.status_code, REDIRECT_STATUS_CODE)
        self.assertRedirects(response, reverse(constants.PAGES.INDEX))
        self.assertEquals(User.objects.last().username, "TestUserName")

    def test_tasks_page(self):
        request: HttpRequest = self.client.get(
            reverse(constants.PAGES.TASKS_PAGE))
        request.user = self.logged_superuser_ceo
        request.user.groups.clear()
        Group.objects.get(name=constants.ROLES.ACCOUNTING_MANAGER
                          ).user_set.add(request.user)
        response: HttpResponse = tasks(request)
        self.assertEquals(response.status_code, SUCCESS_RESPONSE_STATUS_CODE)
