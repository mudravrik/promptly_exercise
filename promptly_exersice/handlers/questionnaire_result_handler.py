"""Handler to support operations with QuestionaryAnswer class
"""
import logging
from typing import Union, Dict, List, Any

import pandas as pd
from pandas._libs.missing import NAType  # pylint: disable=no-name-in-module

from promptly_exersice.entities.questionnaire_result import QuestionnaireResult

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class QuestionnaireResultHandler:
    """Handler to perform various operations with data about questionary answers.

    We probably should split it further into builder and actual handler and
    maybe make it more suitable for inheritance.
    But without deeper understanding of other use-cases
    it actually worthless and too theoretical
    """

    @classmethod
    def get_str_answers_from_deserialized_json(
        cls, deserialized_input: Any
    ) -> Union[str, NAType, Any]:
        """Transform object which supposed to be questionnaire answers to "standard"
        string-formed shape.

        Standard - in terms of starting code. I don`t actually think
        this form with concatenation is useful
        for further analysis.
        :param: deserialized_input: result of deserialization of json with answers,
            expected format is list of dicts
        :return: Transformed string
        if input was actually json with results of questionary,
        pd.NA if the result was empty or not presented
        or the input if there was some unexpected
        """
        if not isinstance(deserialized_input, list):
            if not pd.isna(deserialized_input):
                logger.info(
                    "Unknown input for QuestionnaireResult: %s, check data upstream!",
                    deserialized_input,
                )
            return deserialized_input
        if not deserialized_input:
            return pd.NA
        return cls._get_answers_from_list_of_dicts(deserialized_input)

    @classmethod
    def _get_answers_from_list_of_dicts(
        cls, list_of_dicts: List[Dict[str, Union[float, str]]]
    ) -> Union[str, NAType]:
        results = cls._create_results_from_list_of_dicts(list_of_dicts)
        return cls._get_concatenated_answers_from_results(results)

    @staticmethod
    def _get_concatenated_answers_from_results(
        results: List[QuestionnaireResult],
    ) -> Union[str, NAType]:
        answers = [result.answer for result in results if not pd.isna(result.answer)]
        if answers:
            return ", ".join(answers)
        else:
            return pd.NA

    @classmethod
    def _create_results_from_list_of_dicts(
        cls, list_of_dicts: List[Dict[str, Union[float, str]]]
    ) -> List[QuestionnaireResult]:
        return [
            cls._create_questionary_result_from_dict(result) for result in list_of_dicts
        ]

    @staticmethod
    def _create_questionary_result_from_dict(
        result: Dict[str, Union[float, str]]
    ) -> QuestionnaireResult:
        return QuestionnaireResult(**result)
