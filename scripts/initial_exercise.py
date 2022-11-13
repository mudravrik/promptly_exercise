import json
from collections import defaultdict

import pandas as pd


df = pd.read_csv('source_data.csv', index_col=0)

birthday_col_nm = 'birthdate'
completed_col_name = 'completed_at'
created_col_name = 'created_at'
updated_col_name = 'updated_at'
event_date_col_name = 'event_date'
assessment_col_name = 'assessment_id'
patient_col_name = 'patient_id'
event_col_name = 'event_id'
institution_col_name = 'institution'

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
df.loc[:, 'answers'] = df.loc[:, 'answers'].apply(lambda val: json.loads(val) if isinstance(val, str) else val)
df = df.loc[df["disease"] == "Cataract", :]
# To check all values are dicts
for val in df.loc[:, 'answers']:
    d_types_dict[type(val)] += 1
assert len(list(d_types_dict.keys())) == 1
df_answers = pd.json_normalize(df['answers'])

def value_choice_extractor(dictionary):
    for key in dictionary.keys():
        if key == 'value':
            return dictionary['value']
        for key in dictionary.keys():
            if key == 'choice':
                return dictionary['choice']
            return pd.NA

df_answers = df_answers.applymap(lambda answer: answer if not isinstance(answer, list)
                                                        else pd.NA if len(answer) == 0
                                                        else value_choice_extractor(answer[0]) if len(answer) == 1
                                                        else ', '.join([str(value_choice_extractor(dictionary)) for dictionary in answer]))

df_answers = df_answers.dropna(axis=1, how='all')
df = df.drop("answers", axis=1)
df = df.join(df_answers)
del df_answers
df = df.loc[df["event_date"] > "2019-06-01", :]
is_assessment_fully_completed = []
for val in df["completed_at"]:
    if pd.isna(val):
        is_assessment_fully_completed.append(False)
    else:
        is_assessment_fully_completed.append(True)
df["is_assessment_fully_completed"] = is_assessment_fully_completed
df = df.loc[df["is_assessment_fully_completed"] == True, :]
df = df.drop(columns="is_assessment_fully_completed")
df.to_csv('processed_data.csv')