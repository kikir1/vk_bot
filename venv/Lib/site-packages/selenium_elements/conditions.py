from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import _element_if_visible
from selenium.webdriver.support.expected_conditions import _find_element


class ElementTextError(Exception):
    pass


class ElementNotVisibleError(Exception):
    pass


class ElementNotClickableError(Exception):
    pass


class ElementSelectedError(Exception):
    pass


def _find_element_on_region(by, root_element):
    try:
        return root_element.find_element(*by)
    except NoSuchElementException as e:
        raise e
    except WebDriverException as e:
        raise e


def _find_elements_on_region(by, root_element):
    try:
        return root_element.find_elements(*by)
    except WebDriverException as e:
        raise e


def _element_visible(driver, by, root_element=None):
    if not root_element:
        element = _find_element(driver, by)
    else:
        element = _find_element_on_region(by, root_element)

    if not element.is_displayed():
        raise ElementNotVisibleError(f"Element ({by}) not visible.")
    return element


class present(EC.presence_of_element_located):
    def __init__(self, locator, root_element=None):
        super().__init__(locator)
        self.root_element = root_element

    def __call__(self, driver):
        if not self.root_element:
            return super().__call__(driver)
        return _find_element_on_region(self.locator, self.root_element)


class all_present(EC.presence_of_all_elements_located):
    def __init__(self, locator, root_element=None):
        super().__init__(locator)
        self.root_element = root_element

    def __call__(self, driver):
        if not self.root_element:
            return super().__call__(driver)
        return _find_elements_on_region(self.locator, self.root_element)


class visible:
    def __init__(self, locator, root_element=None):
        self.locator = locator
        self.root_element = root_element

    def __call__(self, driver):
        return _element_visible(driver, self.locator, self.root_element)


class clickable:
    def __init__(self, locator, root_element=None):
        self.locator = locator
        self.root_element = root_element

    def __call__(self, driver):
        element = _element_visible(driver, self.locator, self.root_element)

        if element.is_enabled():
            return element
        raise ElementNotClickableError(f"Element ({self.locator}) not clickable.")


class selected:
    def __init__(self, locator, root_element=None):
        self.locator = locator
        self.root_element = root_element

    def __call__(self, driver):
        element = _element_visible(driver, self.locator, self.root_element)

        if element.is_selected():
            return element
        raise ElementSelectedError(f"Element ({self.locator}) not selected.")


class visibility_of_any_elements(EC.visibility_of_any_elements_located):
    def __init__(self, locator, root_element=None):
        super().__init__(locator)
        self.root_element = root_element

    def __call__(self, driver):
        if not self.root_element:
            return super().__call__(driver)
        return [
            element
            for element in _find_elements_on_region(self.locator, self.root_element)
            if _element_if_visible(element)
        ]


class all_elements_visible(EC.visibility_of_all_elements_located):
    def __init_(self, locator, root_element=None):
        self.locator = locator
        self.root_element = root_element

    def __call__(self, driver):
        if not self.root_element:
            return super().__call__(driver)
        try:
            elements = _find_elements_on_region(self.locator, self.root_element)
            for element in elements:
                if _element_if_visible(element, visibility=False):
                    return False
            return elements
        except StaleElementReferenceException:
            return False


def has_text(text):
    class has_text:
        def __init__(self, locator, root_element=None):
            self.locator = locator
            self.text = text
            self.root_element = root_element

        def __call__(self, driver):
            if not self.root_element:
                element = _find_element(driver, self.locator)
            else:
                element = _find_element_on_region(self.locator, self.root_element)

            if self.text in element.text:
                return element
            raise ElementTextError(
                f'"{self.text}" not present in element located by {self.locator}.'
            )

    return has_text
