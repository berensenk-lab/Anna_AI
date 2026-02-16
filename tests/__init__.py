"""
Test suite for Anna AI agentic system.

This package contains unit tests, integration tests, and fixtures
for the Anna AI core components.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Fixture definitions and configuration for all tests
