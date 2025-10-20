from splinter import Browser
from xmldiff import main
from lxml import etree
from io import StringIO
import re
import time

# This class executes labels on the SUT and generates responses
class SeleniumSut:
    """
    Constructor
    """
    def __init__(self, logger, responses, event_queue, headless):
        self.logger = logger
        self.responses = responses
        self.event_queue = event_queue
        self.headless = headless
        self.browser = None
        self.page_source = ''

        # Tunables to align with harness timeouts
        self.find_wait_css = 2.0     # seconds for CSS probes
        self.find_wait_text = 0.1   # seconds for text probes
        self.action_wait_cap = 2.0   # seconds to wait after click before responding

        self.logger.debug("Sut", "Init: headless={}".format(self.headless))

    """
    Special function: class name
    """
    def __name__(self):
        return "Sut"

    """
    Perform any cleanup if the selenium has stopped
    """
    def stop(self):
        self.logger.info("Sut", "Selenium has stopped testing the SUT")
        self.responses = []
        try:
            if self.browser:
                self.browser.quit()
                self.logger.debug("Sut", "Browser quit")
        except Exception as e:
            self.logger.debug("Sut", "Browser quit error: {}".format(e))

    """
    Add the response  to the response stack from the
    Handler class.
    param [[String, {String : String}, {String: String}]] selector
    """
    def handle_response(self, response):
        self.logger.debug("Sut", "Add response: {}".format(response))
        self.responses.append(response)

    # =============================
    # Utilities
    # =============================

    def _normalize_ws_py(self, s: str) -> str:
        """Python-side whitespace normalize (trim + collapse)."""
        return " ".join((s or "").split())

    def _element_text_normalized(self, el):
        """
        Return case-sensitive, whitespace-normalized text for comparison.
        For <input>, prefer @value; else use element.text.
        """
        try:
            tag = getattr(el, 'tag_name', '').lower()
        except Exception:
            tag = ''
        txt = None
        try:
            if tag == "input":
                txt = el._element.get_attribute("value")
            if txt is None:
                txt = el.text
        except Exception:
            txt = ""
        return self._normalize_ws_py(txt)

    def _safe_tag_role(self, el):
        tag = None
        role = None
        try:
            tag = getattr(el, 'tag_name', None)
        except Exception:
            pass
        try:
            if hasattr(el, '_element'):
                role = el._element.get_attribute("role")
        except Exception:
            pass
        return tag, role

    # =============================
    # XPath helpers (TEXT search)
    # =============================

    def _xpath_literal(self, s: str) -> str:
        """Return an XPath string literal for arbitrary text (handles quotes)."""
        if "'" not in s:
            return "'{}'".format(s)
        if '"' not in s:
            return '"{}"'.format(s)
        # Contains both quote types: concat('foo', "'", 'bar')
        parts = s.split("'")
        return "concat(" + ",".join(["'{}'".format(p) for p in parts[:-1]] + ['"\'"'] + ["'{}'".format(parts[-1])]) + ")"

    def _xpath_for_case_sensitive_normalized_text_deepest(self, text: str) -> str:
        """
        XPath for the DEEPEST element whose text equals `text` EXACTLY (case-sensitive),
        with whitespace normalized on both sides (trim + collapse).
        Avoids matching containers that merely contain the same text.
        """
        needle = " ".join(text.split())
        lit = self._xpath_literal(needle)
        xpath = (
            "//*[normalize-space(string(.)) = {L} and not(.//*[normalize-space(string(.)) = {L}])]"
            .format(L=lit)
        )
        self.logger.debug("Sut", "Deepest exact-text (case-sensitive, ws-normalized) XPath for '{}': {}".format(text, xpath))
        return xpath

    # =============================
    # Selector Resolution
    # =============================

    def sanitize_selector(self, selector: str) -> str:
        """
        Loosens strict CSS selectors: converts exact href matches to partial,
        removes IDs, and normalizes spacing. Only applied to CSS attempts.
        """
        original = selector
        selector = re.sub(r"\[href=['\"](.*?)['\"]\]", r"[href*='\1']", selector)
        selector = re.sub(r"#\w+", "", selector)
        selector = re.sub(r"\s+", " ", selector).strip()
        if selector != original:
            self.logger.debug("Sut", "Sanitize selector: '{}' -> '{}'".format(original, selector))
        return selector

    def _find_by_css(self, css: str):
        if not css:
            return None
        self.logger.debug("Sut", "_find_by_css: '{}'".format(css))
        if self.browser.is_element_present_by_css(css, wait_time=self.find_wait_css):
            els = self.browser.find_by_css(css)
            self.logger.debug("Sut", "_find_by_css: found {} matches".format(len(els)))
            return els
        self.logger.debug("Sut", "_find_by_css: no matches")
        return None

    def _find_by_text_deepest(self, text: str):
        self.logger.debug("Sut", "_find_by_text_deepest: '{}' (wait_time={})".format(text, self.find_wait_text))
        xp = self._xpath_for_case_sensitive_normalized_text_deepest(text)
        if self.browser.is_element_present_by_xpath(xp, wait_time=self.find_wait_text):
            el = self.browser.find_by_xpath(xp).first
            t, r = self._safe_tag_role(el)
            self.logger.debug("Sut", "Text match element (deepest): tag={} role={}".format(t, r))
            return el
        self.logger.debug("Sut", "_find_by_text_deepest: no matches")
        return None

    def _resolve_css_text(self, css: str, text: str):
        """
        Core resolver for the new API (two inputs).
          - css and text both provided:
              * find CSS matches
              * pick the one whose own normalized text == text (case-sensitive)
              * if none, search for a deepest descendant inside each CSS match that equals text; click that
          - css only:
              * first CSS match (sanitized fallback)
          - text only:
              * deepest text match in the document
        Returns element or None.
        """
        css = (css or "").strip()
        text = (text or "").strip()
        self.logger.debug("Sut", "_resolve_css_text: css='{}' text='{}'".format(css, text))

        # Both css and text present
        if css and text:
            els = self._find_by_css(css)
            if not els:
                sane = self.sanitize_selector(css)
                if sane != css:
                    els = self._find_by_css(sane)
            if els:
                needle = self._normalize_ws_py(text)
                # 1) try element itself
                for el in els:
                    if self._element_text_normalized(el) == needle:
                        self.logger.debug("Sut", "Resolved by CSS+TEXT on element itself")
                        return el
                # 2) try deepest matching descendant under each candidate
                lit = self._xpath_literal(needle)
                rel_xp = ".//*[normalize-space(string(.)) = {L} and not(.//*[normalize-space(string(.)) = {L}])]".format(L=lit)
                for el in els:
                    try:
                        if el.is_element_present_by_xpath(rel_xp, wait_time=self.find_wait_text):
                            desc = el.find_by_xpath(rel_xp).first
                            t, r = self._safe_tag_role(desc)
                            self.logger.debug("Sut", "Resolved by CSS+TEXT descendant: tag={} role={}".format(t, r))
                            return desc
                    except Exception:
                        continue
            self.logger.debug("Sut", "No element satisfies CSS+TEXT combined")
            return None

        # Only css
        if css:
            els = self._find_by_css(css)
            if els:
                return els.first
            sane = self.sanitize_selector(css)
            if sane != css:
                els = self._find_by_css(sane)
                if els:
                    return els.first
            return None

        # Only text
        if text:
            return self._find_by_text_deepest(text)

        # Neither provided
        return None

    # =============================
    # Public Actions (two-arg click)
    # =============================

    """
    Simulates a click on an element specified by the selector and generates a response.
    Accepts two explicit params:
      - css : string (can be empty "")
      - text: string (can be empty "")
    Resolution:
      - css & text → CSS filtered by case-sensitive, ws-normalized text (or matching descendant)
      - css only   → CSS (sanitized fallback)
      - text only  → deepest text match
    """
    def click(self, css, text):
        self.logger.debug("Sut", "Click: css='{}' text='{}'".format(css, text))
        element = self._resolve_css_text(css, text)
        if not element:
            raise Exception("Element not found using css='{}' text='{}'".format(css, text))

        element.is_visible()
        old_url = self.browser.url
        self.logger.debug("Sut", "URL before click: {}".format(old_url))
        self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element._element)
        try:
            self.browser.execute_script(
                "arguments[0].dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, composed:true}));",
                element._element,
            )
        except Exception:
            self.browser.execute_script("arguments[0].click();", element._element)

        # Wait for URL to change (capped under action_wait_cap)
        deadline = time.time() + self.action_wait_cap
        while time.time() < deadline:
            time.sleep(0.25)
            now = self.browser.url
            self.logger.debug("Sut", "Waiting for URL change: now={}".format(now))
            if now != old_url:
                break

        self.logger.debug("Sut", "URL after click: {}".format(self.browser.url))
        self.generate_response()

    def accept_alert(self):
        self.logger.debug("Sut", "Accept alert")
        self.browser.driver.switch_to.alert.accept()

    """
    Navigates to the specified URL and generates a response.
    param : [String] url
    """
    def visit(self, url):
        self.logger.debug("Sut", "Visit: {}".format(url))
        self.browser.visit(url)
        self.generate_response()

    """
    Enters the provided value into an input field.
    You can pass either a CSS-only locator via css, or a TEXT-only locator via text,
    or both (the element must satisfy both).
    param [String] css
    param [String] text
    param [String] value
    """
    def fill_in(self, css, text, value):
        self.logger.debug("Sut", "Fill In: css='{}' text='{}'".format(css, text))
        element = self._resolve_css_text(css, text)
        if not element:
            raise Exception("Element not found for fill_in using css='{}' text='{}'".format(css, text))
        element.is_visible()
        self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", element._element)
        tag, role = self._safe_tag_role(element)
        self.logger.debug("Sut", "Fill target tag={} role={} value_len={}".format(tag, role, len(str(value)) if value is not None else 0))
        # Set value and fire input event for frameworks
        self.browser.execute_script(
            "arguments[0].setAttribute('value', arguments[1]);",
            element._element,
            value,
        )
        self.browser.execute_script(
            "var e = new Event('input', { bubbles: true }); arguments[0].dispatchEvent(e);",
            element._element,
        )
        self.generate_response()

    """
    Creates a new Selenium browser instance.
    """
    def start(self):
        self.logger.debug("Sut", "Start browser: headless={}".format(self.headless))
        self.browser = Browser('chrome', headless=self.headless)
        self.browser.wait_time = 10
        self.logger.debug("Sut", "Browser started: wait_time={}".format(self.browser.wait_time))

    """
    Generates a response containing the current page's title and URL.
    """
    def generate_response(self):
        self.page_source = self.browser.html
        response = [
            "page_title",
            {"_title": "string", "_url": "string"},
            {"_title": self.browser.title, "_url": self.browser.url}
        ]
        self.logger.debug("Sut", "Generate response title='{}' url='{}'".format(self.browser.title, self.browser.url))
        self.handle_response(response)

    """
    Compares the page source before and after an action,
    detects updates, and generates a response.
    """
    def get_updates(self):
        self.logger.debug("Sut", "Get updates")
        if not self.page_source:
            self.logger.debug("Sut", "No previous page_source; skipping diff")
            return

        before = self.page_source
        after = self.browser.html

        parser = etree.HTMLParser()

        before = etree.parse(StringIO(before), parser)
        after = etree.parse(StringIO(after), parser)

        results = main.diff_trees(before, after)

        nodes = {}
        for result in results:
            attributes = {}
            fields = result._fields
            for field in fields:
                attributes[field] = str(getattr(result, field))

            if type(result).__name__ not in ['MoveNode', 'RenameNode']:
                if type(result).__name__ in nodes:
                    nodes[type(result).__name__].append(attributes)
                else:
                    nodes[type(result).__name__] = [attributes]

        if nodes:
            self.logger.debug("Sut", "DOM updates: {} groups".format(len(nodes)))
            response = ["page_update", {'nodes': 'struct'}, {'nodes': nodes}]
            self.handle_response(response)
        else:
            self.logger.debug("Sut", "No DOM updates detected")

        self.page_source = self.browser.html
