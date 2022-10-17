from collections import namedtuple as _namedtuple


MAIN_STORAGE_ID: int = 1
PAGINATE_BY: int = 10

CHOICES = _namedtuple('tuple', [
    'COUNTRY',
    'GENDER'
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
