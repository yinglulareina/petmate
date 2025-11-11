#!/usr/bin/env python3
"""
Pre-Commit GitIgnore Safety Check for PetMate Project

This script validates .gitignore BEFORE you commit, preventing sensitive
files from being accidentally tracked. Run this after 'git add' but
BEFORE 'git commit'.

Usage:
    python scripts/check_gitignore.py

Author: PetMate Team
Date: November 2025
"""

import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def run_git_command(command):
    """
    Run a git command and return the output.

    Args:
        command (list): Git command as list of strings

    Returns:
        str: Command output
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_staged_files():
    """
    Get list of files that are staged (ready to commit).

    Returns:
        list: List of staged file paths
    """
    output = run_git_command(['git', 'diff', '--cached', '--name-only'])
    if output:
        return output.split('\n')
    return []


def get_untracked_files():
    """
    Get list of untracked files in working directory.

    Returns:
        list: List of untracked file paths
    """
    output = run_git_command(['git', 'ls-files', '--others', '--exclude-standard'])
    if output:
        return output.split('\n')
    return []


def check_path_exists(path):
    """Check if a path exists"""
    return Path(path).exists()


def print_section(title):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def is_dangerous_file(filename):
    """
    Check if a file is dangerous and should never be committed.
    Returns (is_dangerous, reason)
    """
    # CRITICAL: Exact matches for .env files
    # .env.example is safe (template), .env is dangerous (real keys)
    if filename == '.env':
        return True, 'Environment variables (CONTAINS REAL API KEYS!)'

    if filename == '.env.local':
        return True, 'Local environment variables'

    # Dangerous patterns (substring or extension match)
    dangerous_patterns = {
        # Virtual environments
        '.venv/': 'Virtual environment',
        'venv/': 'Virtual environment',
        'env/': 'Virtual environment',

        # IDE files
        '.idea/': 'PyCharm settings',
        '.vscode/': 'VS Code settings',

        # Python cache
        '__pycache__/': 'Python cache',
        '.pyc': 'Python bytecode',

        # Secrets
        '.streamlit/secrets.toml': 'Streamlit secrets',
        '.secrets': 'Secret files',
        '.key': 'Key files',
        '.pem': 'Certificate files',

        # Team documentation (local only)
        'CODING_STANDARDS.md': 'Team coding standards (local reference)',
        'TERMINOLOGY_GUIDE.md': 'Team terminology guide (local reference)',

        # OS files
        '.DS_Store': 'macOS system file',
        'Thumbs.db': 'Windows thumbnail',

        # Testing
        '.pytest_cache/': 'Pytest cache',
        '.coverage': 'Coverage data',
        'htmlcov/': 'Coverage HTML report',

        # Logs
        '.log': 'Log files',
    }

    # Check patterns
    for pattern, reason in dangerous_patterns.items():
        if pattern in filename or filename.endswith(pattern.rstrip('/')):
            return True, reason

    return False, ''


def main():
    """Main validation function"""

    print_section("🛡️  PetMate Pre-Commit Safety Check")

    # Check if we're in a git repository
    if not Path('.git').exists():
        print_error("Not a git repository! Run 'git init' first.")
        sys.exit(1)

    # Check if .gitignore exists
    if not Path('.gitignore').exists():
        print_error(".gitignore file not found!")
        sys.exit(1)

    print_success(".gitignore file exists")

    # Define files that SHOULD be committed
    important_files = [
        ('README.md', 'Project documentation'),
        ('requirements.txt', 'Python dependencies'),
        ('.gitignore', 'Git ignore rules'),
        ('.env.example', 'Environment variables template (SAFE - no real keys)'),
    ]

    errors = 0
    warnings = 0

    # Get current git state
    staged_files = get_staged_files()
    untracked_files = get_untracked_files()

    # Test 1: Check staged files for dangerous patterns
    print_section("Test 1: 🚨 Checking Staged Files (About to Commit)")

    if not staged_files:
        print_info("No files are staged for commit yet.")
        print_info("Run 'git add <file>' to stage files, then run this check again.")
    else:
        print(f"Found {len(staged_files)} staged file(s):\n")

        dangerous_found = False

        for staged_file in staged_files:
            is_dangerous, danger_reason = is_dangerous_file(staged_file)

            if is_dangerous:
                print_error(f"{staged_file}")
                print(f"         ⚠️  DANGER: {danger_reason}")
                print(f"         ACTION: Remove with 'git reset HEAD {staged_file}'")
                errors += 1
                dangerous_found = True
            else:
                print_success(f"{staged_file}")

        if not dangerous_found:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All staged files look safe!{Colors.END}\n")

    # Test 2: Check working directory for files that should be ignored
    print_section("Test 2: 📂 Checking Working Directory")

    # Check for dangerous files that exist
    dangerous_files_to_check = [
        '.env',
        '.env.local',
        '.venv/',
        'venv/',
        '.idea/',
        '__pycache__/',
        '.DS_Store',
        'CODING_STANDARDS.md',
        'TERMINOLOGY_GUIDE.md',
    ]

    found_sensitive = False
    for file_path in dangerous_files_to_check:
        if check_path_exists(file_path.rstrip('/')):
            found_sensitive = True
            if file_path in staged_files or file_path.rstrip('/') in staged_files:
                print_error(f"{file_path} exists and is STAGED for commit!")
                errors += 1
            elif file_path not in untracked_files:
                print_success(f"{file_path} is properly ignored")
            else:
                print_warning(f"{file_path} exists but is untracked (should add to .gitignore)")

    if not found_sensitive:
        print_info("No sensitive files found in working directory (this is good)")

    # Test 3: Verify important files are ready
    print_section("Test 3: 📋 Checking Important Files")

    for file_path, description in important_files:
        exists = check_path_exists(file_path)
        is_staged = file_path in staged_files

        if not exists:
            print_warning(f"{file_path} ({description}) doesn't exist yet")
            warnings += 1
        elif is_staged:
            print_success(f"{file_path} ({description}) is staged ✓")
        else:
            print_info(f"{file_path} ({description}) exists but not staged")

    # Test 4: Check for placeholder files in empty directories
    print_section("Test 4: 📁 Checking Directory Structure")

    required_dirs = [
        ('src/', '__init__.py', 'Source code'),
        ('tests/', '__init__.py', 'Tests'),
        ('data/', '.gitkeep', 'Data files'),
        ('app/', '.gitkeep', 'Application'),
    ]

    for dir_path, placeholder, description in required_dirs:
        dir_exists = check_path_exists(dir_path)
        placeholder_path = dir_path + placeholder
        placeholder_exists = check_path_exists(placeholder_path)
        placeholder_staged = placeholder_path in staged_files

        if not dir_exists:
            print_warning(f"{dir_path} ({description}) doesn't exist yet")
            warnings += 1
        elif not placeholder_exists:
            print_warning(f"{dir_path} exists but {placeholder} is missing")
            print(f"         Create with: touch {placeholder_path}")
            warnings += 1
        elif placeholder_staged:
            print_success(f"{placeholder_path} is staged ✓")
        else:
            print_info(f"{placeholder_path} exists but not staged yet")

    # Final Summary
    print_section("📊 Safety Check Summary")

    print(f"Errors:   {Colors.RED}{errors}{Colors.END}")
    print(f"Warnings: {Colors.YELLOW}{warnings}{Colors.END}")
    print(f"Staged:   {len(staged_files)} file(s)")

    print()

    if errors > 0:
        print(f"{Colors.RED}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}🚨 DANGER! DO NOT COMMIT!{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"\n{Colors.RED}Found {errors} critical issue(s) that could leak sensitive data.{Colors.END}")
        print(f"{Colors.RED}Fix the errors above before committing.{Colors.END}\n")

        print(f"{Colors.YELLOW}Quick fix commands:{Colors.END}")
        print(f"  git reset HEAD <file>    # Unstage a specific file")
        print(f"  git reset HEAD .         # Unstage all files")
        print()
        return 1

    elif len(staged_files) == 0:
        print(f"{Colors.YELLOW}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  No files staged for commit{Colors.END}")
        print(f"{Colors.YELLOW}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"\n{Colors.YELLOW}No files are ready to commit yet.{Colors.END}\n")

        print(f"{Colors.BLUE}Next steps:{Colors.END}")
        print(f"  1. Stage files:  git add <file>")
        print(f"  2. Run check:    python scripts/check_gitignore.py")
        print(f"  3. If safe:      git commit -m 'your message'")
        print()
        return 0

    else:
        print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SAFE TO COMMIT!{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"\n{Colors.GREEN}All staged files passed safety checks.{Colors.END}")

        if warnings > 0:
            print(f"{Colors.YELLOW}Note: {warnings} warning(s) found, but they won't block commit.{Colors.END}")

        print(f"\n{Colors.GREEN}You can now safely commit:{Colors.END}")
        print(f"  git commit -m 'your commit message'")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())