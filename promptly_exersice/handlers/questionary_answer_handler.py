from typing import Union, Dict, List, Any

import pandas as pd
from pandas._libs.missing import NAType

from promptly_exersice.entities.questionary_answer import QuestionaryResult


class QuestionaryResultHandler:
    @classmethod
    def safe_get_answers_from_json_deserialization_result(
        cls, deserialized_input: Any
    ) -> Union[str, NAType, Any]:
        if not isinstance(deserialized_input, list):
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
        results: List[QuestionaryResult],
    ) -> Union[str, NAType]:
        answers = [result.answer for result in results]
        return ", ".join(answers)

    @classmethod
    def _create_results_from_list_of_dicts(
        cls, list_of_dicts: List[Dict[str, Union[float, str]]]
    ) -> List[QuestionaryResult]:
        return [cls._create_result_from_dict(result) for result in list_of_dicts]

    @staticmethod
    def _create_result_from_dict(
        result: Dict[str, Union[float, str]]
    ) -> QuestionaryResult:
        return QuestionaryResult(**result)
