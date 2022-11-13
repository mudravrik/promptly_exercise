import pandas as pd

from promptly_exersice.dataframe_formatter import DataFrameFormatter
from promptly_exersice.handlers.questionary_answer_handler import (
    QuestionaryResultHandler,
)

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
OUTPUT_PATH = "results/processed_data.csv"

df = pd.read_csv("resources/source_data.csv", index_col=0)

# move filtration earlier in the script to reduce number of rows and error chance
df = df[df["disease"] == DISEASE_OF_INTEREST]
df = df[df["event_date"] > EARLIEST_EVENT_THRESHOLD]
df = df[~pd.isna(df["completed_at"])]  # pylint: disable=invalid-unary-operand-type

df = DataFrameFormatter.parce_columns_to_datetime_with_errors_coerce(
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
df = DataFrameFormatter.parce_columns_to_string(df, ID_COLUMNS)
df = DataFrameFormatter.parce_json_string_columns_to_dicts(df, "answers")
df_answers = pd.json_normalize(df["answers"])

df_answers = df_answers.applymap(
    QuestionaryResultHandler.safe_get_answers_from_json_deserialization_result
)

df_answers = df_answers.dropna(axis=1, how="all")
df = df.drop(columns=["answers"])
df = df.join(df_answers)
del df_answers
df.to_csv(OUTPUT_PATH)
