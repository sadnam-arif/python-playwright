import pytest

browsers = ["chromium", "firefox"]

@pytest.fixture(params=browsers)
def browser_name(request):
    return request.param
