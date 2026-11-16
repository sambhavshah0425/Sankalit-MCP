import pytest
import sankalit_mcp.config

@pytest.fixture(autouse=True)
def patch_workspace_root(tmp_path_factory):
    # Set workspace root to the pytest temporary directory so all tests can write inside it safely
    temp_dir = tmp_path_factory.getbasetemp()
    sankalit_mcp.config.WORKSPACE_ROOT = temp_dir
    sankalit_mcp.config.WORKSPACE_ROOTS = [temp_dir]
