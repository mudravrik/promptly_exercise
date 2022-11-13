"""Various utils
"""
import json
import logging
import os
from json import JSONDecodeError
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class DeserializationResultIsNotDictException(Exception):
    """Custom exception for cases when dict had been expected from json
    but did not appear
    """

    def __init__(self, message):
        super().__init__(message)


# pylint: disable=too-few-public-methods
class JsonDeserializer:
    """Set of methods to deserialize json-s in different cases"""

    @classmethod
    def deserialize_json_to_dict(cls, json_input: str) -> Dict:
        """Deserialize json only to dict or throw an exception

        :param: json_input: json to be deserialized
        :return: Resulted dict
        :raise: DeserializationResultIsNotDictException in case when result is not a dict
        """
        parsed_object = cls._safe_json_parse(json_input)
        if not isinstance(parsed_object, dict):
            raise DeserializationResultIsNotDictException(
                f"Deserialization result {parsed_object} is not a dict:"
            )
        return parsed_object

    @staticmethod
    def _safe_json_parse(input_string):
        try:
            parsed_json = json.loads(input_string)
        except JSONDecodeError:
            logger.error("Input string %s is not-parsable to json", input_string)
            parsed_json = input_string
        except TypeError:
            logger.error("Input is not a string, but %s", type(input_string))
            parsed_json = input_string
        return parsed_json


class PathHandler:
    """Basic tool for safe work with paths"""
    @staticmethod
    def create_path_from_dir_and_filename(dir_path: str, filename: str) -> Path:
        """Create Path from path to directory and filename.

        Also making sure folder exists or creates it.
        """
        dir_path = Path(dir_path)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        fullname = dir_path / filename
        return fullname
