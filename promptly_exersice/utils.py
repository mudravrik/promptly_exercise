import json
import logging
from json import JSONDecodeError

logger = logging.getLogger(__name__)


class ParsedResultIsNotDictException(Exception):
    def __init__(self, message):
        super().__init__(message)


class SafeJsonDeserializer:
    @classmethod
    def safe_deserialize_json_to_dict(cls, input_string):
        parsed_object = cls._safe_json_parse(input_string)
        if not isinstance(parsed_object, dict):
            raise ParsedResultIsNotDictException(
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
