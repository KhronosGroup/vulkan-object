# #!/usr/bin/env python3 -i
#
# Copyright 2025 The Khronos Group Inc.
# SPDX-License-Identifier: Apache-2.0

# This file is used to automatically take the Vulkan-Headers and update this repo to match it

import re
import shutil
import argparse
from pathlib import Path

DEST_DIR = Path("src/vulkan_object")
PYPROJECT_PATH = Path("pyproject.toml")
# These are the known, top-level modules in the registry that might be imported.
# We'll use this list to dynamically find and fix relative imports.
KNOWN_MODULES = [
    'apiconventions', 'base_generator', 'cgenerator', 'generator',
    'reg', 'stripAPI', 'vkconventions', 'vulkan_object',
    'parse_dependency', 'spec_tools'
]

def get_vulkan_header_version(registry_path: Path) -> str:
    """
    Parses the Vulkan header version from vk.xml using the VK_MAKE_API_VERSION macro.
    """
    vk_xml_path = registry_path / "vk.xml"
    if not vk_xml_path.is_file():
        raise FileNotFoundError(f"Could not find vk.xml at {vk_xml_path}")

    content = vk_xml_path.read_text(encoding='utf-8')

    # 1. Find the patch number for the core Vulkan API based on the first occurrence.
    # Simplified regex based on the assumption it will be in the format:
    # <name>VK_HEADER_VERSION</name> 318</type>
    patch_match = re.search(
        r'<name>VK_HEADER_VERSION</name>\s*(\d+)</type>',
        content
    )
    if not patch_match:
        raise ValueError("Could not find the patch version from VK_HEADER_VERSION in vk.xml")
    patch_version = patch_match.group(1)

    # 2. Find the major and minor version from the first VK_HEADER_VERSION_COMPLETE macro.
    # Simplified regex based on the assumption it will be in the format:
    # <name>VK_HEADER_VERSION_COMPLETE</name> <type>VK_MAKE_API_VERSION</type>(0, 1, 4, VK_HEADER_VERSION)</type>
    version_complete_match = re.search(
        r'<name>VK_HEADER_VERSION_COMPLETE</name>\s*<type>VK_MAKE_API_VERSION</type>\s*\(\s*0,\s*(\d+),\s*(\d+),',
        content
    )
    if not version_complete_match:
        raise ValueError("Could not find VK_HEADER_VERSION_COMPLETE macro for api='vulkan' in vk.xml")

    major_version = version_complete_match.group(1)
    minor_version = version_complete_match.group(2)

    return f"{major_version}.{minor_version}.{patch_version}"


def update_pyproject_version(version: str):
    """Updates the version in pyproject.toml."""
    if not PYPROJECT_PATH.is_file():
        print(f"Warning: {PYPROJECT_PATH} not found. Skipping version update.")
        return

    print(f"Updating package version to {version} in {PYPROJECT_PATH}...")
    content = PYPROJECT_PATH.read_text()

    # Use a simpler regex to find and replace the version line.
    # This captures the part before the version number (group 1) and replaces
    # the existing version number with the new one.
    new_content, num_subs = re.subn(
        r'^(version\s*=\s*").*(")',      # Find lines starting with version = "..."
        rf'\g<1>{version}\g<2>',         # Rebuild the line with the new version
        content,
        flags=re.MULTILINE              # Ensure '^' matches the start of each line
    )

    if num_subs == 0:
        print("Warning: Could not find 'version = ...' line in pyproject.toml. Skipping update.")
        return

    PYPROJECT_PATH.write_text(new_content)
    print("...Done.")


def copy_registry_files(source_path: Path):
    """Copies all files and directories from the source registry to the destination."""
    if not DEST_DIR.exists():
        print(f"Destination directory {DEST_DIR} does not exist. Creating it.")
        DEST_DIR.mkdir(parents=True)

    print(f"Copying files from {source_path} to {DEST_DIR}...")
    for item in source_path.iterdir():
        dest_item = DEST_DIR / item.name
        if item.is_dir():
            if dest_item.exists():
                shutil.rmtree(dest_item)
            shutil.copytree(item, dest_item)
        else:
            shutil.copy2(item, dest_item)
    print("...Done copying files.")


def fix_relative_imports():
    """
    Scans all .py files in the destination directory and converts absolute
    imports of known local modules to relative imports.
    """
    print("Fixing imports to be package-relative...")
    # Create a regex pattern like: from (apiconventions|base_generator|...)
    module_pattern = "|".join(KNOWN_MODULES)

    # This more robust regex finds 'from <module>' at the start of a line
    # (with optional indentation) and uses a word boundary (\b) to ensure
    # it doesn't match modules with similar prefixes (e.g., 'generators').
    pattern = re.compile(
        rf"^(\s*from\s+)({module_pattern})\b",
        re.MULTILINE
    )

    file_count = 0
    for py_file in DEST_DIR.glob("*.py"):
        content = py_file.read_text()
        # The replacement adds a dot right after 'from ', converting the import
        # to a relative one, e.g., 'from generator' -> 'from .generator'
        new_content, num_subs = pattern.subn(r"\g<1>.\g<2>", content)
        if num_subs > 0:
            py_file.write_text(new_content)
            file_count += 1
            print(f"  - Patched imports in {py_file.name}")

    if file_count == 0:
        print("  - No files needed import patching.")
    print("...Done fixing imports.")


def main():
    """Main script execution."""
    parser = argparse.ArgumentParser(
        description="Update the vulkan_object package from a Vulkan-Headers repository checkout."
    )
    parser.add_argument(
        "vulkan_headers",
        type=str,
        help="The path to the root of the Vulkan-Headers repository.",
    )
    args = parser.parse_args()

    # The registry directory is a subdirectory of the provided path
    source_registry_path = Path(args.vulkan_headers) / "registry"

    if not source_registry_path.is_dir():
        print(f"Error: Registry directory not found at '{source_registry_path}'")
        print("Please provide the path to the root of the Vulkan-Headers git repository.")
        return

    try:
        # Get version from vk.xml BEFORE copying
        print("Step 1: Reading version from original vk.xml...")
        version = get_vulkan_header_version(source_registry_path)
        print(f"Found Vulkan-Headers version: {version}")

        print("\nStep 2: Copying registry files...")
        copy_registry_files(source_registry_path)

        print("\nStep 3: Updating pyproject.toml...")
        update_pyproject_version(version)

        print("\nStep 4: Converting imports to relative...")
        fix_relative_imports()

        print("\nUpdate complete!")

    except (FileNotFoundError, ValueError) as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()
