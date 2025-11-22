import pytest

BROWSERS = ["chromium", "firefox"]

@pytest.fixture()
def browser_name(request):
    if "browser_name" in request.fixturenames:
        return request.param
    return None

def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        metafunc.parametrize("browser_name", BROWSERS)
