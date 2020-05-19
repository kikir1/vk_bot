from functools import lru_cache
from typing import List
from typing import Union

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from .conditions import all_present
from .conditions import present
from .types import PageElementsType
from .types import PageElementType
from .types import RegionClassType
from .types import checkedmeta


def list_by_fields():
    return {k: v for k, v in vars(By).items() if not k.startswith("_")}


def validate_by(by):
    if by not in list_by_fields().values():
        raise TypeError(f"Unsupported locator strategy: {by}")
    return by


class PageElement:
    def __init__(
        self,
        by,
        value,
        timeout=5,
        condition=present,
        wait_type="until",
        cache=False,
        find_on_page_load=False,
    ):
        self.by = validate_by(by)
        self.value = value
        self.timeout = timeout
        self.condition = condition
        wait_types = ["until", "until_not"]
        assert wait_type in wait_types, (
            f"wait_type should be one of the following:" f" {wait_types}"
        )
        self.wait_type = wait_type
        self.cache = cache
        self.find_on_page_load = find_on_page_load

    @lru_cache(maxsize=128)
    def find(self, instance):
        driver = instance.driver
        page_class_name = instance.__class__.__name__
        root_element = getattr(instance, "root_element", None)

        wait = getattr(WebDriverWait(driver, self.timeout), self.wait_type)

        message = (
            f"{self.__class__.__name__}("
            f'by="{self.by}",'
            f' value="{self.value}",'
            f' timeout="{self.timeout}",'
            f" condition={self.condition.__name__},"
            f' wait_type="{self.wait_type}",'
            f' cache="{self.cache}",'
            f' root_element="{root_element}",'
            f" find_on_page_load={self.find_on_page_load}),"
        )
        if root_element:
            return wait(
                self.condition(
                    locator=(self.by, self.value), root_element=root_element
                ),
                message=f"{message} not found on {page_class_name} Region",
            )
        return wait(
            self.condition(locator=(self.by, self.value)),
            message=f"{message} not found on {page_class_name} Page",
        )

    def to_locator(self):
        return self.by, self.value

    def __get__(self, instance, owner) -> Union[WebElement, "PageElement"]:
        if instance is None:
            return self
        if self.cache:
            return self.find(instance)
        return self.find.__wrapped__(self, instance)

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}(by="{self.by}", value="{self.value}",'
            f' condition={self.condition.__name__}, timeout="{self.timeout}",'
            f" find_on_page_load={self.find_on_page_load})>"
        )


class PageElements(PageElement):
    def __init__(
        self,
        by,
        value,
        condition=all_present,
        timeout=5,
        wait_type="until",
        cache=False,
        find_on_page_load=False,
    ):
        super().__init__(
            by,
            value,
            condition=condition,
            timeout=timeout,
            wait_type=wait_type,
            cache=cache,
            find_on_page_load=find_on_page_load,
        )

    def __get__(self, instance, owner) -> Union[List[WebElement], "PageElements"]:
        if instance is None:
            return self
        if self.cache:
            return self.find(instance)
        return self.find.__wrapped__(self, instance)


class RegionElement(metaclass=checkedmeta):
    region_class = RegionClassType()
    root_element = PageElementType()

    def __init__(self, region_class, root_element):
        self.region_class = region_class
        self.root_element = root_element

    @classmethod
    def to_region(cls, page, region_class, root_element):
        return region_class(page=page, driver=page.driver, root_element=root_element)

    def __get__(self, instance, owner):
        root_element = self.root_element.find(instance)
        return self.region_class(
            page=instance, driver=instance.driver, root_element=root_element
        )


class RegionElements(metaclass=checkedmeta):
    region_class = RegionClassType()
    root_element = PageElementsType()

    def __init__(self, region_class, root_element):
        self.region_class = region_class
        self.root_element = root_element

    def __get__(self, instance, owner):
        return [
            self.region_class(page=instance, driver=instance.driver, root_element=r)
            for r in self.root_element.find(instance)
        ]
