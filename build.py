#!/usr/bin/env python3
"""
Build script for wheat-viz project.
Copies source files and data to the build/ directory.
"""

import os
import shutil
from pathlib import Path


def clean_build_dir(build_dir):
    """Remove and recreate the build directory."""
    if build_dir.exists():
        print(f"Cleaning {build_dir}...")
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created {build_dir}")


def copy_file(src, dest):
    """Copy a single file to destination."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"  Copied: {src} -> {dest}")


def copy_directory(src, dest):
    """Copy an entire directory to destination."""
    if src.exists():
        shutil.copytree(src, dest, dirs_exist_ok=True)
        print(f"  Copied: {src} -> {dest}")
    else:
        print(f"  Warning: {src} does not exist, skipping")


def build():
    """Main build function."""
    # Define paths
    project_root = Path(__file__).parent
    build_dir = project_root / "build"
    
    print("=" * 60)
    print("Building wheat-viz project")
    print("=" * 60)
    
    # Clean build directory
    clean_build_dir(build_dir)
    
    # Copy main HTML file
    print("\nCopying HTML files...")
    copy_file(project_root / "index.html", build_dir / "index.html")
    
    # Copy CSS directory
    print("\nCopying CSS files...")
    copy_directory(project_root / "css", build_dir / "css")
    
    # Copy JavaScript directory
    print("\nCopying JavaScript files...")
    copy_directory(project_root / "javascript", build_dir / "javascript")
    
    # Copy data directory
    print("\nCopying data files...")
    copy_directory(project_root / "data", build_dir / "data")
    
    # Copy videos directory if it exists
    print("\nCopying video files...")
    copy_directory(project_root / "videos", build_dir / "videos")
    
    # Create .nojekyll file for GitHub Pages
    print("\nCreating .nojekyll file...")
    (build_dir / ".nojekyll").touch()
    print("  Created: .nojekyll")
    
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print(f"Output directory: {build_dir}")
    print("=" * 60)


if __name__ == "__main__":
    build()
