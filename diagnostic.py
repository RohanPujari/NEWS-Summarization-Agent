#!/usr/bin/env python3
"""
Diagnostic script to debug Claude API authentication issues
Run this in your project root directory to find the problem
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🔍 CLAUDE API AUTHENTICATION DIAGNOSTIC")
print("=" * 60)

# Check 1: Is .env file in the right location?
print("\n1️⃣ Checking .env file location...")
env_path = Path(".env")
if env_path.exists():
    print(f"   ✅ .env file found at: {env_path.absolute()}")
else:
    print(f"   ❌ .env file NOT found in project root!")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Files in current directory:")
    for item in os.listdir("."):
        print(f"      - {item}")
    sys.exit(1)

# Check 2: Can we read the .env file?
print("\n2️⃣ Checking .env file content...")
try:
    with open(".env", "r") as f:
        content = f.read()
    print(f"   ✅ .env file is readable")
    print(f"   Content: {content[:50]}..." if len(content) > 50 else f"   Content: {content}")
except Exception as e:
    print(f"   ❌ Error reading .env: {e}")
    sys.exit(1)

# Check 3: Is ANTHROPIC_API_KEY in .env?
print("\n3️⃣ Checking if ANTHROPIC_API_KEY is in .env...")
if "ANTHROPIC_API_KEY" in content:
    print(f"   ✅ ANTHROPIC_API_KEY found in .env")
else:
    print(f"   ❌ ANTHROPIC_API_KEY NOT found in .env!")
    sys.exit(1)

# Check 4: Can we load it with python-dotenv?
print("\n4️⃣ Trying to load .env with python-dotenv...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"   ✅ Successfully loaded ANTHROPIC_API_KEY")
        print(f"   Key format: {api_key[:10]}...{api_key[-5:]}")
        print(f"   Key length: {len(api_key)} characters")
    else:
        print(f"   ❌ ANTHROPIC_API_KEY is None after loading!")
        sys.exit(1)
except ImportError:
    print(f"   ❌ python-dotenv not installed!")
    print(f"   Run: pip install python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error loading .env: {e}")
    sys.exit(1)

# Check 5: Is anthropic library installed?
print("\n5️⃣ Checking if anthropic library is installed...")
try:
    import anthropic
    print(f"   ✅ anthropic library installed (version: {anthropic.__version__ if hasattr(anthropic, '__version__') else 'unknown'})")
except ImportError:
    print(f"   ❌ anthropic library NOT installed!")
    print(f"   Run: pip install anthropic")
    sys.exit(1)

# Check 6: Can we create Anthropic client?
print("\n6️⃣ Trying to create Anthropic client...")
try:
    client = anthropic.Anthropic()
    print(f"   ✅ Anthropic client created successfully")
except Exception as e:
    print(f"   ❌ Error creating Anthropic client: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

# Check 7: Can we make a test API call?
print("\n7️⃣ Trying to make test API call...")
try:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Say 'Hello, Claude is working!' in one sentence."}
        ]
    )
    print(f"   ✅ API call successful!")
    print(f"   Response: {message.content[0].text}")
except Exception as e:
    print(f"   ❌ API call failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED! Claude API is working correctly!")
print("=" * 60)

