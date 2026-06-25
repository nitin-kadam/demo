#!/bin/bash
# Run API tests locally
# Usage: ./run_tests.sh [simple|pytest|all]

set -e

TEST_TYPE=${1:-all}

echo "🧪 API Test Runner"
echo "=================="

if [ "$TEST_TYPE" = "simple" ] || [ "$TEST_TYPE" = "all" ]; then
    echo ""
    echo "▶️  Running simple API tests..."
    python test_api.py
fi

if [ "$TEST_TYPE" = "pytest" ] || [ "$TEST_TYPE" = "all" ]; then
    echo ""
    echo "▶️  Running pytest tests..."
    pytest tests/test_jsonplaceholder_api.py -v
fi

if [ "$TEST_TYPE" = "coverage" ]; then
    echo ""
    echo "▶️  Running tests with coverage report..."
    pytest tests/test_jsonplaceholder_api.py --cov=. --cov-report=html --cov-report=term
    echo ""
    echo "📊 Coverage report generated: htmlcov/index.html"
fi

echo ""
echo "✅ Tests completed!"
