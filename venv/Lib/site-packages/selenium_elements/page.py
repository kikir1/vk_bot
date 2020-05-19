import concurrent.futures

from abc import ABCMeta
from abc import abstractmethod
from collections import OrderedDict
from functools import reduce
from urllib.parse import urljoin

from selenium.common.exceptions import TimeoutException

from .elements import PageElement
from .elements import PageElements
from .elements import RegionElement
from .elements import RegionElements
from .validators import ValidationError


def trigger_auto_find_elements(page):
    elements_with_auto_find = filter(
        lambda x: x.find_on_page_load, page.declared_elements.values()
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_element = {
            executor.submit(e.find, page): e for e in elements_with_auto_find
        }
        errs = []
        for future in concurrent.futures.as_completed(future_element):
            element = future_element[future]
            try:
                future.result()
            except Exception:
                errs.append(element)
        if errs:
            raise ValidationError(errs)


class PageMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs, **kwargs):
        elements = []
        regions = []
        for key, value in attrs.items():
            if isinstance(value, PageElement) or isinstance(value, PageElements):
                elements.append((key, value))
            if isinstance(value, RegionElement) or isinstance(value, RegionElements):
                regions.append((key, value))

        attrs["declared_elements"] = OrderedDict(elements)
        attrs["declared_regions"] = OrderedDict(regions)
        return super().__new__(mcs, name, bases, attrs)


class BasePage(metaclass=PageMeta):
    def __iter__(self):
        for name in self.declared_elements:
            yield self[name]

    def __getitem__(self, name):
        try:
            return self.declared_elements[name]
        except KeyError:
            raise KeyError(
                f'Key "{name}" not found in "{self.__class__.__name__}".'
                f' Choices are: {", ".join(f for f in self.declared_elements)}'
            )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(base_url={self.base_url}, visit={self.visit},"
            f" load_timeout={self.load_timeout}, kwargs={self.kwargs},"
            f" current_url={self.driver.current_url})"
        )


# def slash_join2(*args):
#     return f'{"/".join(arg.strip("/") for arg in args)}/'


def slash_join(*args):
    return reduce(urljoin, args)


class Page(BasePage):

    load_timeout = 30
    validators = []

    @property
    @abstractmethod
    def path(self):
        pass

    def __init__(self, driver, base_url, visit=True, **kwargs):
        self.driver = driver
        self.base_url = base_url
        self.visit = visit
        self.kwargs = kwargs

        self.driver.set_page_load_timeout(self.load_timeout)

        if self.visit:
            from string import Formatter

            variable_substitutions = [
                fname for _, fname, _, _ in Formatter().parse(self.path) if fname
            ]
            if variable_substitutions:
                diff = set(variable_substitutions).difference(set(self.kwargs.keys()))
                if diff:
                    msg = (
                        f"The following fields: {diff} are required when"
                        f" instantiating {self.__class__.__name__}"
                    )
                    raise ValueError(msg)

            path = self.path.format(**kwargs)
            url = slash_join(self.base_url, path)

            try:
                self.driver.get(url)
            except TimeoutException as e:
                msg = f"Page timeout after {self.load_timeout} seconds for url: {url}"
                raise TimeoutException(msg) from e

        self.html = self.driver.find_element_by_tag_name("html")

        trigger_auto_find_elements(page=self)

        errs = []
        for validator in self.validators:
            try:
                validator(self.driver)
            except ValidationError as e:
                errs.append(e.message)
        if errs:
            raise ValidationError(errs)


class Region(BasePage):
    def __init__(self, page, driver, root_element):
        self.page = page
        self.base_url = page.base_url
        self.driver = driver
        self.root_element = root_element

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(page={self.page.__class__.__name__},"
            f" current_url={self.driver.current_url})"
        )
