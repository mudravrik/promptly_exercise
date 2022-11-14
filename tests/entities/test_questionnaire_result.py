import pandas as pd
import pytest

from promptly_exersice.entities.questionnaire_result import QuestionnaireResult


@pytest.fixture
def float_questionnaire_field():
    return 42.42


def test_questionnaire_result_choice_if_non_string_given(float_questionnaire_field):
    test_quest = QuestionnaireResult(
        value=float_questionnaire_field, choice=float_questionnaire_field
    )
    assert test_quest.value == str(float_questionnaire_field)
    assert test_quest.choice == str(float_questionnaire_field)


def test_questionnaire_result_choice_if_zero_given():
    test_quest = QuestionnaireResult(choice=0, value=0)
    assert test_quest.value == "0"
    assert test_quest.choice == "0"
    assert test_quest.answer == "0"


def test_questionnaire_result_answer_when_value_and_choice_presented(
    questionnaire_choice, questionnaire_value
):
    test_quest = QuestionnaireResult(
        value=questionnaire_value, choice=questionnaire_choice
    )
    assert test_quest.answer == questionnaire_value


def test_questionnaire_result_answer_when_only_value_presented(questionnaire_value):
    test_quest = QuestionnaireResult(value=questionnaire_value)
    assert test_quest.answer == questionnaire_value


def test_questionnaire_result_answer_when_only_choice_presented(questionnaire_choice):
    test_quest = QuestionnaireResult(choice=questionnaire_choice)
    assert test_quest.answer == questionnaire_choice


def test_questionnaire_result_answer_when_neither_choice_nor_value_presented():
    test_quest = QuestionnaireResult()
    assert pd.isna(test_quest.answer)
