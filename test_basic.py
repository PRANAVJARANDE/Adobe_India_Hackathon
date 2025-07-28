#!/usr/bin/env python3
"""Basic test script to verify code structure and imports"""

import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing utils...")
        from utils.io_utils import save_json, ensure_dirs
        print("✓ utils.io_utils imported successfully")
        
        print("Testing round1a modules...")
        from round1a.heading_model import infer_headings, blocks_to_sections
        print("✓ round1a.heading_model imported successfully")
        
        # PDF parser requires PyMuPDF which may not be installed
        try:
            from round1a.pdf_parser import extract_text_blocks
            print("✓ round1a.pdf_parser imported successfully")
        except ImportError as e:
            print(f"⚠ round1a.pdf_parser requires PyMuPDF: {e}")
        
        # Round1b requires sentence-transformers which may not be installed
        try:
            from round1b.processor import process_collection
            print("✓ round1b.processor imported successfully")
        except ImportError as e:
            print(f"⚠ round1b.processor requires dependencies: {e}")
            
        try:
            from round1b.semantic_ranker import embed_texts, cosine_sim_matrix
            print("✓ round1b.semantic_ranker imported successfully")
        except ImportError as e:
            print(f"⚠ round1b.semantic_ranker requires dependencies: {e}")
            
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False
    return True

def test_directory_structure():
    """Test if directories exist"""
    dirs = ['input', 'output', 'round1a', 'round1b', 'utils']
    for d in dirs:
        if os.path.exists(d):
            print(f"✓ {d}/ directory exists")
        else:
            print(f"✗ {d}/ directory missing")

def test_main_script():
    """Test if main.py has basic structure"""
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        required_funcs = ['run_round1a', 'run_round1b']
        for func in required_funcs:
            if func in content:
                print(f"✓ {func} function found in main.py")
            else:
                print(f"✗ {func} function missing from main.py")
                
    except Exception as e:
        print(f"✗ Error reading main.py: {e}")

if __name__ == "__main__":
    print("=== Basic Code Structure Test ===")
    test_directory_structure()
    print("\n=== Import Test ===")
    test_imports()
    print("\n=== Main Script Test ===")
    test_main_script()
    print("\n=== Test Complete ===")