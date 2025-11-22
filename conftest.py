import pytest

BROWSERS = ["chromium", "firefox"]

@pytest.fixture(params=["chromium", "firefox"])
def my_browser(request):
    return request.param
    return None

def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        metafunc.parametrize("browser_name", BROWSERS)
