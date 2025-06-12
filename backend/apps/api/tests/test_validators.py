import pytest
from apps.api.validators import cpf_is_valid, cpf_validator


@pytest.mark.parametrize(
    "cpf",
    [
        "529.982.247-25",  # valid formatted
        "52998224725",  # valid unformatted
        "12345678909",  # valid
    ],
)
def test_cpf_is_valid_valid_cases(cpf):
    assert cpf_is_valid(cpf) is True


@pytest.mark.parametrize(
    "cpf",
    [
        "111.111.111-11",  # repeated digits
        "22222222222",  # repeated digits
        "12345678900",  # invalid check digits
        "5299822472",  # too short
        "529982247252",  # too long
        "abcdefghijk",  # non-numeric
        "",  # empty
    ],
)
def test_cpf_is_valid_invalid_cases(cpf):
    assert cpf_is_valid(cpf) is False


@pytest.mark.parametrize(
    "cpf",
    [
        "529.982.247-25",
        "52998224725",
        "12345678909",
    ],
)
def test_cpf_validator_valid(cpf):
    assert cpf_validator(cpf) == cpf


@pytest.mark.parametrize(
    "cpf",
    [
        "111.111.111-11",
        "22222222222",
        "12345678900",
        "5299822472",
        "529982247252",
        "abcdefghijk",
        "",
    ],
)
def test_cpf_validator_invalid(cpf):
    with pytest.raises(ValueError):
        cpf_validator(cpf)
