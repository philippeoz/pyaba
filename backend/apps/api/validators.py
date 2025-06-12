"""Validators for various data formats."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def cpf_is_valid(cpf):
    """
    Validates a Brazilian CPF number.
    A valid CPF must contain 11 digits and follow the Brazilian CPF rules.
    """
    cpf = "".join(filter(str.isdigit, cpf))

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    first_digit_sum = sum(int(cpf[number]) * (10 - number) for number in range(9))
    if ((first_digit_sum * 10 % 11) % 10) != int(cpf[9]):
        return False

    second_digit_sum = sum(int(cpf[number]) * (11 - number) for number in range(10))
    if ((second_digit_sum * 10 % 11) % 10) != int(cpf[10]):
        return False

    return True


def cpf_validator(value):
    """
    Validates if the provided CPF is valid.
    """
    if not cpf_is_valid(value):
        raise ValueError(_("CPF inválido. Deve conter 11 dígitos e ser válido segundo as regras brasileiras."))
    return value
