import pytest
from uuid import uuid4

from questrya.common.value_objects.email import Email, InvalidEmailError


class TestEmail:
    @pytest.mark.parametrize('email',
        [
            'abc',
            'abc@def',
            'abc.def',
            '.def',
        ],
    )
    def test_email_must_be_invalid(self, email):
        with pytest.raises(InvalidEmailError) as _:
            _ = Email(address=email)

    @pytest.mark.parametrize('email',
        [
            'JEANLUC@google.com',
            'JEANLUC@GOOGLE.COM',
            'JeAn-LuC@google.COM',
            'jean_luc@GOOGLE.com',
        ],
    )
    def test_email_must_be_valid(self, email):
        email_instance = Email(address=email)
        assert email_instance.address == email.lower()

    @pytest.mark.parametrize('email',
        [
            'JEANLUC@google.com',
            'JEANLUC@GOOGLE.COM',
            'JeAn-LuC@google.COM',
            'jean_luc@GOOGLE.com',
        ],
    )
    def test_email_difference(self, email):
        email_instance = Email(address=email)
        assert email_instance.address != email

    @pytest.mark.parametrize('email',
        [
            'JEANLUC@google.com',
            'JEANLUC@GOOGLE.COM',
            'JeAn-LuC@google.COM',
            'jean_luc@GOOGLE.com',
        ],
    )
    def test_email_as_string(self, email):
        email_instance = Email(address=email)
        assert str(email_instance) == email.lower()

    @pytest.mark.parametrize('email',
        [
            'JEANLUC@google.com',
            'JEANLUC@GOOGLE.COM',
            'JeAn-LuC@google.COM',
            'jean_luc@GOOGLE.com',
        ],
    )
    def test_email_repr(self, email):
        email_instance = Email(address=email)
        assert repr(email_instance) == f"Email('{email.lower()}')"
