import logging
from typing import List, Union

import pandas as pd

from promptly_exersice.utils import SafeJsonDeserializer

logger = logging.getLogger(__name__)


class DataFrameFormatter:
    @classmethod
    def parce_columns_to_datetime_with_errors_coerce(
        cls, df: pd.DataFrame, input_columns: Union[List[str], str]
    ) -> pd.DataFrame:
        new_df = df.copy()
        columns_to_parse = cls._calculate_column_list_to_parse(new_df, input_columns)
        new_df[columns_to_parse] = new_df[columns_to_parse].apply(
            lambda col: pd.to_datetime(col, errors="coerce")
        )
        return new_df

    @classmethod
    def parce_json_string_columns_to_dicts(cls, df: pd.DataFrame, input_columns: Union[List[str], str]) -> pd.DataFrame:
        new_df = df.copy()
        columns_to_parse = cls._calculate_column_list_to_parse(new_df, input_columns)
        new_df[columns_to_parse] = new_df[columns_to_parse].applymap(
            SafeJsonDeserializer.safe_deserialize_json_to_dict
        )
        return new_df

    @classmethod
    def parce_columns_to_int(cls, df: pd.DataFrame, input_columns: Union[List[str], str]):
        """Parse columns from df into Int64Dtype

        :param df: Pandas df with columns to convert
        :param input_columns: list of column names to parse
        :raise ValueError when cannot parse into int correctly
        :return: new df with modified columns
        """
        try:
            return cls._parse_columns_to_type(df, input_columns, pd.Int64Dtype())
        except ValueError as err:
            logger.error("Unable to parse value to int in %s - %s", input_columns, err)
            raise err

    @classmethod
    def parce_columns_to_string(cls, df: pd.DataFrame, input_columns: Union[List[str], str]):
        """Parse columns from df into StringDtype

        :param df: Pandas df with columns to convert
        :param input_columns: list of column names to parse
        :raise ValueError when cannot parse into string correctly
        :return: new df with modified columns
        """
        try:
            return cls._parse_columns_to_type(df, input_columns, pd.StringDtype())
        except ValueError as err:
            logger.error("Unable to parse value to string in %s - %s", input_columns, err)
            raise err

    @classmethod
    def _parse_columns_to_type(
        cls, df: pd.DataFrame, input_columns: Union[List[str], str], new_type: pd.api.extensions.ExtensionDtype
    ):
        new_df = df.copy()
        columns_to_parse = cls._calculate_column_list_to_parse(new_df, input_columns)
        new_df[columns_to_parse] = new_df[columns_to_parse].astype(new_type)
        return new_df

    @staticmethod
    def _calculate_column_list_to_parse(
        df: pd.DataFrame, input_columns: Union[List[str], str]
    ) -> List[str]:
        df_column_names = df.columns
        if isinstance(input_columns, str):
            input_columns = [input_columns]
        unique_input_columns = set(input_columns)
        unique_columns_to_parse = [
            column for column in unique_input_columns if column in df_column_names
        ]
        unknown_columns = unique_input_columns.difference(unique_columns_to_parse)
        if unknown_columns:
            logger.warning(
                "Some input columns were not found in df: %s", unknown_columns
            )
        return list(unique_columns_to_parse)
