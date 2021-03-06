import re
import os
import sublime
try:
    from typing_extensions import Protocol
    from typing import Optional, List, Callable, Dict, Any
    assert Optional and List and Callable and Dict and Any
except ImportError:
    pass
    Protocol = object  # type: ignore

from debug_tools import getLogger
from debug_tools.utilities import get_representation
log = getLogger(1, __package__)

class SmartObject(object):

    def __str__(self):
        return get_representation(self, repr=str)

    def __repr__(self):
        return get_representation(self, repr=repr)


class Settings(SmartObject):

    def __init__(self) -> None:
        self.show_status_messages = True
        self.show_view_status = True
        self.auto_show_diagnostics_panel = True
        self.auto_show_diagnostics_panel_level = 3
        self.show_diagnostics_phantoms = False
        self.show_diagnostics_count_in_view_status = False
        self.show_diagnostics_in_view_status = True
        self.show_diagnostics_severity_level = 3
        self.only_show_lsp_completions = False
        self.diagnostics_highlight_style = "underline"
        self.highlight_active_signature_parameter = True
        self.document_highlight_style = "stippled"
        self.document_highlight_scopes = {
            "unknown": "text",
            "text": "text",
            "read": "markup.inserted",
            "write": "markup.changed"
        }
        self.diagnostics_gutter_marker = "dot"
        self.show_code_actions_bulb = False
        self.complete_all_chars = False
        self.completion_hint_type = "auto"
        self.complete_using_text_edit = False
        self.resolve_completion_for_snippets = False
        self.log_debug = True
        self.log_server = True
        self.log_stderr = False
        self.log_payloads = False

    @staticmethod
    def setLevel(enabled, level):
        log._debug_level = log.debug_level | level if enabled else log.debug_level & ~level

    @staticmethod
    def setLogFile(file_path):
        file_path = file_path.strip()

        if file_path:
            if os.path.isabs(file_path):
                log.setup(file_path)
            else:
                new_path = os.path.join(sublime.packages_path(), "User", file_path)
                log.setup(new_path)
        else:
            log.setup(file_path)

class ClientStates(SmartObject):
    STARTING = 0
    READY = 1
    STOPPING = 2


def config_supports_syntax(config: 'ClientConfig', syntax: str) -> bool:
    for language in config.languages:
        try:
            regex = r'|'.join(r'\b%s\b' % re.escape(s) for s in language.syntaxes)
            if re.search(regex, syntax, re.IGNORECASE):
                return True
        except:
            log.exception('regex', regex, 'syntax', syntax)
    return False


class LanguageConfig(SmartObject):
    def __init__(self, language_id: str, scopes: 'List[str]', syntaxes: 'List[str]') -> None:
        self.id = language_id
        self.scopes = scopes
        self.syntaxes = syntaxes


class ClientConfig(SmartObject):
    def __init__(self, name: str, binary_args: 'List[str]', tcp_port: 'Optional[int]', scopes=[],
                 syntaxes=[], languageId: 'Optional[str]'=None,
                 languages: 'List[LanguageConfig]'=[], enabled: bool=True, init_options=dict(),
                 settings=dict(), env=dict(), tcp_host: 'Optional[str]'=None) -> None:
        self.name = name
        self.binary_args = binary_args
        self.tcp_port = tcp_port
        self.tcp_host = tcp_host
        if not languages:
            languages = [LanguageConfig(languageId, scopes, syntaxes)] if languageId else []
        self.languages = languages
        self.enabled = enabled
        self.init_options = init_options
        self.settings = settings
        self.env = env


class ViewLike(Protocol):
    def __init__(self) -> None:
        pass

    def file_name(self) -> 'Optional[str]':
        ...

    def window(self) -> 'Optional[Any]':  # WindowLike
        ...

    def buffer_id(self) -> int:
        ...

    def substr(self, region: 'Any') -> str:
        ...

    def settings(self) -> 'Any':  # SettingsLike
        ...

    def size(self) -> int:
        ...

    def set_status(self, key: str, status: str) -> None:
        ...

    def sel(self):
        ...

    def score_selector(self, region, scope: str) -> int:
        ...


class WindowLike(Protocol):
    def id(self) -> int:
        ...

    def folders(self) -> 'List[str]':
        ...

    def num_groups(self) -> int:
        ...

    def active_group(self) -> int:
        ...

    def active_view_in_group(self, group: int) -> ViewLike:
        ...

    def project_data(self) -> 'Optional[dict]':
        ...

    def active_view(self) -> 'Optional[ViewLike]':
        ...

    def status_message(self, msg: str) -> None:
        ...

    def views(self) -> 'List[ViewLike]':
        ...

    def run_command(self, command_name: str, command_args: 'Dict[str, Any]') -> None:
        ...
