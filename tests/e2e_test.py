import pandas as pd
import pytest

# Well, that is very-very lazy way to run scripts and generate result for comparison
# the proper way should be creating some small test dataset, converting scripts to
# something like tasks, which can be parametrized with input data and then comparing
# the result.
# Or ideally we should not compare new result to old, but to some "gold-standard",
# which  we actually expect from the script. But in this case we do not have
# even description of the task to create e2e-tests from it and run tests against.

import scripts.exercise_refactored
import scripts.initial_exercise


@pytest.fixture(scope="session")
def old_result() -> pd.DataFrame:
    return pd.read_csv("results/old_processed_data.csv", index_col=0)


@pytest.fixture(scope="session")
def new_result() -> pd.DataFrame:
    return pd.read_csv("results/new_processed_data.csv", index_col=0)


def test_results_have_same_shape(old_result, new_result):
    assert old_result.shape == new_result.shape


def test_result_have_same_column_names(old_result, new_result):
    assert set(old_result.columns).difference(set(new_result.columns)) == set()


def test_every_column_is_same(old_result, new_result):
    for column in old_result.columns:
        # Series.eq(fill_value=) does not work
        # if both sides missing value at the same place,
        # so replace missing manually
        old_filled_col = old_result[column].fillna("missing")
        new_filled_col = new_result[column].fillna("missing")
        comparison_result = old_filled_col.eq(new_filled_col)
        assert comparison_result.all()
