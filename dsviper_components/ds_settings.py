from __future__ import annotations

from PySide6.QtCore import QSettings

from .ds_commit_synchronization_source import DSCommitSynchronizationSource
from dsviper import CommitDatabasing, CommitDatabaseSQLite, CommitDatabaseRemote, CommitSynchronizer


class DSSettings:
    def __init__(self):
        self._settings = QSettings()

    @property
    def python_script(self) -> str:
        return self._value_str("DSSettingsPythonScript")

    @python_script.setter
    def python_script(self, value: str):
        self._settings.setValue("DSSettingsPythonScript", value)

    @property
    def python_font_size(self) -> int:
        return self._value_int("DSSettingsPythonFontSize")

    @python_font_size.setter
    def python_font_size(self, value: int):
        self._settings.setValue("DSSettingsPythonFontSize", value)

    @property
    def reopen_last_file(self) -> bool:
        return self._value_bool("DSSettingsReopenLastFile")

    @reopen_last_file.setter
    def reopen_last_file(self, value: bool):
        self._settings.setValue("DSSettingsReopenLastFile", value)

    @property
    def last_file_url(self) -> str:
        return self._value_str("DSSettingsLastFileURL")

    @last_file_url.setter
    def last_file_url(self, value: str):
        self._settings.setValue("DSSettingsLastFileURL", value)

    @property
    def connect_hostname(self) -> str:
        return self._value_str("DSSettingsConnectHost")

    @connect_hostname.setter
    def connect_hostname(self, value: str):
        self._settings.setValue("DSSettingsConnectHost", value)

    @property
    def connect_service(self) -> str:
        return self._value_str("DSSettingsConnectService")

    @connect_service.setter
    def connect_service(self, value: str):
        self._settings.setValue("DSSettingsConnectService", value)

    @property
    def connect_socket_path(self) -> str:
        return self._value_str("DSSettingsConnectSocketPath")

    @connect_socket_path.setter
    def connect_socket_path(self, value: str):
        self._settings.setValue("DSSettingsConnectSocketPath", value)

    @property
    def connect_use_socket_path(self) -> bool:
        return self._value_bool("DSSettingsConnectUseSocketPath")

    @connect_use_socket_path.setter
    def connect_use_socket_path(self, value: bool):
        self._settings.setValue("DSSettingsConnectUseSocketPath", value)

    @property
    def sync_source(self) -> int:
        return self._value_int("DSSettingsSyncSource")

    @sync_source.setter
    def sync_source(self, value: int):
        self._settings.setValue("DSSettingsSyncSource", value)

    @property
    def sync_hostname(self) -> str:
        return self._value_str("DSSettingsSyncHostname")

    @sync_hostname.setter
    def sync_hostname(self, value: str):
        self._settings.setValue("DSSettingsSyncHostname", value)

    @property
    def sync_service(self) -> str:
        return self._value_str("DSSettingsSyncService")

    @sync_service.setter
    def sync_service(self, value: str):
        self._settings.setValue("DSSettingsSyncService", value)

    @property
    def sync_socket_path(self) -> str:
        return self._value_str("DSSettingsSyncSocketPath")

    @sync_socket_path.setter
    def sync_socket_path(self, value: str):
        self._settings.setValue("DSSettingsSyncSocketPath", value)

    @property
    def sync_file_path(self) -> str:
        return self._value_str("DSSettingsSyncFilePath")

    @sync_file_path.setter
    def sync_file_path(self, value: str):
        self._settings.setValue("DSSettingsSyncFilePath", value)

    @property
    def live_update_interval(self) -> int:
        return self._value_int("DSSettingsLiveUpdateInterval")

    @live_update_interval.setter
    def live_update_interval(self, value):
        self._settings.setValue("DSSettingsLiveUpdateInterval", value)

    @property
    def live_sync_with_source(self) -> bool:
        return self._value_bool("DSSettingsLiveSyncWithSource")

    @live_sync_with_source.setter
    def live_sync_with_source(self, value: bool):
        self._settings.setValue("DSSettingsLiveSyncWithSource", value)

    def register_default(self):
        if self._settings.value("DSSettingsPythonScript") is None:
            self.python_script = "playground"

        if self._settings.value("DSSettingsPythonFontSize") is None:
            self.python_font_size = 12

        if self._settings.value("DSSettingsLastFileURL") is None:
            self.last_file_url = ""

        if self._settings.value("DSSettingsReopenLastFile") is None:
            self.reopen_last_file = False

        if self._settings.value("DSSettingsConnectHost") is None:
            self.connect_hostname = "localhost"

        if self._settings.value("DSSettingsConnectService") is None:
            self.connect_service = "54321"

        if self._settings.value("DSSettingsConnectSocketPath") is None:
            self.connect_socket_path = "/tmp/commit.sock"

        if self._settings.value("DSSettingsConnectUseSocketPath") is None:
            self.connect_use_socket_path = False

        if self._settings.value("DSSettingsSyncSource") is None:
            self.sync_source = 0

        if self._settings.value("DSSettingsSyncHostname") is None:
            self.sync_hostname = "localhost"

        if self._settings.value("DSSettingsSyncService") is None:
            self.sync_service = "54321"

        if self._settings.value("DSSettingsSyncFilePath") is None:
            self.sync_file_path = ""

        if self._settings.value("DSSettingsSyncSocketPath") is None:
            self.sync_socket_path = "/tmp/commit.sock"

        if self._settings.value("DSSettingsLiveUpdateInterval") is None:
            self.live_update_interval = 5

        if self._settings.value("DSSettingsLiveSyncWithSource") is None:
            self.live_sync_with_source = False

        self._settings.sync()

    def has_source_of_synchronization(self) -> bool:
        return self.sync_source != 0

    def create_synchronizer(self, mode: str, target_path: str) -> CommitSynchronizer | None:
        s_source = self.sync_source
        source: CommitDatabasing | None = None

        if s_source == DSCommitSynchronizationSource.NONE.value:
            return None

        elif s_source == DSCommitSynchronizationSource.FILE.value:
            file_path = self.sync_file_path
            source = CommitDatabaseSQLite.open(file_path).commit_databasing()

        elif s_source == DSCommitSynchronizationSource.SOCKET.value:
            socket_path = self.sync_socket_path
            source = CommitDatabaseRemote.connect(socket_path).commit_databasing()

        elif s_source == DSCommitSynchronizationSource.HOST.value:
            hostname = self.sync_hostname
            service = self.sync_service
            source = CommitDatabaseRemote.connect(hostname, service).commit_databasing()

        target = CommitDatabaseSQLite.open(target_path)
        return CommitSynchronizer(source, target.commit_databasing(), mode)

    def sync(self):
        self._settings.sync()

    def _value_bool(self, key: str) -> bool:
        return bool(self._settings.value(key, type=bool))

    def _value_int(self, key: str) -> int:
        return int(str(self._settings.value(key, type=int)))

    def _value_str(self, key: str) -> str:
        return str(self._settings.value(key, type=str))
