#!/usr/bin/env python3
"""
Automated quality check tool for GravityHook repositories.
Parses vibe_check.md and executes automated verification tasks.
"""

import argparse
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any


def parse_vibe_check(vibe_check_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parse vibe_check.md and categorize items into automated vs manual.
    
    Returns:
        {
            "automated": [{"item": str, "command": str, "type": "command|file_exists"}],
            "manual": [{"item": str}]
        }
    """
    if not vibe_check_path.exists():
        raise FileNotFoundError(f"vibe_check.md not found at {vibe_check_path}")
    
    content = vibe_check_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    automated = []
    manual = []
    
    # Regex patterns
    command_pattern = re.compile(r"^- \[ \] (.+?) \(`(.+?)`\)$")
    file_exists_pattern = re.compile(r"^- \[ \] File exists: (.+)$")
    manual_pattern = re.compile(r"^- \[ \] (.+)$")
    
    for line in lines:
        # Check for command-based automation
        match = command_pattern.match(line)
        if match:
            item_desc = match.group(1)
            command = match.group(2)
            automated.append({
                "item": item_desc,
                "command": command,
                "type": "command"
            })
            continue
        
        # Check for file existence
        match = file_exists_pattern.match(line)
        if match:
            file_path = match.group(1)
            automated.append({
                "item": f"File exists: {file_path}",
                "file_path": file_path,
                "type": "file_exists"
            })
            continue
        
        # Manual item (no automation syntax)
        match = manual_pattern.match(line)
        if match:
            item_desc = match.group(1)
            # Exclude items that are already captured (edge case)
            if not any(cmd in item_desc for cmd in ["`", "File exists:"]):
                manual.append({"item": item_desc})
    
    return {"automated": automated, "manual": manual}


def run_command_check(item: Dict[str, Any], repo_path: Path) -> Dict[str, Any]:
    """Execute a command-based check and return result."""
    command = item["command"]
    result = {
        "item": item["item"],
        "command": command,
        "status": "unknown",
        "output": ""
    }
    
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60  # 60s timeout
        )
        
        result["output"] = proc.stdout.strip() if proc.stdout else proc.stderr.strip()
        result["status"] = "pass" if proc.returncode == 0 else "fail"
        result["return_code"] = proc.returncode
        
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["output"] = "Command execution exceeded 60 second timeout"
    except Exception as e:
        result["status"] = "error"
        result["output"] = f"Exception during execution: {str(e)}"
    
    return result


def check_file_exists(item: Dict[str, Any], repo_path: Path) -> Dict[str, Any]:
    """Check if a file exists."""
    file_path = Path(repo_path) / item["file_path"]
    result = {
        "item": item["item"],
        "file_path": str(file_path),
        "status": "pass" if file_path.exists() else "fail",
        "output": f"File exists: {file_path.exists()}"
    }
    return result


def identify_agent_review_items(manual_items: List[Dict[str, Any]], repo_path: Path) -> List[Dict[str, Any]]:
    """
    Analyze manual items and provide context for agent review.
    """
    review_items = []
    
    for item in manual_items:
        item_text = item["item"].lower()
        context = {}
        
        # Async-first principles
        if "async" in item_text:
            context = {
                "item": item["item"],
                "files_to_check": ["engines/*.py", "main.py"],
                "rule_reference": ".agent/rules/claw_rules.md#async-first-approach"
            }
        
        # Strong typing
        elif "strong typing" in item_text or "pydantic" in item_text:
            context = {
                "item": item["item"],
                "files_to_check": ["models.py", "**/*.py"],
                "rule_reference": ".agent/rules/claw_rules.md#strong-typing"
            }
        
        # Hardcoded values
        elif "hardcoded" in item_text or "magic number" in item_text:
            context = {
                "item": item["item"],
                "files_to_check": ["**/*.py"],
                "rule_reference": ".agent/rules/claw_rules.md#code-quality-standards"
            }
        
        # Error handling
        elif "error handling" in item_text:
            context = {
                "item": item["item"],
                "files_to_check": ["**/*.py"],
                "rule_reference": ".agent/rules/claw_rules.md#error-handling"
            }
        
        # Docstrings
        elif "docstring" in item_text:
            context = {
                "item": item["item"],
                "files_to_check": ["**/*.py"],
                "rule_reference": ".agent/rules/claw_rules.md#code-quality-standards"
            }
        
        # MISSION_STATE updated
        elif "mission_state" in item_text:
            try:
                mission_state_path = repo_path / ".agent" / "MISSION_STATE.md"
                if mission_state_path.exists():
                    last_modified = datetime.fromtimestamp(
                        mission_state_path.stat().st_mtime,
                        tz=timezone.utc
                    ).isoformat()
                else:
                    last_modified = "File not found"
            except Exception:
                last_modified = "Error reading file"
            
            context = {
                "item": item["item"],
                "last_modified": last_modified,
                "instruction": "Compare MISSION_STATE.md last entry with latest git commit"
            }
        
        # User input sanitization
        elif "sanitiz" in item_text or "user input" in item_text:
            context = {
                "item": item["item"],
                "files_to_check": ["ui/*.py", "engines/*.py"],
                "rule_reference": ".agent/rules/project_rules.md#security-requirements"
            }
        
        # Database indexes (manual review)
        elif "database" in item_text and "index" in item_text:
            context = {
                "item": item["item"],
                "instruction": "Manually review database schema and query patterns"
            }
        
        # Generic manual item
        else:
            context = {
                "item": item["item"],
                "instruction": "Manual review required (no automated check available)"
            }
        
        review_items.append(context)
    
    return review_items


def main():
    parser = argparse.ArgumentParser(
        description="Automated quality check for GravityHook repositories"
    )
    parser.add_argument(
        "--vibe-check",
        type=Path,
        required=True,
        help="Path to vibe_check.md"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/vibe_report.json"),
        help="Path to output JSON report"
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Parse vibe_check.md
    print(f"📋 Parsing {args.vibe_check}...")
    parsed = parse_vibe_check(args.vibe_check)
    
    # Execute automated checks
    print(f"🤖 Running {len(parsed['automated'])} automated checks...")
    automated_results = []
    
    for item in parsed["automated"]:
        if item["type"] == "command":
            result = run_command_check(item, args.repo_path)
        elif item["type"] == "file_exists":
            result = check_file_exists(item, args.repo_path)
        else:
            result = {"item": item["item"], "status": "unknown", "output": "Unknown check type"}
        
        automated_results.append(result)
        status_icon = "✅" if result["status"] == "pass" else "❌" if result["status"] == "fail" else "⚠️"
        print(f"  {status_icon} {result['item']}: {result['status']}")
    
    # Identify agent review items
    print(f"🧠 Identifying {len(parsed['manual'])} items for agent review...")
    agent_review_items = identify_agent_review_items(parsed["manual"], args.repo_path)
    
    # Generate summary
    passed = sum(1 for r in automated_results if r["status"] == "pass")
    failed = sum(1 for r in automated_results if r["status"] == "fail")
    total_items = len(parsed["automated"]) + len(parsed["manual"])
    
    summary = {
        "total_items": total_items,
        "automated": len(automated_results),
        "passed": passed,
        "failed": failed,
        "pending": len(agent_review_items)
    }
    
    # Build final report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo_path": str(args.repo_path.resolve()),
        "vibe_check_path": str(args.vibe_check.resolve()),
        "automated": automated_results,
        "agent_review_needed": agent_review_items,
        "summary": summary
    }
    
    # Write JSON report
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"📊 Report saved to {args.output}")
    print(f"📈 Summary: {passed}/{len(automated_results)} automated checks passed")
    print(f"🧠 {len(agent_review_items)} items require agent review")
    
    return 0


if __name__ == "__main__":
    exit(main())
