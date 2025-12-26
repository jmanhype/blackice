"""
Code Extractor
==============

Extracts specs from existing codebases.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any
from datetime import datetime


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    bases: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    file_path: Optional[Path] = None
    line_number: int = 0


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    parameters: list[dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False
    file_path: Optional[Path] = None
    line_number: int = 0


@dataclass
class ImportInfo:
    """Information about an import."""
    module: str
    names: list[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from: bool = False


@dataclass
class ExtractionResult:
    """Result of code extraction."""
    source_path: Path
    language: str
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    imports: list[ImportInfo] = field(default_factory=list)
    patterns: dict[str, Any] = field(default_factory=dict)
    naming_conventions: dict[str, str] = field(default_factory=dict)
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class CodeExtractor:
    """
    Extracts structural information from code.

    Uses tree-sitter for accurate parsing when available,
    falls back to regex for basic extraction.
    """

    def __init__(self, language: str = "python"):
        self.language = language
        self._parser = None
        self._tree_sitter_available = False
        self._try_init_tree_sitter()

    def _try_init_tree_sitter(self):
        """Try to initialize tree-sitter parser."""
        try:
            import tree_sitter_python as tspython
            from tree_sitter import Language, Parser

            self._parser = Parser(Language(tspython.language()))
            self._tree_sitter_available = True
        except ImportError:
            self._tree_sitter_available = False

    def extract_file(self, path: Path) -> ExtractionResult:
        """Extract information from a single file."""
        content = path.read_text()

        if self._tree_sitter_available:
            return self._extract_with_tree_sitter(path, content)
        else:
            return self._extract_with_regex(path, content)

    def _extract_with_tree_sitter(self, path: Path, content: str) -> ExtractionResult:
        """Extract using tree-sitter (accurate)."""
        tree = self._parser.parse(bytes(content, "utf8"))
        root = tree.root_node

        classes = []
        functions = []
        imports = []

        def visit(node, depth=0):
            if node.type == "class_definition":
                class_info = self._extract_class_node(node, path, content)
                if class_info:
                    classes.append(class_info)

            elif node.type == "function_definition":
                # Skip methods (they're part of classes)
                if node.parent and node.parent.type != "class_definition":
                    func_info = self._extract_function_node(node, path, content)
                    if func_info:
                        functions.append(func_info)

            elif node.type in ("import_statement", "import_from_statement"):
                import_info = self._extract_import_node(node, content)
                if import_info:
                    imports.append(import_info)

            for child in node.children:
                visit(child, depth + 1)

        visit(root)

        # Detect patterns
        patterns = self._detect_patterns(classes, functions, imports)
        naming = self._detect_naming_conventions(classes, functions)

        return ExtractionResult(
            source_path=path,
            language=self.language,
            classes=classes,
            functions=functions,
            imports=imports,
            patterns=patterns,
            naming_conventions=naming,
            confidence=0.95,
        )

    def _extract_class_node(self, node, path: Path, content: str) -> Optional[ClassInfo]:
        """Extract class information from AST node."""
        name = None
        bases = []
        methods = []
        docstring = None
        decorators = []

        for child in node.children:
            if child.type == "identifier":
                name = content[child.start_byte:child.end_byte]
            elif child.type == "argument_list":
                # Base classes
                for arg in child.children:
                    if arg.type == "identifier":
                        bases.append(content[arg.start_byte:arg.end_byte])
            elif child.type == "block":
                # Methods and docstring
                for block_child in child.children:
                    if block_child.type == "function_definition":
                        method_name = None
                        for fc in block_child.children:
                            if fc.type == "identifier":
                                method_name = content[fc.start_byte:fc.end_byte]
                                break
                        if method_name:
                            methods.append(method_name)
                    elif block_child.type == "expression_statement":
                        # Potential docstring
                        for expr in block_child.children:
                            if expr.type == "string":
                                docstring = content[expr.start_byte:expr.end_byte].strip("\"'")
            elif child.type == "decorator":
                dec_text = content[child.start_byte:child.end_byte]
                decorators.append(dec_text)

        if name:
            return ClassInfo(
                name=name,
                bases=bases,
                methods=methods,
                docstring=docstring,
                decorators=decorators,
                file_path=path,
                line_number=node.start_point[0] + 1,
            )
        return None

    def _extract_function_node(self, node, path: Path, content: str) -> Optional[FunctionInfo]:
        """Extract function information from AST node."""
        name = None
        parameters = []
        return_type = None
        docstring = None
        decorators = []
        is_async = False

        # Check for async
        if node.type == "function_definition":
            # Look at previous sibling for async keyword
            pass

        for child in node.children:
            if child.type == "identifier":
                name = content[child.start_byte:child.end_byte]
            elif child.type == "parameters":
                for param in child.children:
                    if param.type == "identifier":
                        param_name = content[param.start_byte:param.end_byte]
                        parameters.append({"name": param_name})
                    elif param.type == "typed_parameter":
                        param_name = None
                        param_type = None
                        for pc in param.children:
                            if pc.type == "identifier":
                                param_name = content[pc.start_byte:pc.end_byte]
                            elif pc.type == "type":
                                param_type = content[pc.start_byte:pc.end_byte]
                        if param_name:
                            parameters.append({"name": param_name, "type": param_type})
            elif child.type == "type":
                return_type = content[child.start_byte:child.end_byte]
            elif child.type == "block":
                # Check for docstring
                for block_child in child.children:
                    if block_child.type == "expression_statement":
                        for expr in block_child.children:
                            if expr.type == "string":
                                docstring = content[expr.start_byte:expr.end_byte].strip("\"'")
                                break
                        break

        if name:
            return FunctionInfo(
                name=name,
                parameters=parameters,
                return_type=return_type,
                docstring=docstring,
                decorators=decorators,
                is_async=is_async,
                file_path=path,
                line_number=node.start_point[0] + 1,
            )
        return None

    def _extract_import_node(self, node, content: str) -> Optional[ImportInfo]:
        """Extract import information from AST node."""
        if node.type == "import_statement":
            for child in node.children:
                if child.type == "dotted_name":
                    module = content[child.start_byte:child.end_byte]
                    return ImportInfo(module=module, is_from=False)

        elif node.type == "import_from_statement":
            module = None
            names = []
            for child in node.children:
                if child.type == "dotted_name":
                    module = content[child.start_byte:child.end_byte]
                elif child.type == "import_from_as_names":
                    for name_node in child.children:
                        if name_node.type == "identifier":
                            names.append(content[name_node.start_byte:name_node.end_byte])
            if module:
                return ImportInfo(module=module, names=names, is_from=True)

        return None

    def _extract_with_regex(self, path: Path, content: str) -> ExtractionResult:
        """Extract using regex (fallback, less accurate)."""
        import re

        classes = []
        functions = []
        imports = []

        # Extract classes
        class_pattern = r'^class\s+(\w+)(?:\(([\w\s,]+)\))?:'
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            name = match.group(1)
            bases = match.group(2).split(',') if match.group(2) else []
            bases = [b.strip() for b in bases if b.strip()]
            classes.append(ClassInfo(
                name=name,
                bases=bases,
                file_path=path,
                line_number=content[:match.start()].count('\n') + 1,
            ))

        # Extract functions
        func_pattern = r'^(?:async\s+)?def\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            name = match.group(1)
            functions.append(FunctionInfo(
                name=name,
                is_async='async' in match.group(0),
                file_path=path,
                line_number=content[:match.start()].count('\n') + 1,
            ))

        # Extract imports
        import_pattern = r'^(?:from\s+([\w.]+)\s+)?import\s+([\w\s,*]+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            from_module = match.group(1)
            import_names = [n.strip() for n in match.group(2).split(',')]
            if from_module:
                imports.append(ImportInfo(module=from_module, names=import_names, is_from=True))
            else:
                for name in import_names:
                    imports.append(ImportInfo(module=name, is_from=False))

        return ExtractionResult(
            source_path=path,
            language=self.language,
            classes=classes,
            functions=functions,
            imports=imports,
            confidence=0.7,
            warnings=["Using regex extraction (tree-sitter not available)"],
        )

    def _detect_patterns(
        self,
        classes: list[ClassInfo],
        functions: list[FunctionInfo],
        imports: list[ImportInfo],
    ) -> dict[str, Any]:
        """Detect common patterns in the code."""
        patterns = {}

        # Check for dataclasses
        dataclass_count = sum(1 for c in classes if "@dataclass" in c.decorators)
        if dataclass_count > 0:
            patterns["data_modeling"] = "dataclasses"

        # Check for pydantic
        pydantic_imports = any(i.module.startswith("pydantic") for i in imports)
        if pydantic_imports:
            patterns["data_modeling"] = "pydantic"

        # Check for async
        async_count = sum(1 for f in functions if f.is_async)
        if async_count > len(functions) * 0.5:
            patterns["concurrency"] = "async"

        # Check for type hints
        typed_funcs = sum(1 for f in functions if f.return_type or any(p.get("type") for p in f.parameters))
        if typed_funcs > len(functions) * 0.5:
            patterns["typing"] = "strict"

        return patterns

    def _detect_naming_conventions(
        self,
        classes: list[ClassInfo],
        functions: list[FunctionInfo],
    ) -> dict[str, str]:
        """Detect naming conventions."""
        import re

        conventions = {}

        # Class naming
        pascal_case = sum(1 for c in classes if re.match(r'^[A-Z][a-zA-Z0-9]*$', c.name))
        if pascal_case == len(classes) and classes:
            conventions["classes"] = "PascalCase"

        # Function naming
        snake_case = sum(1 for f in functions if re.match(r'^[a-z_][a-z0-9_]*$', f.name))
        camel_case = sum(1 for f in functions if re.match(r'^[a-z][a-zA-Z0-9]*$', f.name))

        if snake_case > camel_case:
            conventions["functions"] = "snake_case"
        elif camel_case > snake_case:
            conventions["functions"] = "camelCase"

        return conventions


def extract_spec(path: Path, language: str = "python") -> ExtractionResult:
    """Convenience function to extract spec from a file or directory."""
    extractor = CodeExtractor(language)

    if path.is_file():
        return extractor.extract_file(path)

    # Directory: aggregate results
    all_classes = []
    all_functions = []
    all_imports = []
    all_patterns = {}
    all_naming = {}
    warnings = []

    for file_path in path.rglob(f"*.py" if language == "python" else "*"):
        if "__pycache__" in str(file_path) or ".git" in str(file_path):
            continue
        try:
            result = extractor.extract_file(file_path)
            all_classes.extend(result.classes)
            all_functions.extend(result.functions)
            all_imports.extend(result.imports)
            all_patterns.update(result.patterns)
            all_naming.update(result.naming_conventions)
            warnings.extend(result.warnings)
        except Exception as e:
            warnings.append(f"Error extracting {file_path}: {e}")

    return ExtractionResult(
        source_path=path,
        language=language,
        classes=all_classes,
        functions=all_functions,
        imports=all_imports,
        patterns=all_patterns,
        naming_conventions=all_naming,
        confidence=0.85,
        warnings=warnings,
    )
