"""Placeholder test - will be replaced in Phase 2."""


def test_project_structure():
    """Verify the project is set up correctly."""
    import os
    assert os.path.exists("services/portfolio")
    assert os.path.exists("services/trading")
    assert os.path.exists("services/wallet")
    assert os.path.exists("services/notifications")
    assert os.path.exists(".github/workflows/test.yml")
