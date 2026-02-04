"""
Impact Analyzer for GravityHook (Optional)

Analyzes structural impact of code changes before execution.
Detects Pydantic models and predicts which components will be affected.
"""

from pathlib import Path
from typing import List, Set, Dict, Optional
from pydantic import BaseModel, Field
import ast
import re


class ModelField(BaseModel):
    """Represents a field in a Pydantic model"""
    name: str
    type_annotation: str
    is_optional: bool = False
    has_default: bool = False


class ModelDefinition(BaseModel):
    """Represents a Pydantic model class"""
    name: str
    file_path: Path
    line_number: int
    fields: List[ModelField] = Field(default_factory=list)
    base_classes: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


class ImpactReport(BaseModel):
    """Report of structural impact analysis"""
    target_file: Path
    affected_models: List[ModelDefinition] = Field(default_factory=list)
    usage_locations: Dict[str, List[str]] = Field(default_factory=dict)  # model_name -> [file_paths]
    risk_level: str = "low"  # low, medium, high
    
    class Config:
        arbitrary_types_allowed = True


def scan_pydantic_models(directory: Path) -> List[ModelDefinition]:
    """
    Scan directory for Pydantic model definitions using AST parsing.
    
    Args:
        directory: Root directory to scan for Python files
    
    Returns:
        List of ModelDefinition objects found in the directory
    
    Example:
        >>> models = scan_pydantic_models(Path("backend/models"))
        >>> for model in models:
        ...     print(f"{model.name} in {model.file_path}")
    """
    models = []
    
    for python_file in directory.rglob("*.py"):
        try:
            with open(python_file, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            file_models = _extract_models_from_ast(tree, python_file)
            models.extend(file_models)
        except Exception as e:
            # Skip files that can't be parsed
            continue
    
    return models


def _extract_models_from_ast(tree: ast.AST, file_path: Path) -> List[ModelDefinition]:
    """Extract Pydantic model definitions from AST."""
    models = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if class inherits from BaseModel
            base_names = [_get_name(base) for base in node.bases]
            
            if any('BaseModel' in name for name in base_names):
                model = ModelDefinition(
                    name=node.name,
                    file_path=file_path,
                    line_number=node.lineno,
                    base_classes=base_names
                )
                
                # Extract fields
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field = ModelField(
                            name=item.target.id,
                            type_annotation=ast.unparse(item.annotation) if hasattr(ast, 'unparse') else str(item.annotation),
                            has_default=item.value is not None
                        )
                        
                        # Check if Optional
                        field.is_optional = 'Optional' in field.type_annotation
                        
                        model.fields.append(field)
                
                models.append(model)
    
    return models


def _get_name(node: ast.AST) -> str:
    """Get name from AST node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_get_name(node.value)}.{node.attr}"
    else:
        return ""


def analyze_impact(
    file_path: Path,
    workspace_root: Path,
    proposed_changes: Optional[str] = None
) -> ImpactReport:
    """
    Analyze the impact of changes to a specific file.
    
    Args:
        file_path: Path to the file being modified
        workspace_root: Root directory of the workspace
        proposed_changes: Optional description of proposed changes
    
    Returns:
        ImpactReport with affected models and usage locations
    
    Example:
        >>> report = analyze_impact(
        ...     Path("backend/models/user.py"),
        ...     Path("."),
        ...     "Changing User.email from str to EmailStr"
        ... )
        >>> print(f"Risk level: {report.risk_level}")
        >>> for model in report.affected_models:
        ...     print(f"  Affects: {model.name}")
    """
    report = ImpactReport(target_file=file_path)
    
    # Find models in the target file
    if file_path.exists() and file_path.suffix == '.py':
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
            report.affected_models = _extract_models_from_ast(tree, file_path)
        except:
            pass
    
    # Search for usage of these models across the workspace
    for model in report.affected_models:
        usage_files = _find_model_usages(model.name, workspace_root)
        report.usage_locations[model.name] = usage_files
    
    # Determine risk level
    total_usages = sum(len(files) for files in report.usage_locations.values())
    
    if total_usages == 0:
        report.risk_level = "low"
    elif total_usages <= 5:
        report.risk_level = "medium"
    else:
        report.risk_level = "high"
    
    return report


def _find_model_usages(model_name: str, workspace_root: Path) -> List[str]:
    """
    Find files that import or use a specific model.
    
    Uses simple text search (grep-like) to find references.
    """
    usage_files = set()
    
    for python_file in workspace_root.rglob("*.py"):
        try:
            with open(python_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for imports or direct usage
            if re.search(rf'\b{model_name}\b', content):
                usage_files.add(str(python_file.relative_to(workspace_root)))
        except:
            continue
    
    return sorted(list(usage_files))


def print_impact_report(report: ImpactReport) -> str:
    """
    Generate human-readable impact analysis report.
    
    Returns:
        Formatted string with impact analysis
    """
    lines = []
    lines.append("🔍 Structural Impact Analysis")
    lines.append("=" * 50)
    lines.append(f"Target File: {report.target_file}")
    lines.append(f"Risk Level: {report.risk_level.upper()}")
    lines.append("")
    
    if not report.affected_models:
        lines.append("ℹ️ No Pydantic models found in target file")
        return "\n".join(lines)
    
    lines.append(f"📦 Affected Models ({len(report.affected_models)}):")
    for model in report.affected_models:
        lines.append(f"\n  • {model.name} (Line {model.line_number})")
        lines.append(f"    Fields: {len(model.fields)}")
        
        if model.name in report.usage_locations:
            usage_count = len(report.usage_locations[model.name])
            lines.append(f"    Used in: {usage_count} files")
            
            if usage_count > 0 and usage_count <= 5:
                for usage_file in report.usage_locations[model.name]:
                    lines.append(f"      - {usage_file}")
            elif usage_count > 5:
                lines.append(f"      (showing first 5)")
                for usage_file in report.usage_locations[model.name][:5]:
                    lines.append(f"      - {usage_file}")
    
    lines.append("")
    
    risk_warnings = {
        "low": "✅ Low risk - proceed with confidence",
        "medium": "⚠️ Medium risk - review usage locations",
        "high": "🚨 High risk - extensive impact, careful review required"
    }
    lines.append(risk_warnings.get(report.risk_level, "❓ Unknown risk"))
    
    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Test scanning current directory
    models = scan_pydantic_models(Path("."))
    print(f"Found {len(models)} Pydantic models")
    
    for model in models:
        print(f"\n{model.name}:")
        for field in model.fields:
            optional_mark = "?" if field.is_optional else ""
            print(f"  - {field.name}: {field.type_annotation}{optional_mark}")
