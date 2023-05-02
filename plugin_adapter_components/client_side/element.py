class Element:
    def __init__(self, css_selector, title, value, expect):
        self.value = value
        self.title = title
        self.css_selector = css_selector
        self.expect = expect

