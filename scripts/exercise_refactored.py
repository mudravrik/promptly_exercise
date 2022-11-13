"""Refactored script for cleaning Cataract questionnaires result data"""
import pandas as pd

from promptly_exersice.dataframe_transformer import DataFrameTransformer
from promptly_exersice.handlers.questionnaire_result_handler import (
    QuestionnaireResultHandler,
)
from promptly_exersice.utils import PathHandler

DISEASE_OF_INTEREST = "Cataract"
DATETIME_COLUMNS = [
    "birthdate",
    "completed_at",
    "created_at",
    "updated_at",
    "event_date",
]
ID_COLUMNS = ["assessment_id", "patient_id", "event_id", "institution"]
EARLIEST_EVENT_THRESHOLD = "2019-06-01"

INPUT_FILE = "resources/source_data.csv"

OUTPUT_DIR = "results"
OUTPUT_FILE = "new_processed_data.csv"

df = pd.read_csv(INPUT_FILE, index_col=0)

# move filtration earlier in the script to reduce number of rows and error chance
df = df[df["disease"] == DISEASE_OF_INTEREST]

df = DataFrameTransformer.parse_columns_to_datetime_with_errors_coerce(
    df, DATETIME_COLUMNS
)

# in initial script ids were parsed into INT,
# but in general it is a bad design idea for multiple reason:
# - id can be non-int by nature (UUID for example)
#       and we should be able to handle it still
# - INT implies comparison like greater/less and math operation,
#       but for IDs such operations are meaningless
#       and we better protect users from doing it
# and so on, so lets go for basic string for ids
df = DataFrameTransformer.parce_columns_to_string(df, ID_COLUMNS)
df = DataFrameTransformer.parce_json_columns_to_dicts(df, "answers")

# index in pandas is pure pain! So preserve this low-level operation in demo purpose on
# top level of logic, but better to create index-safe method in transformer for future
df_answers = pd.json_normalize(df["answers"]).set_index(df.index)

df_answers = df_answers.applymap(
    QuestionnaireResultHandler.get_str_answers_from_deserialized_json
)

df_answers = df_answers.dropna(axis=1, how="all")
df = df.drop(columns=["answers"])
df = df.join(df_answers)

# I don`t feel this del very useful since it happens right before the end of the script
# but leave it just in case of some huge memory consumption on write step
del df_answers
df = df[df["event_date"] > EARLIEST_EVENT_THRESHOLD]
df = df[~pd.isna(df["completed_at"])]  # pylint: disable=invalid-unary-operand-type
full_output_path = PathHandler.create_path_from_dir_and_filename(
    OUTPUT_DIR, OUTPUT_FILE
)
df.to_csv(full_output_path)
