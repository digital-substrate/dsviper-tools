"""Python syntax highlighter for QPlainTextEdit.

Same application order as ge-qml version.
Colors from DSSyntaxColor.xcassets dark theme.
"""
from __future__ import annotations

import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

# --- Dark theme colors from DSSyntaxColor.xcassets ---
_COLORS = {
    "TextPlain":              "#ffffff",
    "TextBackground":         "#292a2f",
    "TextKeyword":            "#f469a0",
    "TextBuiltin":            "#6b8ac3",
    "TextString":             "#a3c2a3",
    "TextQuote":              "#f06860",
    "TextComment":            "#6c7985",
    "TextNumber":             "#cfbe69",
    "TextOperator":           "#41a0c0",
    "TextConstant":           "#c7b18f",
    "TextTypeUser":           "#78b8a9",
    "TextViperType":          "#d0a8ff",
    "TextAttribut":           "#60a898",
    "TextDunder":             "#6f89ff",
    "TextDocStr":             "#a7acbd",
    "TextDefinitionConstant": "#b0bb9a",
    "TextViperFunction":      "#af75f6",
    "TextViperConstant":      "#ad9fc6",
    "TextViperAttribut":      "#8d73be",
    "TextError":              "#e54c4c",
    "TextCursor":             "#ff8900",
    "TextSelection":          "#3f4858",
}

# --- Python keywords ---
_KEYWORDS = [
    'and', 'as', 'assert', 'async', 'await', 'break', 'class',
    'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
    'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
    'while', 'with', 'yield',
]

_SPECIAL_CONSTANTS = ['False', 'None', 'True']

_BUILTINS = [
    'print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict',
    'set', 'tuple', 'type', 'isinstance', 'hasattr', 'getattr',
    'setattr', 'open', 'input', 'abs', 'all', 'any', 'bin', 'bool',
    'bytes', 'callable', 'chr', 'dir', 'divmod', 'enumerate',
    'eval', 'exec', 'filter', 'format', 'frozenset', 'globals',
    'hash', 'hex', 'id', 'iter', 'locals', 'map', 'max', 'min',
    'next', 'object', 'oct', 'ord', 'pow', 'repr', 'reversed',
    'round', 'slice', 'sorted', 'sum', 'super', 'vars', 'zip',
    'self', 'cls',
]

# --- Viper types ---
_VIPER_TYPES = [
    'Type', 'TypeName', 'TypeAny', 'TypeVoid', 'TypeBool',
    'TypeUInt8', 'TypeUInt16', 'TypeUInt32', 'TypeUInt64',
    'TypeInt8', 'TypeInt16', 'TypeInt32', 'TypeInt64',
    'TypeFloat', 'TypeDouble', 'TypeString', 'TypeBlob',
    'TypeBlobId', 'TypeCommitId', 'TypeUUId',
    'TypeVec', 'TypeMat', 'TypeTuple',
    'TypeOptional', 'TypeVector', 'TypeSet', 'TypeMap', 'TypeXArray',
    'TypeAny', 'TypeVariant',
    'TypeEnumerationDescriptor', 'TypeEnumeration', 'TypeEnumerationCase',
    'TypeStructureDescriptor', 'TypeStructure', 'TypeStructureField',
    'TypeKey', 'TypeConcept', 'TypeClub', 'TypeAnyConcept',
    'Value', 'ValueAny', 'ValueVoid', 'ValueBool',
    'ValueUInt8', 'ValueUInt16', 'ValueUInt32', 'ValueUInt64',
    'ValueInt8', 'ValueInt16', 'ValueInt32', 'ValueInt64',
    'ValueFloat', 'ValueDouble', 'ValueBlobId', 'ValueCommitId', 'ValueUUId',
    'ValueBlob', 'ValueString',
    'ValueVec', 'ValueMat',
    'ValueTuple', 'ValueTupleIter',
    'ValueOptional', 'ValueVector', 'ValueVectorIter',
    'ValueSet', 'ValueSetIter', 'ValueMap', 'ValueVariant', 'ValueXArray',
    'ValueMapValuesIter', 'ValueMapItemsIter', 'ValueMapKeysIter',
    'ValueStructure', 'ValueEnumeration', 'ValueKey',
    'ValueProgram', 'ValueOpcodeKey', 'ValueOpcode',
    'ValueOpcodeDocumentSet', 'ValueOpcodeDocumentUpdate',
    'ValueOpcodeMapSubtract', 'ValueOpcodeMapUnion', 'ValueOpcodeMapUpdate',
    'ValueOpcodeSetSubtract', 'ValueOpcodeSetUnion',
    'ValueOpcodeXArrayInsert', 'ValueOpcodeXArrayRemove', 'ValueOpcodeXArrayUpdate',
    'Attachment', 'AttachmentGetting', 'AttachmentMutating',
    'AttachmentFunctionPool', 'AttachmentFunctionPoolFunctions',
    'AttachmentGettingFunction', 'AttachmentMutatingFunction',
    'Definitions', 'DefinitionsConst', 'DefinitionsInspector',
    'DefinitionsExtendInfo', 'DefinitionsCollector', 'DefinitionsMapper',
    'DocumentNode', 'Html', 'Key', 'KeyHelper', 'KeyNamer',
    'Path', 'PathConst', 'PathComponent', 'PathElementInfo', 'PathEntryKeyInfo',
    'FunctionPrototype', 'Function', 'FunctionPool', 'FunctionPoolFunctions',
    'BlobEncoder', 'BlobEncoderLayout', 'BlobView', 'BlobArray', 'BlobStatistics',
    'BlobPackDescriptor', 'BlobPack', 'BlobPackRegion',
    'BlobData', 'BlobInfo', 'BlobLayout', 'BlobStream',
    'BlobIdMapper', 'BlobGetting',
    'Databasing', 'Database', 'DatabaseSQLite', 'DatabaseRemote',
    'Commit', 'CommitAction', 'CommitData', 'CommitEvalAction',
    'CommitDatabase', 'CommitDatabaseSQLite', 'CommitDatabaseRemote',
    'CommitDatabasing', 'CommitDatabaseServer',
    'CommitHeader', 'CommitState', 'CommitMutableState',
    'CommitPersistenceSQLite', 'CommitServerLocal', 'CommitServerRemote',
    'CommitStore', 'CommitStoreBaseNotifying',
    'CommitSynchronizer', 'CommitSyncData',
    'CommitSynchronizerInfo', 'CommitSynchronizerInfoTransmit',
    'CommitNode', 'CommitNodeGrid', 'CommitNodeGridBuilder',
    'StreamRawReading', 'StreamRawWriting', 'StreamRawReader', 'StreamRawWriter',
    'StreamWriting', 'StreamReading',
    'StreamBinaryReader', 'StreamBinaryWriter',
    'StreamTokenBinaryReader', 'StreamTokenBinaryWriter',
    'StreamReaderBlob', 'StreamReaderFile', 'StreamWriterBlob', 'StreamWriterFile',
    'StreamReaderSharedMemory', 'StreamWriterSharedMemory',
    'Codec', 'StreamCodecInstancing', 'StreamEncoding', 'StreamDecoding', 'StreamSizing',
    'Service', 'ServiceRemote', 'ServiceRemoteFunction', 'ServiceRemoteFunctions',
    'ServiceRemoteFunctionPool', 'ServiceRemoteFunctionPoolFunction',
    'ServiceRemoteFunctionPoolFunctions', 'ServiceRemoteFunctionPools',
    'ServiceRemoteAttachmentFunction', 'ServiceRemoteAttachmentFunctionPool',
    'ServiceRemoteAttachmentFunctionPoolFunction',
    'ServiceRemoteAttachmentFunctionPoolFunctions', 'ServiceRemoteAttachmentFunctionPools',
    'DSMBuilder', 'DSMBuilderPart', 'DSMParseReport', 'DSMParseError',
    'DSMDefinitions', 'DSMDefinitionsInspector',
    'DSMConcept', 'DSMClub', 'DSMEnumeration', 'DSMEnumerationCase',
    'DSMStructure', 'DSMStructureField', 'DSMTypeKey', 'DSMTypeReference',
    'DSMTypeVec', 'DSMTypeMat', 'DSMTypeTuple',
    'DSMTypeOptional', 'DSMTypeVector', 'DSMTypeSet', 'DSMTypeMap', 'DSMTypeXArray',
    'DSMTypeVariant', 'DSMLiteralList', 'DSMLiteralValue',
    'DSMAttachment', 'DSMFunction', 'DSMFunctionPrototype', 'DSMFunctionPool',
    'DSMAttachmentFunction', 'DSMAttachmentFunctionPool',
    'SharedMemory', 'SQLite', 'Hashing', 'Cancelation',
    'Logging', 'LoggerConsole', 'LoggerNull', 'LoggerPrint', 'LoggerReport',
    'Socket', 'RPCPacket', 'Range', 'RangeIter',
    'HashCRC32', 'HashMD5', 'HashSHA1', 'HashSHA256', 'HashSHA3',
    'Float16', 'Fuzzer', 'Error', 'ViperError', 'Optional',
]


def _word_boundary_pattern(words):
    return r'\b(?:' + '|'.join(re.escape(w) for w in words) + r')\b'


def _make_format(color_name, bold=False, italic=False):
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(_COLORS[color_name]))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


class PythonHighlighter(QSyntaxHighlighter):
    """Python syntax highlighter for QTextDocument.

    Application order matches the Obj-C version exactly.
    """

    def __init__(self, document=None):
        super().__init__(document)
        self._mode = "source"
        self._setup_formats()
        self._setup_rules()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if self._mode != value:
            self._mode = value
            self.rehighlight()

    def _setup_formats(self):
        self.f_type_user     = _make_format("TextTypeUser")
        self.f_viper_type    = _make_format("TextViperType")
        self.f_keyword       = _make_format("TextKeyword", bold=True)
        self.f_builtin       = _make_format("TextBuiltin")
        self.f_viper_func    = _make_format("TextViperFunction")
        self.f_attribut      = _make_format("TextAttribut")
        self.f_viper_attr    = _make_format("TextViperAttribut")
        self.f_dunder        = _make_format("TextDunder")
        self.f_operator      = _make_format("TextOperator")
        self.f_number        = _make_format("TextNumber")
        self.f_string        = _make_format("TextString")
        self.f_quote         = _make_format("TextQuote")
        self.f_comment       = _make_format("TextComment", italic=True)
        self.f_constant      = _make_format("TextConstant")
        self.f_def_constant  = _make_format("TextDefinitionConstant")
        self.f_viper_const   = _make_format("TextViperConstant")
        self.f_docstr        = _make_format("TextDocStr")
        self.f_error         = _make_format("TextError")
        self.f_help_section  = _make_format("TextConstant", bold=True)

    def _setup_rules(self):
        self.rules = []
        self.rules.append((re.compile(r'\b[A-Z]\w*\b'), self.f_type_user))
        self.rules.append((re.compile(_word_boundary_pattern(_VIPER_TYPES)), self.f_viper_type))
        self.rules.append((re.compile(_word_boundary_pattern(_KEYWORDS)), self.f_keyword))
        self.rules.append((re.compile(_word_boundary_pattern(_BUILTINS)), self.f_builtin))
        self.rules.append((re.compile(r'\bversion\b'), self.f_viper_func))
        self.rules.append((re.compile(r'\.\w+'), self.f_attribut))
        self.rules.append((re.compile(r'\bvpr_\w+'), self.f_viper_attr))
        self.rules.append((re.compile(r'__\w+__'), self.f_dunder))
        self.rules.append((re.compile(r'[+\-*/^%<>()\[\]{}=!|:@.]'), self.f_operator))
        self.rules.append((re.compile(r'\b[-+]?[0-9_]*\.?[0-9_]+([eE][-+]?[0-9_]+)?\b'), self.f_number))
        self.rules.append((re.compile(r'\b0x[0-9a-fA-F]+\b'), self.f_number))
        self.rules.append((re.compile(r'f?".*?"'), self.f_string))
        self.rules.append((re.compile(r"f?'.*?'"), self.f_quote))
        self.rules.append((re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'), self.f_number))
        self.rules.append((re.compile(r'\b[0-9a-fA-F]{40}\b'), self.f_number))
        self.rules.append((re.compile(_word_boundary_pattern(_SPECIAL_CONSTANTS)), self.f_keyword))
        self.rules.append((re.compile(r'\b[A-Z]+_[0-9A-Z_]*\b'), self.f_constant))
        self.rules.append((re.compile(r'\b[0-9A-Z_]+_[TKESAP]_[0-9A-Z_]+\b'), self.f_def_constant))
        self.rules.append((re.compile(r'""".*?"""'), self.f_docstr))
        self.rules.append((re.compile(r"'''.*?'''"), self.f_docstr))
        self.rules.append((re.compile(r'#.*|//.*'), self.f_comment))

        self._docstr_double = re.compile(r'"""')
        self._docstr_single = re.compile(r"'''")

        self.help_rules = [
            (re.compile(_word_boundary_pattern(_VIPER_TYPES)), self.f_viper_type),
            (re.compile(r'\bversion\b'), self.f_viper_func),
            (re.compile(_word_boundary_pattern(_SPECIAL_CONSTANTS)), self.f_keyword),
            (re.compile(r'^\s{4}\w+', re.MULTILINE), self.f_attribut),
            (re.compile(r'^(?:NAME|DESCRIPTION|DATA|FILE|CLASSES|FUNCTIONS|MODULE REFERENCE)\b', re.MULTILINE), self.f_help_section),
        ]

        _DSM_KEYWORDS = ['struct', 'enum', 'concept', 'club', 'attachment', 'namespace',
                         'function_pool', 'mutable', 'is', 'a']
        self.dsm_rules = [
            (re.compile(r'\b[A-Z]\w*\b'), self.f_type_user),
            (re.compile(_word_boundary_pattern(_VIPER_TYPES)), self.f_viper_type),
            (re.compile(_word_boundary_pattern(_DSM_KEYWORDS)), self.f_keyword),
            (re.compile(r'[+\-*/^%<>()\[\]{}=!|:@.]'), self.f_operator),
            (re.compile(r'\b[-+]?[0-9_]*\.?[0-9_]+([eE][-+]?[0-9_]+)?\b'), self.f_number),
            (re.compile(r'f?".*?"'), self.f_string),
            (re.compile(r"f?'.*?'"), self.f_quote),
            (re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'), self.f_number),
            (re.compile(r'""".*?"""'), self.f_docstr),
            (re.compile(r'#.*|//.*'), self.f_comment),
        ]

    # Block states for multi-line docstrings
    _STATE_NORMAL = -1
    _STATE_IN_DOUBLE_DOCSTR = 1
    _STATE_IN_SINGLE_DOCSTR = 2

    def highlightBlock(self, text: str):
        if self._mode == "help":
            rules = self.help_rules
        elif self._mode == "dsm":
            rules = self.dsm_rules
        else:
            rules = self.rules

        for pattern, fmt in rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - match.start()
                self.setFormat(start, length, fmt)

        self._highlight_multiline(text, self._docstr_double, self._STATE_IN_DOUBLE_DOCSTR)
        self._highlight_multiline(text, self._docstr_single, self._STATE_IN_SINGLE_DOCSTR)

    def _highlight_multiline(self, text: str, delimiter: re.Pattern, state: int):
        if self.previousBlockState() == state:
            start = 0
            match = delimiter.search(text)
            if match:
                length = match.end()
                self.setFormat(start, length, self.f_docstr)
                self.setCurrentBlockState(self._STATE_NORMAL)
            else:
                self.setFormat(0, len(text), self.f_docstr)
                self.setCurrentBlockState(state)
            return

        start = 0
        while start < len(text):
            match = delimiter.search(text, start)
            if not match:
                break
            close = delimiter.search(text, match.end())
            if close:
                start = close.end()
            else:
                self.setFormat(match.start(), len(text) - match.start(), self.f_docstr)
                self.setCurrentBlockState(state)
                return
