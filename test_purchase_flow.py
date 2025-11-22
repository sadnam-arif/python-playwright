import json
import logging
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, Page, expect

BASE_URL = "https://automationexercise.com"
CREDENTIALS_FILE = Path("fixtures/user_credentials.json")
DOWNLOADS_DIR = Path("downloads")

BROWSERS = ["chromium", "firefox"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_credentials() -> tuple[str, str]:
    """
    Read email & password from fixtures/user_credentials.json
    (written by test_create_user.py).
    """
    assert CREDENTIALS_FILE.exists(), (
        f"Credentials file not found: {CREDENTIALS_FILE}. "
        "Run test_create_user.py first to generate it."
    )

    data = json.loads(CREDENTIALS_FILE.read_text())
    email = data.get("email")
    password = data.get("password")

    assert email and password, "Email/password missing in credentials file"
    logger.info("Loaded credentials for %s", email)
    return email, password


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def accept_cookies_if_present(self) -> None:
        cookie_buttons = self.page.locator("p.fc-button-label")

        if cookie_buttons.count() > 0:
            try:
                cookie_buttons.first.click(timeout=3000)
                logger.info("Cookie popup dismissed.")
            except Exception:
                logger.info("Cookie popup not visible / clickable, continuing.")


class HomePage(BasePage):
    def goto(self) -> None:
        logger.info("Navigating to home page: %s", BASE_URL)
        self.page.goto(BASE_URL)
        expect(self.page).to_have_title("Automation Exercise")
        self.accept_cookies_if_present()

    def go_to_login(self) -> None:
        logger.info("Navigating to Login page.")
        self.page.locator("a[href='/login']").click()
        expect(self.page.locator("h2:has-text('Login to your account')")).to_be_visible()

    def add_product_to_cart_by_index(self, index: int, view_cart_after: bool = False) -> None:
        logger.info("Adding product index %s to cart (view_cart_after=%s)", index, view_cart_after)
        product = self.page.locator("div.features_items .productinfo").nth(index)
        product.hover()
        product.locator("a:has-text('Add to cart')").click()

        modal = self.page.locator("#cartModal .modal-content")
        expect(modal).to_be_visible()

        if view_cart_after:
            logger.info("Clicking 'View Cart' in modal.")
            modal.locator("a:has-text('View Cart')").click()
        else:
            logger.info("Clicking 'Continue Shopping' in modal.")
            modal.locator("button:has-text('Continue Shopping')").click()


class LoginPage(BasePage):
    def login(self, email: str, password: str) -> None:
        logger.info("Logging in as %s", email)
        self.page.locator("input[data-qa='login-email']").fill(email)
        self.page.locator("input[placeholder='Password']").fill(password)
        self.page.locator("button[data-qa='login-button']").click()

    def assert_logged_in(self) -> None:
        logger.info("Verifying successful login.")
        expect(self.page.locator("a:has-text('Logged in as')")).to_be_visible()
        expect(self.page).to_have_url(BASE_URL + "/")


class CartPage(BasePage):
    def open_cart_from_nav(self) -> None:
        logger.info("Opening cart page from nav.")
        self.page.locator("a[href='/view_cart']").click()
        expect(self.page).to_have_url(BASE_URL + "/view_cart")

    def assert_two_products_present(self) -> None:
        logger.info("Verifying at least two products in cart.")
        rows = self.page.locator("table tbody tr")
        assert rows.count() >= 2, "Expected at least 2 products in cart"

    def proceed_to_checkout(self) -> None:
        logger.info("Clicking 'Proceed To Checkout'.")
        self.page.locator("a:has-text('Proceed To Checkout')").click()
        expect(self.page.locator("h2:has-text('Address Details')")).to_be_visible()


class CheckoutPage(BasePage):
    def place_order(self, comment: str) -> None:
        logger.info("Filling order comment and placing order.")
        expect(self.page.locator("h2:has-text('Review Your Order')")).to_be_visible()
        self.page.locator("textarea[name='message']").fill(comment)
        self.page.locator("a:has-text('Place Order')").click()
        expect(self.page.locator("h2:has-text('Payment')")).to_be_visible()


class PaymentPage(BasePage):
    def fill_payment_and_confirm(
        self,
        name_on_card: str,
        card_number: str,
        cvc: str,
        exp_month: str,
        exp_year: str,
    ) -> None:
        logger.info("Entering payment details and confirming order.")
        expect(self.page.locator("h2:has-text('Payment')")).to_be_visible()

        self.page.fill("input[name='name_on_card']", name_on_card)
        self.page.fill("input[name='card_number']", card_number)
        self.page.fill("input[placeholder='ex. 311']", cvc)
        self.page.fill("input[placeholder='MM']", exp_month)
        self.page.fill("input[placeholder='YYYY']", exp_year)

        self.page.click("button#submit")

        expect(self.page.locator("b:has-text('Order Placed!')")).to_be_visible()
        success_message = self.page.locator(
            "p:has-text('Congratulations! Your order has been confirmed!')"
        )
        expect(success_message).to_be_visible()

        logger.info("Order placed successfully: %s", success_message.inner_text())

        expected_url_part = "/payment_done"
        assert expected_url_part in self.page.url, (
            f"Unexpected success URL: {self.page.url}. "
            "Adjust 'expected_url_part' if needed."
        )

    def download_and_verify_invoice(self, downloads_dir: Path) -> Path:
        logger.info("Downloading invoice.")
        downloads_dir.mkdir(parents=True, exist_ok=True)

        with self.page.expect_download() as download_info:
            self.page.locator("a:has-text('Download Invoice')").click()

        download = download_info.value
        target_path = downloads_dir / download.suggested_filename
        download.save_as(target_path)

        logger.info("Invoice downloaded to %s", target_path)

        assert target_path.exists(), "Invoice file was not found on disk."
        size = target_path.stat().st_size
        assert size > 0, f"Invoice file is empty (size={size})."

        logger.info("Invoice file exists and is non-empty (size=%s bytes).", size)
        return target_path


def test_purchase_flow(browser_name: str) -> None:
    """
    Full purchase + invoice downloading flow:
    1. Navigate to site
    2. Login using fixtures/user_credentials.json
    3. Add 2 products to the cart
    4. Checkout & place order successfully
    5. Verify success message + URL
    6. Download invoice and verify the downloaded file
    """
    email, password = load_credentials()

    with sync_playwright() as p:
        browser_type = getattr(p, browser_name)
        logger.info("Launching browser: %s", browser_name)
        browser = browser_type.launch(headless=False, slow_mo=300)
        context = browser.new_context(
            accept_downloads=True,
            record_video_dir="videos/",
            )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = context.new_page()

        home = HomePage(page)
        login_page = LoginPage(page)
        cart_page = CartPage(page)
        checkout_page = CheckoutPage(page)
        payment_page = PaymentPage(page)

        # Navigate to homepage
        home.goto()

        # Login using stored credentials
        home.go_to_login()
        login_page.login(email, password)
        login_page.assert_logged_in()

        # Add two products to the cart
        # First product from home page
        home.add_product_to_cart_by_index(0, view_cart_after=False)
        # Second product, then go to cart via modal "View Cart"
        home.add_product_to_cart_by_index(1, view_cart_after=True)

        # Proceed to checkout and complete order
        cart_page.assert_two_products_present()
        cart_page.proceed_to_checkout()

        checkout_page.place_order(comment="Please deliver between 9 AM and 5 PM.")

        payment_page.fill_payment_and_confirm(
            name_on_card="Credit Card User",
            card_number="4111111111111111",
            cvc="123",
            exp_month="12",
            exp_year="2030",
        )

        # Download and verify the downloaded invoice
        payment_page.download_and_verify_invoice(DOWNLOADS_DIR)

        # Cleanup
        context.tracing.stop(path="traces/trace.zip")
        context.close()
        browser.close()

