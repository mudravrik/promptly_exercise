"""Basic representation of result from some questionary
"""
import dataclasses
from typing import Optional

import pandas as pd


@dataclasses.dataclass
class QuestionnaireResult:
    """Basic representation of result from some questionary

    Has choice and/or value. Both transformed into string, because we have no details
    about what it really is so string is a safer choice.
    Does not have name of questionary inside now because we do not use it,
    but probably should for better encapsulation.
    """

    choice: Optional[str] = None
    value: Optional[str] = None

    def __post_init__(self):
        if self.choice is not None:
            self.choice = str(self.choice)
        if self.value is not None:
            self.value = str(self.value)

    @property
    def answer(self) -> Optional[str]:
        """Get answer from questionary result.

        It may be value, choice or pd.NA if neither presented
        :return: unified answer from questionary
        """
        return self.value or self.choice or pd.NA
