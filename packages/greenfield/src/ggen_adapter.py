"""
ggen Adapter
============

Integration with Sean Chatman's ggen (v5.0.2)
https://github.com/seanchatman/ggen

ggen provides deterministic ontology-to-code generation in Rust.
This is the core of greenfield generation - no LLM hallucination,
just structured transformation from ontology to code.

Features:
- FMEA (Failure Mode and Effects Analysis) built-in
- Poka-Yoke (error-proofing) patterns
- Multiple output languages
- Versioned, reproducible output
"""

import subprocess
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any


@dataclass
class GgenConfig:
    """Configuration for ggen."""
    ggen_path: Path = field(default_factory=lambda: Path("../ggen"))
    output_language: str = "python"  # python, typescript, rust, go
    include_tests: bool = True
    include_docs: bool = True
    fmea_enabled: bool = True
    poka_yoke_enabled: bool = True


@dataclass
class GgenResult:
    """Result of ggen code generation."""
    success: bool
    files: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fmea_report: Optional[dict] = None


class GgenAdapter:
    """
    Adapter for Sean Chatman's ggen ontology-to-code generator.

    ggen transforms ontologies (RDF/OWL) into working code with:
    - Type-safe data models
    - CRUD operations
    - Validation logic
    - Tests
    - Documentation

    This is DETERMINISTIC - same ontology always produces same code.
    No LLM randomness.
    """

    def __init__(self, config: Optional[GgenConfig] = None):
        self.config = config or GgenConfig()
        self._verified = False

    def verify_installation(self) -> tuple[bool, str]:
        """Verify ggen is installed and accessible."""
        ggen_path = self.config.ggen_path

        if not ggen_path.exists():
            return False, f"ggen not found at {ggen_path}. Clone from: https://github.com/seanchatman/ggen"

        cargo_toml = ggen_path / "Cargo.toml"
        if not cargo_toml.exists():
            return False, f"ggen Cargo.toml not found. Invalid ggen installation."

        # Check if built
        target_release = ggen_path / "target" / "release" / "ggen"
        if not target_release.exists():
            return False, f"ggen not built. Run: cd {ggen_path} && cargo build --release"

        self._verified = True
        return True, "ggen ready"

    def generate(
        self,
        ontology_path: Path,
        output_dir: Path,
        language: Optional[str] = None,
    ) -> GgenResult:
        """
        Generate code from ontology using ggen.

        Args:
            ontology_path: Path to ontology file (RDF/OWL/TTL)
            output_dir: Directory to write generated code
            language: Override output language

        Returns:
            GgenResult with generated files
        """
        if not self._verified:
            ok, msg = self.verify_installation()
            if not ok:
                return GgenResult(success=False, errors=[msg])

        lang = language or self.config.output_language
        ggen_binary = self.config.ggen_path / "target" / "release" / "ggen"

        cmd = [
            str(ggen_binary),
            str(ontology_path),
            "--output", str(output_dir),
            "--language", lang,
        ]

        if self.config.include_tests:
            cmd.append("--tests")
        if self.config.include_docs:
            cmd.append("--docs")
        if self.config.fmea_enabled:
            cmd.append("--fmea")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                return GgenResult(
                    success=False,
                    errors=[result.stderr or "ggen failed"],
                )

            # Collect generated files
            files = {}
            if output_dir.exists():
                for file_path in output_dir.rglob("*"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(output_dir)
                        files[str(rel_path)] = file_path.read_text()

            # Parse FMEA report if generated
            fmea_report = None
            fmea_path = output_dir / "fmea_report.json"
            if fmea_path.exists():
                fmea_report = json.loads(fmea_path.read_text())

            return GgenResult(
                success=True,
                files=files,
                fmea_report=fmea_report,
            )

        except subprocess.TimeoutExpired:
            return GgenResult(success=False, errors=["ggen timed out"])
        except Exception as e:
            return GgenResult(success=False, errors=[str(e)])

    def generate_from_spec(self, spec, output_dir: Path) -> GgenResult:
        """
        Generate code from a BLACKICE Spec.

        Converts Spec to ontology format, then runs ggen.
        """
        # Convert spec to temporary ontology file
        ontology = self._spec_to_ontology(spec)

        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
            f.write(ontology)
            ontology_path = Path(f.name)

        try:
            return self.generate(ontology_path, output_dir)
        finally:
            ontology_path.unlink()

    def _spec_to_ontology(self, spec) -> str:
        """Convert BLACKICE Spec to Turtle ontology format."""
        lines = [
            "@prefix : <http://blackice.dev/ontology#> .",
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
            "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
            "",
            f": a owl:Ontology ;",
            f'  rdfs:label "{spec.name}" ;',
            f'  rdfs:comment "{spec.description}" .',
            "",
        ]

        # Add classes
        for cls in spec.classes:
            name = cls.get("name", "Unknown")
            lines.append(f":{name} a owl:Class ;")
            if cls.get("description"):
                lines.append(f'  rdfs:comment "{cls["description"]}" ;')

            # Add attributes as properties
            for attr in cls.get("attributes", []):
                lines.append(f"  :has{attr.title()} :{attr} ;")

            lines.append("  .")
            lines.append("")

        # Add functions as operations
        for func in spec.functions:
            name = func.get("name", "unknown")
            lines.append(f":{name} a :Operation ;")
            if func.get("description"):
                lines.append(f'  rdfs:comment "{func["description"]}" ;')
            lines.append("  .")
            lines.append("")

        return "\n".join(lines)
