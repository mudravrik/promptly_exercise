import json
from collections import defaultdict

import pandas as pd

# ** change path for easier tests
# it would be better to move path to some constant for easier change
# and future parametrization
df = pd.read_csv("resources/source_data.csv", index_col=0)

# these variables are used only ones during the script,
# what the purpose of creating so much of them?
# maybe we can just create list with "similar" columns and apply functions over the list
birthday_col_nm = "birthdate"
completed_col_name = "completed_at"
created_col_name = "created_at"
updated_col_name = "updated_at"
event_date_col_name = "event_date"
assessment_col_name = "assessment_id"
patient_col_name = "patient_id"
event_col_name = "event_id"
institution_col_name = "institution"

# there is no need to repeat the same command, just use Dataframe.applymap()
df[birthday_col_nm] = pd.to_datetime(df[birthday_col_nm], errors="coerce")
df[completed_col_name] = pd.to_datetime(df[completed_col_name], errors="coerce")
df[created_col_name] = pd.to_datetime(df[created_col_name], errors="coerce")
df[event_date_col_name] = pd.to_datetime(df[event_date_col_name], errors="coerce")
df[updated_col_name] = pd.to_datetime(df[updated_col_name], errors="coerce")
df[assessment_col_name] = df[assessment_col_name].astype(pd.Int64Dtype())
df[patient_col_name] = df[patient_col_name].astype(pd.Int64Dtype())
df[event_col_name] = df[event_col_name].astype(pd.Int64Dtype())
df[institution_col_name] = df[institution_col_name].astype(pd.Int64Dtype())
d_types_dict = defaultdict(lambda: 0)
# this way of "safe" parsing is not so safe, we still can get malformed string or
# pd.NA values which gonna break the code
df.loc[:, "answers"] = df.loc[:, "answers"].apply(
    lambda val: json.loads(val) if isinstance(val, str) else val
)
df = df.loc[df["disease"] == "Cataract", :]

# well, that`s pretty cryptic way to check if every value in Series is of some type.
# it is hard to read and actually does not guarantee that all value are dicts,
# just that all of them are the same type
# using Series.all() with isinstance() looks so better here
# To check all values are dicts
for val in df.loc[:, "answers"]:
    d_types_dict[type(val)] += 1
assert len(list(d_types_dict.keys())) == 1

# There was a bug, which essentially resulted in corrupted result.
# Using json_normalize() erase index from df, but after a couple of steps
# we join the result with default "by-index" way. This lead to joining incorrect
# answers to every patient. So fixing it right here is pretty easy - we need to bring
# indexes back to answers.
# But the more complicated questions is how to prevent such errors in future?
# We can reduce using pandas in "prod" transformation, because it is pretty
# non-restrictive about possible mistakes and tends to quietly make some under-the-hood
# operation and conversions.
# Also it is very useful to bring some testing into the play - at the level of some
# basic transformation step as well e2e-test comparing to expected result, if speaking
# about pure data transformation.
# ** btw fix the error to make script result testable
df_answers = pd.json_normalize(df["answers"]).set_index(df.index)

# Overall naming does not look good. Ie in this function:
# - function should be named with verbs
# - argument name does not mean anything
# - argument names should avoid having type reference in them
# - typing is totally missed
def value_choice_extractor(dictionary):
    for key in dictionary.keys():
        # dict.get() will be an easier way to go
        if key == "value":
            return dictionary["value"]
        # what the purpose of this cycle here?
        for key in dictionary.keys():
            if key == "choice":
                return dictionary["choice"]
            return pd.NA


# This lambda with multiple if-else is so hard to read and understand.
# Such complex functions with tons of business logic should definitely be
# a separate function with proper testing
df_answers = df_answers.applymap(
    lambda answer: answer
    if not isinstance(answer, list)
    else pd.NA
    if len(answer) == 0
    else value_choice_extractor(answer[0])
    if len(answer) == 1
    else ", ".join([str(value_choice_extractor(dictionary)) for dictionary in answer])
)

df_answers = df_answers.dropna(axis=1, how="all")
df = df.drop("answers", axis=1)
df = df.join(df_answers)
del df_answers
# first of all moving threshold to constant would be a great idea to make support easier
# another issue with this is the fact that filtering rows is done after filtering column.
# So we can still end up with columns consisting only of pd.NA values,
# because we filtered out all rows with non-empty values after we check the column for
# have it.
# But without actual task presented I`m can be sure if this intended or not,
# thus I left the filtration here.

df = df.loc[df["event_date"] > "2019-06-01", :]

# This filtration is over-complicated,
# it is virtually just filtering all rows with missing values in completed_at
# so why not use it?
is_assessment_fully_completed = []
for val in df["completed_at"]:
    if pd.isna(val):
        is_assessment_fully_completed.append(False)
    else:
        is_assessment_fully_completed.append(True)
df["is_assessment_fully_completed"] = is_assessment_fully_completed
# btw comparing with True is useless in python :)
df = df.loc[df["is_assessment_fully_completed"] == True, :]
df = df.drop(columns="is_assessment_fully_completed")

# again, file path better to be moved to constant
# **chainged it a bit in purpose of testing
df.to_csv("results/old_processed_data.csv")
