#!/usr/bin/env python3
"""
Test app structure to ensure no duplicate button IDs
"""

import ast
import os

def check_button_ids():
    """Check for duplicate button IDs in the app"""
    
    print("🔍 Checking app.py for duplicate button IDs...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Parse the Python code
        tree = ast.parse(content)
        
        # Find all button calls
        button_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr == 'button'):
                    button_calls.append(node)
        
        print(f"📊 Found {len(button_calls)} button calls")
        
        # Check for duplicate button texts
        button_texts = []
        button_keys = []
        
        for call in button_calls:
            text = None
            key = None
            
            for keyword in call.keywords:
                if keyword.arg == 'label':
                    text = keyword.value.s
                elif keyword.arg == 'key':
                    key = keyword.value.s
            
            # Get the first argument if it's a string (button text)
            if call.args and isinstance(call.args[0], ast.Constant):
                text = call.args[0].value
            
            if text:
                button_texts.append(text)
                button_keys.append(key)
                print(f"  Button: '{text}' | Key: {key}")
        
        # Check for duplicate texts
        duplicate_texts = [text for text in set(button_texts) if button_texts.count(text) > 1]
        
        if duplicate_texts:
            print(f"\n⚠️  Found duplicate button texts: {duplicate_texts}")
            # Check if they have unique keys
            for text in duplicate_texts:
                keys_for_text = [key for t, key in zip(button_texts, button_keys) if t == text]
                unique_keys = set(keys_for_text)
                if len(unique_keys) == len(keys_for_text):
                    print(f"   ✅ '{text}' has unique keys: {keys_for_text}")
                else:
                    print(f"   ❌ '{text}' has duplicate keys: {keys_for_text}")
                    return False
            print("   All duplicate texts have unique keys - this is fine!")
            return True
        else:
            print("\n✅ No duplicate button texts found!")
            return True
            
        # Check for missing keys
        missing_keys = [text for text, key in zip(button_texts, button_keys) if key is None]
        if missing_keys:
            print(f"\n⚠️  WARNING: Buttons without keys: {missing_keys}")
            print("   Consider adding unique keys to avoid potential issues!")
        
    except Exception as e:
        print(f"❌ Error checking app structure: {e}")
        return False
    
    return True

def check_imports():
    """Check if all required imports are present"""
    
    print("\n🔍 Checking required imports...")
    
    required_imports = [
        'streamlit as st',
        'datetime',
        'tempfile',
        'os'
    ]
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"⚠️  Missing imports: {missing_imports}")
            return False
        else:
            print("✅ All required imports found!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking imports: {e}")
        return False

if __name__ == "__main__":
    print("🚀 App Structure Check")
    print("=" * 40)
    
    # Check button IDs
    buttons_ok = check_button_ids()
    
    # Check imports
    imports_ok = check_imports()
    
    print("\n" + "=" * 40)
    if buttons_ok and imports_ok:
        print("✨ App structure looks good! No duplicate ID issues found.")
    else:
        print("⚠️  Some issues found. Please review the warnings above.")
    
    print("\n💡 To run the app:")
    print("   streamlit run app.py")
