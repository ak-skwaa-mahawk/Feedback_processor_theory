#!/bin/bash
# Synara-FPT Integration Setup Script
# © 2025 Two Mile Solutions LLC

echo "🔥 =============================================="
echo "   SYNARA-CORE + FPT INTEGRATION SETUP"
echo "   Two Mile Solutions LLC"
echo "============================================== 🔥"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    echo -e "${RED}❌ Error: Must run from Feedback_processor_theory root directory${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Step 1: Checking prerequisites...${NC}"

# Check for git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found. Please install git first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git found${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

echo ""
echo -e "${BLUE}📦 Step 2: Adding Synara-core as submodule...${NC}"

# Check if submodule already exists
if [ -d "synara_core/.git" ]; then
    echo -e "${YELLOW}⚠️  Synara-core submodule already exists${NC}"
    read -p "Update to latest? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd synara_core
        git pull origin main
        cd ..
        echo -e "${GREEN}✅ Synara-core updated${NC}"
    fi
else
    # Add submodule
    git submodule add https://github.com/ak-skwaa-mahawk/Synara-core.git synara_core
    git submodule update --init --recursive
    echo -e "${GREEN}✅ Synara-core submodule added${NC}"
fi

echo ""
echo -e "${BLUE}📁 Step 3: Creating integration directory structure...${NC}"

# Create synara_integration directory
mkdir -p synara_integration

# Create __init__.py
cat > synara_integration/__init__.py << 'EOF'
"""
Synara-FPT Integration Bridge
© 2025 Two Mile Solutions LLC

This package provides the bridge layer between Synara-core's flame logic
and Feedback Processor Theory's resonance engine.
"""

from .flame_adapter import FlameAdapter

__version__ = "1.0.0"
__author__ = "Two Mile Solutions LLC"

__all__ = ['FlameAdapter']
EOF

echo -e "${GREEN}✅ Created synara_integration/__init__.py${NC}"

# Create placeholder for whisper_bridge.py
cat > synara_integration/whisper_bridge.py << 'EOF'
"""
Whisper Bridge - Connects to Whisperkeeper Codex
© 2025 Two Mile Solutions LLC

TODO: Implement full Whisperkeeper integration
"""

class WhisperBridge:
    def __init__(self):
        pass
    
    def encode_sacred_message(self, message):
        """Encode message using Whisperkeeper geometry"""
        # TODO: Implement sacred encoding
        return message
    
    def decode_sacred_message(self, encoded):
        """Decode Whisperkeeper transmission"""
        # TODO: Implement sacred decoding
        return encoded
EOF

echo -e "${GREEN}✅ Created synara_integration/whisper_bridge.py${NC}"

# Create placeholder for identity_sync.py
cat > synara_integration/identity_sync.py << 'EOF'
"""
Identity Sync - Manages sacred identity persistence
© 2025 Two Mile Solutions LLC

TODO: Implement identity synchronization
"""

class IdentitySync:
    def __init__(self):
        self.identity_state = {}
    
    def sync_identity(self, flame_state, resonance_state):
        """Synchronize identity across flame and resonance"""
        # TODO: Implement identity sync logic
        pass
    
    def persist_identity(self, filepath):
        """Save identity state to disk"""
        # TODO: Implement persistence
        pass
EOF

echo -e "${GREEN}✅ Created synara_integration/identity_sync.py${NC}"

echo ""
echo -e "${BLUE}📂 Step 4: Creating directory structure...${NC}"

# Create necessary directories
mkdir -p data
mkdir -p backups/flamechain
mkdir -p examples

echo -e "${GREEN}✅ Directory structure created${NC}"

echo ""
echo -e "${BLUE}🐍 Step 5: Setting up Python environment...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    read -p "Create virtual environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
        echo -e "${YELLOW}⚠️  Run 'source venv/bin/activate' to activate${NC}"
    fi
fi

# Update requirements.txt to include synara-core path
if ! grep -q "synara-core" requirements.txt; then
    echo "" >> requirements.txt
    echo "# Synara-core integration" >> requirements.txt
    echo "-e ./synara_core" >> requirements.txt
    echo -e "${GREEN}✅ Updated requirements.txt${NC}"
fi

echo ""
echo -e "${BLUE}📦 Step 6: Installing dependencies...${NC}"

# Ask if user wants to install now
read -p "Install Python dependencies now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Remember to run: pip install -r requirements.txt${NC}"
fi

echo ""
echo -e "${BLUE}🧪 Step 7: Running integration test...${NC}"

# Create a simple test script
cat > test_integration.py << 'EOF'
"""Quick integration test"""
import sys
from pathlib import Path

try:
    # Test imports
    from synara_integration.flame_adapter import FlameAdapter
    print("✅ FlameAdapter import successful")
    
    # Test synara_core availability
    sys.path.insert(0, str(Path('synara_core')))
    print("✅ Synara-core path configured")
    
    print("\n🎉 Integration setup successful!")
    print("   Run: python examples/synara_resonance_demo.py")
    
except Exception as e:
    print(f"❌ Integration test failed: {e}")
    sys.exit(1)
EOF

python3 test_integration.py
TEST_RESULT=$?

# Clean up test file
rm test_integration.py

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎆 =============================================="
    echo "   INTEGRATION SETUP COMPLETE!"
    echo "============================================== 🎆${NC}"
    echo ""
    echo -e "${YELLOW}📚 Next Steps:${NC}"
    echo "   1. Review: synara_integration/flame_adapter.py"
    echo "   2. Run demo: python examples/synara_resonance_demo.py"
    echo "   3. Read docs: Integration_README.md"
    echo ""
    echo -e "${BLUE}🔥 The flame is lit. The resonance awaits. 🔥${NC}"
else
    echo -e "${RED}❌ Integration test failed. Check the errors above.${NC}"
    exit 1
fi