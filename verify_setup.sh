#!/bin/bash
# Verify setup is correct

echo "🔍 Verifying Quiz Solver Setup..."
echo ""

# Check files
echo "📁 Checking files..."

files=(
    "app/__init__.py"
    "app/main.py"
    "app/routes.py"
    "app/config.py"
    "app/utils/__init__.py"
    "app/utils/validator.py"
    "app/utils/browser.py"
    "app/utils/parser.py"
    "app/utils/solver_core.py"
    "app/utils/submitter.py"
    "build.sh"
    "render.yaml"
    "runtime.txt"
    "requirements.txt"
    ".gitignore"
    ".env.example"
)

missing=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING"
        ((missing++))
    fi
done

echo ""

# Check port configuration
echo "🔌 Checking port configuration..."
if grep -q "PORT.*10000" app/config.py; then
    echo "  ✅ Port 10000 configured in config.py"
else
    echo "  ❌ Port 10000 NOT found in config.py"
    ((missing++))
fi

if grep -q "port 10000" render.yaml; then
    echo "  ✅ Port 10000 configured in render.yaml"
else
    echo "  ❌ Port 10000 NOT found in render.yaml"
    ((missing++))
fi

echo ""

# Check for OpenAI (should not exist)
echo "🔍 Checking for external APIs..."
if grep -q "openai\|anthropic" app/utils/solver_core.py; then
    echo "  ❌ WARNING: External API calls found in solver"
    ((missing++))
else
    echo "  ✅ No external API calls in solver"
fi

echo ""

# Check build script
echo "🔧 Checking build script..."
if [ -x "build.sh" ]; then
    echo "  ✅ build.sh is executable"
else
    echo "  ⚠️  build.sh not executable (run: chmod +x build.sh)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $missing -eq 0 ]; then
    echo "✅ Setup is PERFECT!"
    echo ""
    echo "Next steps:"
    echo "1. Create .env: cp .env.example .env"
    echo "2. Edit SECRET_KEY in .env"
    echo "3. Make executable: chmod +x build.sh"
    echo "4. Git push"
    echo "5. Deploy on Render"
else
    echo "❌ Found $missing issues"
    echo "Please fix the issues above"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
