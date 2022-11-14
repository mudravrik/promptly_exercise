import logging

import pandas as pd
import pytest

from promptly_exersice.handlers.questionnaire_result_handler import (
    QuestionnaireResultHandler,
)


@pytest.fixture
def deser_json_with_single_result(questionnaire_value, questionnaire_choice):
    return [{"choice": questionnaire_choice, "value": questionnaire_value}]


@pytest.fixture
def deser_json_with_multiple_results(questionnaire_value, questionnaire_choice):
    return [
        {"choice": questionnaire_choice, "value": questionnaire_value},
        {"value": questionnaire_value},
    ]


@pytest.fixture
def deser_json_with_empty_result():
    return [{}]


def test_get_str_answers_from_deserialized_json_when_result_is_single(
    deser_json_with_single_result, questionnaire_value
):
    result = QuestionnaireResultHandler.get_str_answers_from_deserialized_json(
        deser_json_with_single_result
    )
    assert result == questionnaire_value


def test_get_str_answers_from_deserialized_json_when_result_is_empty(
    deser_json_with_empty_result
):
    result = QuestionnaireResultHandler.get_str_answers_from_deserialized_json(
        deser_json_with_empty_result
    )
    assert pd.isna(result)


def test_get_str_answers_from_deserialized_json_when_multiple_result(
    deser_json_with_multiple_results, questionnaire_value
):
    result = QuestionnaireResultHandler.get_str_answers_from_deserialized_json(
        deser_json_with_multiple_results
    )
    # both results have value, expecting "%value%, %value%"
    assert result == f"{questionnaire_value}, {questionnaire_value}"


def test_get_str_answers_from_deserialized_json_when_result_is_na(caplog):
    result = QuestionnaireResultHandler.get_str_answers_from_deserialized_json(pd.NA)
    assert len(caplog.records) == 0
    assert pd.isna(result)


def test_get_str_answers_from_deserialized_json_when_result_invalid(caplog):
    with caplog.at_level(logging.INFO):
        result = QuestionnaireResultHandler.get_str_answers_from_deserialized_json("foo")
        assert len(caplog.records) == 1
        assert "Unknown input for QuestionnaireResult" in caplog.records[0].msg
        assert result == "foo"
