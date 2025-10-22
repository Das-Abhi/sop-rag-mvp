"""
Pytest configuration and fixtures
"""
import pytest
import os

# Set test database URL to in-memory SQLite for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
