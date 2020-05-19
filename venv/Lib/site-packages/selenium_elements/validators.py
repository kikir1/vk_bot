import re


class ValidationError(Exception):
    def __init__(self, msg):
        self.errors = msg if isinstance(msg, list) else [msg]

    @property
    def message(self):
        return "\n".join(self.errors)


class title_matches:
    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, driver):
        if not re.match(self.pattern, driver.title):
            msg = f'Pattern: "{self.pattern}" doesnt match "{driver.title}"'
            raise ValidationError(msg)


class title_is:
    def __init__(self, page_title):
        self.page_title = page_title

    def __call__(self, driver):
        if not self.page_title == driver.title:
            msg = f'Page title: "{driver.title}" is not equal with: "{self.page_title}"'
            raise ValidationError(msg)


class title_contains:
    def __init__(self, page_title):
        self.page_title = page_title

    def __call__(self, driver):
        if self.page_title not in driver.title:
            msg = f'Page title: "{driver.title}" does not contains: "{self.page_title}"'
            raise ValidationError(msg)


class url_matches:
    def __init__(self, url_pattern):
        self.url_pattern = url_pattern

    def __call__(self, driver):
        match = re.search(self.url_pattern, driver.current_url)
        if not match:
            msg = f'URL pattern: "{match}" doesnt match "{driver.current_url}"'
            raise ValidationError(msg)


class url_is:
    def __init__(self, url):
        self.url = url

    def __call__(self, driver):
        if not self.url == driver.current_url:
            msg = f'URL: "{driver.current_url}" is not equal with: "{self.url}"'
            raise ValidationError(msg)


class url_contains:
    def __init__(self, url):
        self.url = url

    def __call__(self, driver):
        if self.url not in driver.current_url:
            msg = f'URL: "{driver.current_url}" does not contains: "{self.url}"'
            raise ValidationError(msg)


class page_contains_text:
    def __init__(self, text):
        self.text = text

    def __call__(self, driver):
        if self.text not in driver.page_source:
            msg = f'Page source does not contains: "{self.text}"'
            raise ValidationError(msg)
