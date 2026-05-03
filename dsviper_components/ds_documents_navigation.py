from __future__ import annotations

from dsviper import ValueKey, Attachment, PathConst


class DSDocumentsNavigation:
    class Location:
        def __init__(self, key: ValueKey, attachment: Attachment | None, path: PathConst | None):
            self._key = key
            self._attachment = attachment
            self._path = path

        @property
        def key(self) -> ValueKey:
            return self._key

        @key.setter
        def key(self, key: ValueKey):
            self._key = key

        @property
        def attachment(self) -> Attachment:
            return self._attachment

        @attachment.setter
        def attachment(self, attachment: Attachment):
            self._attachment = attachment

        @property
        def path(self) -> PathConst:
            return self._path

        @path.setter
        def path(self, path: PathConst):
            self._path = path

    def __init__(self, key: ValueKey, attachment: Attachment | None, path: PathConst | None):
        location = DSDocumentsNavigation.Location(key, attachment, path)
        self._locations: list[DSDocumentsNavigation.Location] = [location]
        self._current_index = 0

    @property
    def can_go_back(self) -> bool:
        return self._current_index != 0

    def go_back(self):
        self._current_index -= 1

    @property
    def can_go_forward(self):
        return self._current_index < len(self._locations) - 1

    def go_forward(self):
        self._current_index += 1

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_location(self) -> DSDocumentsNavigation.Location:
        return self._locations[self._current_index]

    def push(self, key: ValueKey, attachment: Attachment | None, path: PathConst | None):
        if self._current_index != len(self._locations) - 1:
            self._locations[self._current_index + 1:] = []

        location = DSDocumentsNavigation.Location(key, attachment, path)
        self._locations.append(location)
        self._current_index = len(self._locations) - 1
