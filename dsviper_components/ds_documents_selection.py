from dsviper import ValueKey, Attachment, PathConst

class DSDocumentsSelection:
    def __init__(self, key: ValueKey, attachment: Attachment, path: PathConst):
        self._key = key
        self._attachment = attachment
        self._path = path

    @property
    def key(self) -> ValueKey:
        return self._key

    @property
    def attachment(self) -> Attachment:
        return self._attachment

    @property
    def path(self) -> PathConst:
        return self._path