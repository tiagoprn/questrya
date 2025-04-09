"""
Fixtures must be manually registered on questrya/conftest.py
"""

from typing import Dict

import pytest

from questrya.common.value_objects.email import Email


@pytest.fixture
def domain_user_data_picard() -> Dict:
    return {
        'username': 'picard',
        'email': Email('jean_luc_picard@enterprise.org'),
        'password': '12345678',
    }
