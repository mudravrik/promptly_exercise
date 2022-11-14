import pytest

@pytest.fixture
def questionnaire_value():
    return "test_value"


@pytest.fixture
def questionnaire_choice():
    return "test_choice"