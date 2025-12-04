# tests/conftest.py
"""
Pytest configuration and shared fixtures for KACA tests.
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_spec():
    """Provide a sample spec.yaml content."""
    return {
        'meta': {
            'project_name': 'Test Project',
            'project_type': 'analytics',
            'version': 1
        },
        'problem': {
            'business_question': 'What drives performance?',
            'success_criteria': ['Identify top factors']
        },
        'data': {
            'sources': [
                {'name': 'sales', 'path': 'data/sales.csv', 'type': 'csv'}
            ]
        },
        'deliverables': ['Chart', 'Report'],
        'visualization': {
            'format': 'png',
            'size': 'presentation'
        }
    }


@pytest.fixture
def sample_status():
    """Provide a sample status.json content."""
    return {
        'project_name': 'Test Project',
        'project_type': 'analytics',
        'current_phase': 'Phase 1',
        'spec_version': 1,
        'tasks': [
            {'id': '1.1', 'description': 'Load data', 'status': 'done', 'phase': 'Phase 1'},
            {'id': '2.1', 'description': 'Analyze data', 'status': 'pending', 'phase': 'Phase 2'},
        ],
        'artifacts': [],
        'history': []
    }


@pytest.fixture
def sample_data():
    """Provide sample data for chart/insight testing."""
    return {
        'categories': ['North', 'South', 'East', 'West'],
        'values': [150, 100, 80, 70],
        'series': {
            'Revenue': [150, 100, 80, 70],
            'Cost': [80, 60, 50, 40]
        }
    }
