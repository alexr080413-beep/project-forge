from __future__ import annotations

from dataclasses import dataclass, field

from .models import TranslationDictionary
from .validator import TranslationValidator


@dataclass(slots=True)
class TranslationRegistry:
    """In-memory registry for validated translation dictionaries."""

    dictionaries: list[TranslationDictionary] = field(default_factory=list)
    validator: TranslationValidator = field(default_factory=TranslationValidator)

    def __post_init__(self) -> None:
        self._validate_unique_dictionaries()
        for dictionary in self.dictionaries:
            self.validator.validate_dictionary(dictionary)

    def register_dictionary(self, dictionary: TranslationDictionary) -> None:
        if self.get_dictionary(dictionary.identifier) is not None:
            raise ValueError(f"dictionary identifier already exists: {dictionary.identifier}")
        self.validator.validate_dictionary(dictionary)
        self.dictionaries.append(dictionary)
        self.dictionaries.sort(key=lambda item: item.identifier)

    def get_dictionary(self, identifier: str) -> TranslationDictionary | None:
        for dictionary in self.dictionaries:
            if dictionary.identifier == identifier:
                return dictionary
        return None

    def _validate_unique_dictionaries(self) -> None:
        identifiers = [dictionary.identifier for dictionary in self.dictionaries]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("translation dictionary identifiers must be unique")
