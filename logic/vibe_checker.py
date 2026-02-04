"""
Vibe Checker for GravityHook

Parses and executes verification checklist from vibe_check.md.
Automates post-development validation and triggers mission state updates.
"""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
from pydantic import BaseModel, Field
from enum import Enum
import subprocess
import re


class CheckType(str, Enum):
    """Type of verification check"""
    COMMAND = "command"  # Shell command execution
    FILE_EXISTS = "file_exists"  # Check if file exists
    MANUAL = "manual"  # Requires manual verification


class CheckStatus(str, Enum):
    """Status of a check item"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CheckItem(BaseModel):
    """Individual check item from vibe_check.md"""
    description: str
    check_type: CheckType = CheckType.MANUAL
    command: Optional[str] = None
    expected_return_code: int = 0
    status: CheckStatus = CheckStatus.PENDING


class CheckResult(BaseModel):
    """Result of running vibe check"""
    total_checks: int
    passed: int
    failed: int
    skipped: int
    items: List[CheckItem]
    all_passed: bool = False
    
    def __init__(self, **data):
        super().__init__(**data)
        self.all_passed = self.failed == 0 and self.passed == self.total_checks


def parse_vibe_check(vibe_check_path: Path) -> List[CheckItem]:
    """
    Parse vibe_check.md and extract checklist items.
    
    Supports markdown checklist format:
    - [ ] Description
    - [x] Completed item
    
    Also supports special syntax for automated checks:
    - [ ] Run tests (`pytest`)
    - [ ] File exists: src/main.py
    
    Args:
        vibe_check_path: Path to vibe_check.md file
    
    Returns:
        List of CheckItem objects
    """
    if not vibe_check_path.exists():
        return []
    
    with open(vibe_check_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    check_items = []
    
    # Match checkbox items: - [ ] or - [x]
    checkbox_pattern = r'^- \[([ x])\] (.+)$'
    
    for line in content.split('\n'):
        match = re.match(checkbox_pattern, line.strip())
        if match:
            is_checked = match.group(1) == 'x'
            description = match.group(2)
            
            # Parse check type from description
            check_item = _parse_check_description(description)
            
            if is_checked:
                check_item.status = CheckStatus.PASSED
            
            check_items.append(check_item)
    
    return check_items


def _parse_check_description(description: str) -> CheckItem:
    """
    Parse check description to determine type and extract command.
    
    Patterns:
    - "Run tests (`pytest`)" -> command check
    - "File exists: path/to/file" -> file existence check
    - "Manual verification needed" -> manual check
    """
    # Check for command in backticks
    command_match = re.search(r'`([^`]+)`', description)
    if command_match:
        return CheckItem(
            description=description,
            check_type=CheckType.COMMAND,
            command=command_match.group(1)
        )
    
    # Check for file existence pattern
    file_match = re.search(r'[Ff]ile exists?:?\s*(.+)', description)
    if file_match:
        return CheckItem(
            description=description,
            check_type=CheckType.FILE_EXISTS,
            command=file_match.group(1).strip()
        )
    
    # Default to manual check
    return CheckItem(
        description=description,
        check_type=CheckType.MANUAL
    )


def perform_vibe_check(vibe_check_path: Path, auto_run: bool = False) -> CheckResult:
    """
    Execute vibe check verification.
    
    Args:
        vibe_check_path: Path to vibe_check.md
        auto_run: If True, automatically run command checks. If False, only parse.
    
    Returns:
        CheckResult with status of all checks
    
    Example:
        >>> result = perform_vibe_check(Path(".agent/vibe_check.md"), auto_run=True)
        >>> if result.all_passed:
        ...     print("All checks passed!")
        ... else:
        ...     print(f"Failed: {result.failed}/{result.total_checks}")
    """
    check_items = parse_vibe_check(vibe_check_path)
    
    if auto_run:
        for item in check_items:
            if item.status == CheckStatus.PASSED:
                continue  # Already marked as passed
            
            if item.check_type == CheckType.COMMAND:
                item.status = _run_command_check(item)
            elif item.check_type == CheckType.FILE_EXISTS:
                item.status = _check_file_exists(item)
            else:
                # Manual checks remain pending
                pass
    
    # Calculate statistics
    total = len(check_items)
    passed = sum(1 for item in check_items if item.status == CheckStatus.PASSED)
    failed = sum(1 for item in check_items if item.status == CheckStatus.FAILED)
    skipped = sum(1 for item in check_items if item.status == CheckStatus.SKIPPED)
    
    return CheckResult(
        total_checks=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        items=check_items
    )


def _run_command_check(item: CheckItem) -> CheckStatus:
    """Execute shell command and check return code."""
    if not item.command:
        return CheckStatus.SKIPPED
    
    try:
        result = subprocess.run(
            item.command,
            shell=True,
            capture_output=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == item.expected_return_code:
            return CheckStatus.PASSED
        else:
            return CheckStatus.FAILED
    except subprocess.TimeoutExpired:
        return CheckStatus.FAILED
    except Exception:
        return CheckStatus.FAILED


def _check_file_exists(item: CheckItem) -> CheckStatus:
    """Check if specified file exists."""
    if not item.command:
        return CheckStatus.SKIPPED
    
    file_path = Path(item.command)
    
    if file_path.exists():
        return CheckStatus.PASSED
    else:
        return CheckStatus.FAILED


def print_check_result(result: CheckResult) -> str:
    """
    Generate human-readable report of vibe check results.
    
    Returns:
        Formatted string with check results
    """
    lines = []
    lines.append("✨ Vibe Check Results")
    lines.append("=" * 50)
    lines.append(f"Total: {result.total_checks} | ✅ Passed: {result.passed} | ❌ Failed: {result.failed} | ⏭️ Skipped: {result.skipped}")
    lines.append("")
    
    for item in result.items:
        status_icons = {
            CheckStatus.PASSED: "✅",
            CheckStatus.FAILED: "❌",
            CheckStatus.PENDING: "⏸️",
            CheckStatus.SKIPPED: "⏭️"
        }
        icon = status_icons.get(item.status, "❓")
        lines.append(f"{icon} {item.description}")
        
        if item.status == CheckStatus.FAILED and item.command:
            lines.append(f"   Command: `{item.command}`")
    
    lines.append("")
    
    if result.all_passed:
        lines.append("🎉 All checks passed! Ready to update mission state.")
    else:
        lines.append("⚠️ Some checks need attention. Review failed items.")
    
    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Create a test vibe_check.md
    test_vibe_check = Path("test_vibe_check.md")
    
    test_content = """# Vibe Check: Post-Development Verification

- [x] Project structure created
- [ ] All unit tests pass (`pytest`)
- [ ] File exists: requirements.txt
- [ ] Code follows async-first principles (manual review)
- [ ] Documentation updated
"""
    
    with open(test_vibe_check, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    result = perform_vibe_check(test_vibe_check, auto_run=True)
    print(print_check_result(result))
