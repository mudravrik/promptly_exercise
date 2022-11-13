import dataclasses
from typing import Optional, Union

import pandas as pd


@dataclasses.dataclass
class QuestionaryResult:
    choice: Optional[str] = None
    value: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.choice, str):
            self.choice = str(self.choice)
        if not isinstance(self.value, str):
            self.value = str(self.value)

    @property
    def answer(self) -> Optional[Union[str, float]]:
        return self.value or self.choice or pd.NA
