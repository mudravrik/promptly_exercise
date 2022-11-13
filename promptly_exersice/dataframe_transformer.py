"""Tool to perform generic transformation of DataFrame
"""
import logging
from typing import List, Union

import pandas as pd

from promptly_exersice.utils import JsonDeserializer

logger = logging.getLogger(__name__)


class DataFrameTransformer:
    """Set of method to perform transformation of generic DataFrame

    All methods of class do not change input object and return copy of it!

    Making most of the methods a classmethod is not common
    because usually we will pass some settings into transformer.
    But in this exact case it actually works since our classes can pretend to be
    singletones and does not require any inputs.
    So we can just skip initialization in script and just use class method
    like functions from closed namespace when details of implementation is hidden in
    private methods.
    """

    @classmethod
    def parse_columns_to_datetime_with_errors_coerce(
        cls, df: pd.DataFrame, input_columns: Union[List[str], str]
    ) -> pd.DataFrame:
        """Parse various datetimes into actual datetime object.

        Ignore errors like pd.to_datetime(x, errors="coerce")

        :param df: Dataframe with columns to be transformed
        :param input_columns: Column name(s) to be transformed
        :return: DataFrame with columns parsed
        """
        new_df = df.copy()
        columns_to_parse = cls._calculate_column_list_to_parse(new_df, input_columns)
        new_df[columns_to_parse] = new_df[columns_to_parse].applymap(
            lambda x: pd.to_datetime(x, errors="coerce")
        )
        return new_df

    @classmethod
    def parce_json_columns_to_dicts(
        cls, df: pd.DataFrame, input_columns: Union[List[str], str]
    ) -> pd.DataFrame:
        """Convert set of columns with json inside into columns with dicts inside

        :param df: Dataframe with columns to be transformed
        :param input_columns: Column name(s) to be transformed
        :return: DataFrame with columns parsed
        :raise: DeserializationResultIsNotDictException in case when result is not a dict
        """
        new_df = df.copy()
        columns_to_parse = cls._calculate_column_list_to_parse(new_df, input_columns)
        new_df[columns_to_parse] = new_df[columns_to_parse].applymap(
            JsonDeserializer.deserialize_json_to_dict
        )
        return new_df

    @classmethod
    def parce_columns_to_int(
        cls, df: pd.DataFrame, input_columns: Union[List[str], str]
    ):
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
    def parce_columns_to_string(
        cls, df: pd.DataFrame, input_columns: Union[List[str], str]
    ):
        """Parse columns from df into StringDtype

        :param df: Pandas df with columns to convert
        :param input_columns: list of column names to parse
        :raise ValueError when cannot parse into string correctly
        :return: new df with modified columns
        """
        try:
            return cls._parse_columns_to_type(df, input_columns, pd.StringDtype())
        except ValueError as err:
            logger.error(
                "Unable to parse value to string in %s - %s", input_columns, err
            )
            raise err

    @classmethod
    def _parse_columns_to_type(
        cls,
        df: pd.DataFrame,
        input_columns: Union[List[str], str],
        new_type: pd.api.extensions.ExtensionDtype,
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
