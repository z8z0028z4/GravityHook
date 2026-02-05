#!/bin/bash
# GravityHook Installation Script for Linux/macOS
# Usage: ./install.sh /path/to/target/project

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🪝 GravityHook Installer${NC}"
echo "================================"

# Check if target directory is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 /path/to/target/project${NC}"
    read -p "Enter target project directory: " TARGET_DIR
else
    TARGET_DIR="$1"
fi

# Validate target directory
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}Directory does not exist: $TARGET_DIR${NC}"
    read -p "Create it? (y/n): " CREATE_DIR
    if [ "$CREATE_DIR" = "y" ]; then
        mkdir -p "$TARGET_DIR"
        echo -e "${GREEN}✓${NC} Created directory: $TARGET_DIR"
    else
        echo "Installation cancelled."
        exit 1
    fi
fi

# Get absolute path
TARGET_DIR=$(cd "$TARGET_DIR" && pwd)
AGENT_DIR="$TARGET_DIR/.agent"

echo ""
echo "Target project: $TARGET_DIR"
echo "Installing GravityHook to: $AGENT_DIR"
echo ""

# Create .agent directory structure
echo -e "${BLUE}Creating directory structure...${NC}"
mkdir -p "$AGENT_DIR/rules"
mkdir -p "$AGENT_DIR/workflows"
mkdir -p "$AGENT_DIR/skills"
echo -e "${GREEN}✓${NC} Created .agent/ directories"

# Get script directory (where install.sh is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy templates
echo -e "${BLUE}Copying templates...${NC}"

if [ ! -f "$AGENT_DIR/MISSION_STATE.md" ]; then
    cp "$SCRIPT_DIR/templates/MISSION_STATE.md" "$AGENT_DIR/"
    echo -e "${GREEN}✓${NC} Copied MISSION_STATE.md"
else
    echo -e "${YELLOW}⚠${NC} MISSION_STATE.md already exists, skipping"
fi

if [ ! -f "$AGENT_DIR/vibe_check.md" ]; then
    cp "$SCRIPT_DIR/templates/vibe_check.md" "$AGENT_DIR/"
    echo -e "${GREEN}✓${NC} Copied vibe_check.md"
else
    echo -e "${YELLOW}⚠${NC} vibe_check.md already exists, skipping"
fi

if [ ! -f "$AGENT_DIR/rules/claw_rules.md" ]; then
    cp "$SCRIPT_DIR/templates/claw_rules.md" "$AGENT_DIR/rules/"
    echo -e "${GREEN}✓${NC} Copied claw_rules.md to .agent/rules/"
else
    echo -e "${YELLOW}⚠${NC} claw_rules.md already exists, skipping"
fi

if [ ! -f "$AGENT_DIR/skills/SKILL_INDEX.md" ]; then
    cp "$SCRIPT_DIR/templates/SKILL_INDEX.md" "$AGENT_DIR/skills/"
    echo -e "${GREEN}✓${NC} Copied SKILL_INDEX.md to .agent/skills/"
else
    echo -e "${YELLOW}⚠${NC} SKILL_INDEX.md already exists, skipping"
fi

echo ""
echo -e "${BLUE}ℹ${NC} SYSTEM_PROMPT.md is available in GravityHook/templates/"
echo -e "${BLUE}ℹ${NC} Copy its content to your OpenClaw Project's Custom Instructions"

# Copy Python logic modules (optional)
echo ""
read -p "Copy Python logic modules to project? (y/n): " COPY_LOGIC
if [ "$COPY_LOGIC" = "y" ]; then
    mkdir -p "$TARGET_DIR/gravityhook_logic"
    cp -r "$SCRIPT_DIR/logic/"* "$TARGET_DIR/gravityhook_logic/"
    echo -e "${GREEN}✓${NC} Copied Python modules to gravityhook_logic/"
    
    # Copy requirements.txt
    if [ ! -f "$TARGET_DIR/requirements.txt" ]; then
        cp "$SCRIPT_DIR/requirements.txt" "$TARGET_DIR/"
        echo -e "${GREEN}✓${NC} Copied requirements.txt"
    else
        echo -e "${YELLOW}⚠${NC} requirements.txt exists. Add these dependencies:"
        cat "$SCRIPT_DIR/requirements.txt"
    fi
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ GravityHook installed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Created structure:"
echo "  $AGENT_DIR/"
echo "  ├── MISSION_STATE.md"
echo "  ├── vibe_check.md"
echo "  ├── rules/"
echo "  │   └── claw_rules.md"
echo "  ├── workflows/"
echo "  └── skills/"
echo ""
echo "Next steps:"
echo "1. Customize .agent/rules/claw_rules.md for your project"
echo "2. Update .agent/MISSION_STATE.md with your current mission"
echo "3. Edit .agent/vibe_check.md to add project-specific checks"
echo ""
echo "For OpenClaw integration, see: $SCRIPT_DIR/SKILL_MANIFEST.md"
echo ""
echo -e "${BLUE}Happy coding! 🚀${NC}"
