import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:5000"   # Change to EC2 public IP when running remotely
WAIT    = 5


# ─── FIXTURES ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def driver():
    """Set up headless Chrome driver (required for EC2/Jenkins)."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(WAIT)
    yield drv
    drv.quit()


def wait_for(driver, by, value, timeout=WAIT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


# ═════════════════════════════════════════════════════════════════════════════
# TEST SUITE
# ═════════════════════════════════════════════════════════════════════════════

class TestHomePage:
    """TC-01 to TC-03: Home page basic checks."""

    def test_TC01_homepage_loads(self, driver):
        """TC-01: Home page should load with 200 OK and correct title."""
        driver.get(BASE_URL)
        assert "Task Manager" in driver.title, \
            f"Expected 'Task Manager' in title, got: {driver.title}"

    def test_TC02_navbar_visible(self, driver):
        """TC-02: Navigation bar with Home and Add Task links must be visible."""
        driver.get(BASE_URL)
        nav_title = driver.find_element(By.ID, "nav-title")
        nav_home  = driver.find_element(By.ID, "nav-home")
        nav_add   = driver.find_element(By.ID, "nav-add")
        assert nav_title.is_displayed()
        assert nav_home.is_displayed()
        assert nav_add.is_displayed()

    def test_TC03_tasks_table_present(self, driver):
        """TC-03: Tasks table or 'no tasks' message should be rendered."""
        driver.get(BASE_URL)
        table_exists = len(driver.find_elements(By.ID, "tasks-table")) > 0
        empty_exists = len(driver.find_elements(By.ID, "no-tasks"))  > 0
        assert table_exists or empty_exists, \
            "Neither the tasks table nor the empty-state message was found."


class TestAddTask:
    """TC-04 to TC-08: Add-task form validation and submission."""

    def test_TC04_add_page_loads(self, driver):
        """TC-04: Add Task page must load and show the form."""
        driver.get(f"{BASE_URL}/add")
        form = driver.find_element(By.ID, "add-task-form")
        assert form.is_displayed()

    def test_TC05_add_task_fields_present(self, driver):
        """TC-05: All required form fields must exist."""
        driver.get(f"{BASE_URL}/add")
        assert driver.find_element(By.ID, "title").is_displayed()
        assert driver.find_element(By.ID, "description").is_displayed()
        assert driver.find_element(By.ID, "priority").is_displayed()
        assert driver.find_element(By.ID, "status").is_displayed()
        assert driver.find_element(By.ID, "submit-btn").is_displayed()

    def test_TC06_add_task_successfully(self, driver):
        """TC-06: Submitting a valid task should redirect to home with success flash."""
        driver.get(f"{BASE_URL}/add")
        driver.find_element(By.ID, "title").send_keys("Selenium Test Task")
        driver.find_element(By.ID, "description").send_keys("Created by automated test")
        Select(driver.find_element(By.ID, "priority")).select_by_value("High")
        Select(driver.find_element(By.ID, "status")).select_by_value("Pending")
        driver.find_element(By.ID, "submit-btn").click()

        wait_for(driver, By.ID, "flash-message")
        flash = driver.find_element(By.ID, "flash-message")
        assert "success" in flash.get_attribute("class")
        assert "successfully" in flash.text.lower()

    def test_TC07_task_appears_in_list(self, driver):
        """TC-07: The newly added task title must appear in the tasks table."""
        driver.get(BASE_URL)
        titles = [el.text for el in driver.find_elements(By.CLASS_NAME, "task-title")]
        assert "Selenium Test Task" in titles, \
            f"Newly added task not found in table. Found: {titles}"

    def test_TC08_empty_title_rejected(self, driver):
        """TC-08: Submitting a form with empty title should not add a task (HTML5 required)."""
        driver.get(f"{BASE_URL}/add")
        # Clear title and try to submit – browser should block with HTML5 validation
        title_field = driver.find_element(By.ID, "title")
        title_field.clear()
        submit = driver.find_element(By.ID, "submit-btn")
        submit.click()
        # Page should stay on /add (no redirect)
        assert "/add" in driver.current_url or "add" in driver.current_url


class TestEditTask:
    """TC-09 to TC-11: Edit task functionality."""

    def test_TC09_edit_link_exists(self, driver):
        """TC-09: At least one Edit button should be present on the home page."""
        driver.get(BASE_URL)
        edit_btns = driver.find_elements(By.CLASS_NAME, "btn-edit")
        assert len(edit_btns) > 0, "No Edit buttons found on the home page."

    def test_TC10_edit_page_prefills_data(self, driver):
        """TC-10: Clicking Edit should open a form pre-filled with the task's current data."""
        driver.get(BASE_URL)
        first_title = driver.find_element(By.CLASS_NAME, "task-title").text
        driver.find_element(By.CLASS_NAME, "btn-edit").click()

        wait_for(driver, By.ID, "edit-task-form")
        title_val = driver.find_element(By.ID, "title").get_attribute("value")
        assert title_val == first_title, \
            f"Pre-filled title '{title_val}' doesn't match expected '{first_title}'"

    def test_TC11_edit_task_updates_record(self, driver):
        """TC-11: Editing and saving a task should show updated title on home page."""
        driver.get(BASE_URL)
        driver.find_element(By.CLASS_NAME, "btn-edit").click()
        wait_for(driver, By.ID, "edit-task-form")

        title_input = driver.find_element(By.ID, "title")
        title_input.clear()
        title_input.send_keys("Updated by Selenium")
        driver.find_element(By.ID, "update-btn").click()

        wait_for(driver, By.ID, "flash-message")
        driver.get(BASE_URL)
        titles = [el.text for el in driver.find_elements(By.CLASS_NAME, "task-title")]
        assert "Updated by Selenium" in titles, \
            f"Updated title not found. Current titles: {titles}"


class TestDeleteTask:
    """TC-12 to TC-13: Delete task functionality."""

    def test_TC12_delete_btn_present(self, driver):
        """TC-12: Delete buttons must be present on the home page."""
        driver.get(BASE_URL)
        del_btns = driver.find_elements(By.CLASS_NAME, "btn-delete")
        assert len(del_btns) > 0, "No Delete buttons found."

    def test_TC13_delete_task_removes_from_list(self, driver):
        """TC-13: After deleting the last added task, it should no longer appear."""
        # First add a task specifically for deletion
        driver.get(f"{BASE_URL}/add")
        driver.find_element(By.ID, "title").send_keys("Task To Delete")
        driver.find_element(By.ID, "submit-btn").click()
        wait_for(driver, By.ID, "flash-message")

        # Find and delete it
        driver.get(BASE_URL)
        rows = driver.find_elements(By.CLASS_NAME, "task-row")
        initial_count = len(rows)

        # Click the first delete button (confirms via JS dialog)
        driver.execute_script(
            "window.confirm = function() { return true; }"
        )
        driver.find_elements(By.CLASS_NAME, "btn-delete")[0].click()
        wait_for(driver, By.ID, "flash-message")

        new_rows = driver.find_elements(By.CLASS_NAME, "task-row")
        assert len(new_rows) < initial_count, \
            "Row count did not decrease after deletion."


class TestSearch:
    """TC-14 to TC-15: Search functionality."""

    def test_TC14_search_input_present(self, driver):
        """TC-14: Search form and input field should be visible on home page."""
        driver.get(BASE_URL)
        search_form  = driver.find_element(By.ID, "search-form")
        search_input = driver.find_element(By.ID, "search-input")
        assert search_form.is_displayed()
        assert search_input.is_displayed()

    def test_TC15_search_returns_results(self, driver):
        """TC-15: Searching by a known keyword should return matching tasks."""
        driver.get(BASE_URL)
        driver.find_element(By.ID, "search-input").send_keys("Selenium")
        driver.find_element(By.ID, "search-btn").click()
        time.sleep(1)

        titles = [el.text for el in driver.find_elements(By.CLASS_NAME, "task-title")]
        for title in titles:
            assert "selenium" in title.lower() or len(titles) == 0, \
                f"Unexpected task in search results: {title}"

    def test_TC16_search_no_results(self, driver):
        """TC-16: Searching for a non-existent term should show empty/no-tasks state."""
        driver.get(f"{BASE_URL}/search?q=xyznonexistent12345")
        table_rows = driver.find_elements(By.CLASS_NAME, "task-row")
        empty_msg   = driver.find_elements(By.ID, "no-tasks")
        assert len(table_rows) == 0 or len(empty_msg) > 0, \
            "Expected empty state for non-matching search."


class TestPriorityAndStatus:
    """TC-17 to TC-18: Priority/status badge rendering."""

    def test_TC17_priority_badge_displayed(self, driver):
        """TC-17: Each task row should display a priority badge."""
        driver.get(BASE_URL)
        rows = driver.find_elements(By.CLASS_NAME, "task-row")
        if rows:
            badges = rows[0].find_elements(By.CLASS_NAME, "badge")
            assert len(badges) >= 2, \
                "Expected at least 2 badges (priority + status) per row."

    def test_TC18_add_task_with_all_priorities(self, driver):
        """TC-18: Adding tasks with Low/Medium/High priority should work for each."""
        for priority in ["Low", "Medium", "High"]:
            driver.get(f"{BASE_URL}/add")
            driver.find_element(By.ID, "title").send_keys(f"Priority-{priority} Task")
            Select(driver.find_element(By.ID, "priority")).select_by_value(priority)
            driver.find_element(By.ID, "submit-btn").click()
            wait_for(driver, By.ID, "flash-message")
            flash = driver.find_element(By.ID, "flash-message")
            assert "successfully" in flash.text.lower(), \
                f"Failed to add task with priority {priority}"


class TestNavigation:
    """TC-19 to TC-20: Navigation links."""

    def test_TC19_nav_home_link(self, driver):
        """TC-19: Clicking 'Home' in navbar should navigate to '/'."""
        driver.get(f"{BASE_URL}/add")
        driver.find_element(By.ID, "nav-home").click()
        assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/"), \
            f"Home link did not navigate correctly. Current: {driver.current_url}"

    def test_TC20_nav_add_link(self, driver):
        """TC-20: Clicking '+ Add Task' in navbar should navigate to '/add'."""
        driver.get(BASE_URL)
        driver.find_element(By.ID, "nav-add").click()
        assert "/add" in driver.current_url, \
            f"Add Task link did not navigate correctly. Current: {driver.current_url}"
