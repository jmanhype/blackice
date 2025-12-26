"""
unrdf Adapter
=============

Integration with Sean Chatman's unrdf
https://github.com/seanchatman/unrdf

unrdf is an RDF Knowledge Graph Platform with 17 packages.
It provides the semantic layer for ontology storage and querying.

Use cases:
- Store specs as RDF ontologies
- Query relationships between components
- Bridge brownfield extraction to ontology format
- Semantic search over codebase knowledge
"""

import subprocess
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any, List


@dataclass
class UnrdfConfig:
    """Configuration for unrdf."""
    unrdf_path: Path = field(default_factory=lambda: Path("../unrdf"))
    store_path: Path = field(default_factory=lambda: Path(".blackice/ontology"))
    default_graph: str = "http://blackice.dev/graph"


@dataclass
class Triple:
    """An RDF triple."""
    subject: str
    predicate: str
    object: str


@dataclass
class QueryResult:
    """Result of a SPARQL query."""
    success: bool
    bindings: list[dict[str, str]] = field(default_factory=list)
    error: Optional[str] = None


class UnrdfAdapter:
    """
    Adapter for Sean Chatman's unrdf knowledge graph platform.

    unrdf provides:
    - RDF triple store
    - SPARQL query engine
    - Ontology management
    - Semantic reasoning
    """

    def __init__(self, config: Optional[UnrdfConfig] = None):
        self.config = config or UnrdfConfig()
        self._verified = False

    def verify_installation(self) -> tuple[bool, str]:
        """Verify unrdf is installed."""
        unrdf_path = self.config.unrdf_path

        if not unrdf_path.exists():
            return False, f"unrdf not found at {unrdf_path}. Clone from: https://github.com/seanchatman/unrdf"

        package_json = unrdf_path / "package.json"
        if not package_json.exists():
            return False, f"unrdf package.json not found. Invalid installation."

        node_modules = unrdf_path / "node_modules"
        if not node_modules.exists():
            return False, f"unrdf dependencies not installed. Run: cd {unrdf_path} && npm install"

        self._verified = True
        return True, "unrdf ready"

    def load_ontology(self, path: Path, graph: Optional[str] = None) -> bool:
        """
        Load an ontology file into the store.

        Args:
            path: Path to ontology file (TTL, RDF/XML, N-Triples)
            graph: Named graph to load into

        Returns:
            True if successful
        """
        if not self._verified:
            ok, msg = self.verify_installation()
            if not ok:
                raise RuntimeError(msg)

        graph = graph or self.config.default_graph

        # Use unrdf CLI to load
        cmd = [
            "npx", "unrdf", "load",
            "--file", str(path),
            "--graph", graph,
            "--store", str(self.config.store_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.unrdf_path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def query(self, sparql: str) -> QueryResult:
        """
        Execute a SPARQL query.

        Args:
            sparql: SPARQL query string

        Returns:
            QueryResult with bindings
        """
        if not self._verified:
            ok, msg = self.verify_installation()
            if not ok:
                return QueryResult(success=False, error=msg)

        cmd = [
            "npx", "unrdf", "query",
            "--sparql", sparql,
            "--store", str(self.config.store_path),
            "--format", "json",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.unrdf_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return QueryResult(success=False, error=result.stderr)

            data = json.loads(result.stdout)
            return QueryResult(
                success=True,
                bindings=data.get("results", {}).get("bindings", []),
            )
        except Exception as e:
            return QueryResult(success=False, error=str(e))

    def add_triple(self, triple: Triple, graph: Optional[str] = None) -> bool:
        """Add a single triple to the store."""
        graph = graph or self.config.default_graph

        sparql = f"""
        INSERT DATA {{
            GRAPH <{graph}> {{
                <{triple.subject}> <{triple.predicate}> <{triple.object}> .
            }}
        }}
        """

        result = self.query(sparql)
        return result.success

    def spec_to_ontology(self, spec) -> List[Triple]:
        """
        Convert a BLACKICE Spec to RDF triples.

        This bridges brownfield extraction to the ontology world.
        """
        triples = []
        base = "http://blackice.dev/ontology#"
        rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        rdfs = "http://www.w3.org/2000/01/rdf-schema#"

        # Spec metadata
        spec_uri = f"{base}{spec.name}"
        triples.append(Triple(spec_uri, f"{rdf}type", f"{base}Specification"))
        triples.append(Triple(spec_uri, f"{rdfs}label", spec.name))
        triples.append(Triple(spec_uri, f"{base}version", spec.version))

        # Classes
        for cls in spec.classes:
            cls_uri = f"{base}{cls.get('name', 'Unknown')}"
            triples.append(Triple(cls_uri, f"{rdf}type", f"{base}Class"))
            triples.append(Triple(spec_uri, f"{base}hasClass", cls_uri))

            for method in cls.get("methods", []):
                method_uri = f"{cls_uri}/{method}"
                triples.append(Triple(cls_uri, f"{base}hasMethod", method_uri))

        # Functions
        for func in spec.functions:
            func_uri = f"{base}{func.get('name', 'unknown')}"
            triples.append(Triple(func_uri, f"{rdf}type", f"{base}Function"))
            triples.append(Triple(spec_uri, f"{base}hasFunction", func_uri))

        return triples

    def extraction_to_ontology(self, extraction_result) -> List[Triple]:
        """
        Convert brownfield extraction result to RDF triples.

        This is the bridge from tree-sitter extraction to Sean's ontology world.
        """
        triples = []
        base = "http://blackice.dev/extracted#"
        rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

        # Source
        source_uri = f"{base}{extraction_result.source_path.name}"
        triples.append(Triple(source_uri, f"{rdf}type", f"{base}Codebase"))

        # Patterns
        for pattern_name, pattern_value in extraction_result.patterns.items():
            pattern_uri = f"{source_uri}/pattern/{pattern_name}"
            triples.append(Triple(source_uri, f"{base}hasPattern", pattern_uri))
            triples.append(Triple(pattern_uri, f"{base}patternType", str(pattern_value)))

        # Classes
        for cls in extraction_result.classes:
            cls_uri = f"{source_uri}/class/{cls.name}"
            triples.append(Triple(source_uri, f"{base}hasClass", cls_uri))
            triples.append(Triple(cls_uri, f"{rdf}type", f"{base}ExtractedClass"))

        return triples
