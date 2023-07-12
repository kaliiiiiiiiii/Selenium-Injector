# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# edited by kaliiiiiiiiiii

import warnings
from base64 import b64decode

from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.shadowroot import ShadowRoot

from selenium_injector.scripts.socket import JSEvalException


class BaseElement:
    def __init__(self, injector, tab_id):
        self._tab_id = tab_id
        self._injector = injector
        self.t = injector.socket.js.types
        self._by = By.XPATH
        self._value = "/"

    def _exec(self, type_dict: dict, max_depth: int = 2, debug: bool = True, timeout=10):
        try:
            return self._injector.tabs.exec(type_dict=type_dict, tab_id=self._tab_id, max_depth=max_depth,
                                            debug=debug, timeout=timeout)
        except JSEvalException as e:
            self._handle_js_exc(e)

    def _handle_js_exc(self, e):
        if e.message[:41] == "TypeError: Cannot read properties of null":
            locator = {"method": self._by, "selector": self._value}
            raise NoSuchElementException(f"Unable to locate element:{locator}")
        else:
            raise e


    @property
    def raw(self):
        result = self._exec(self._raw, timeout=4, max_depth=2)['result']
        if not result:
            raise NoSuchElementException()

    def get_property(self, name):
        """Gets the given property of the element.

        :Args:
            - name - Name of the property to retrieve.

        :Usage:
            ::

                text_length = target_element.get_property("text_length")
        """
        return self._exec(self._get_property(name), timeout=4, max_depth=2)['result'][0]

    def _get_property(self, name: str):
        return self.t.path(name, obj=self._raw)

    @property
    def _raw(self):
        return self.t.path("document")


# noinspection PyProtectedMember
class WebElement(BaseElement):
    """Represents a DOM element.

    Generally, all interesting operations that interact with a document will be
    performed through this interface.

    All method calls will do a freshness check to ensure that the element
    reference is still valid.  This essentially determines whether the
    element is still attached to the DOM.  If this test fails, then an
    ``StaleElementReferenceException`` is thrown, and all future calls to this
    instance will fail.
    """

    def __init__(self, by: str, value: str, tab_id: int, injector, parent=None) -> None:
        super().__init__(tab_id=tab_id, injector=injector)
        self._by = by
        self._value = value
        if not parent:
            parent = BaseElement(tab_id=tab_id, injector=injector)
        self._parent = parent

        # noinspection PyStatementEffect
        self.raw  # check existence

    @property
    def _raw(self):
        return self._find_element(by=self._by, value=self._value, base_element=self.parent)

    @property
    def tag_name(self) -> str:
        """This element's ``tagName`` property."""
        return self.get_property("tagName")

    @property
    def text(self) -> str:
        """The text of the element."""
        try:
            return self.get_property("textContent")
        except IndexError:
            return ''

    def click(self) -> None:
        """Clicks the element."""
        self._exec(self._click)

    @property
    def _click(self):
        try:
            return self.t.exec(self.t.path("click", obj=self._raw))
        except JSEvalException as e:
            self._handle_js_exc(e)

    def submit(self):
        """Submits a form."""
        script = (
            "/* submitForm */var form = arguments[0];\n"
            'while (form.nodeName != "FORM" && form.parentNode) {\n'
            "  form = form.parentNode;\n"
            "}\n"
            "if (!form) { throw Error('Unable to find containing form element'); }\n"
            "if (!form.ownerDocument) { throw Error('Unable to find owning document'); }\n"
            "var e = form.ownerDocument.createEvent('Event');\n"
            "e.initEvent('submit', true, true);\n"
            "if (form.dispatchEvent(e)) { HTMLFormElement.prototype.submit.call(form) }\n"
        )
        raise NotImplementedError()

    def clear(self) -> None:
        """Clears the text if it's a text entry element."""
        self._exec(self.t.exec(self.t.path("reset"), obj=self._raw))

    def get_dom_attribute(self, name: str) -> str:
        """Gets the given attribute of the element. Unlike
        :func:`~selenium.webdriver.remote.BaseWebElement.get_attribute`, this
        method only returns attributes declared in the element's HTML markup.

        :Args:
            - name - Name of the attribute to retrieve.

        :Usage:
            ::

                text_length = target_element.get_dom_attribute("class")
        """
        raise NotImplementedError("you might use get_attribute instead")

    def get_attribute(self, name):
        """Gets the given attribute or property of the element.

        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, ``None`` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-``None`` values are returned
        as strings.  For attributes or properties which do not exist, ``None``
        is returned.

        To obtain the exact value of the attribute or property,
        use :func:`~selenium.webdriver.remote.BaseWebElement.get_dom_attribute` or
        :func:`~selenium.webdriver.remote.BaseWebElement.get_property` methods respectively.

        :Args:
            - name - Name of the attribute/property to retrieve.

        Example::

            # Check if the "active" CSS class is applied to an element.
            is_active = "active" in target_element.get_attribute("class")
        """
        return self.get_property(name=name)

    def is_selected(self) -> bool:
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
        """
        result = self.get_property("checked")
        if result:
            return True
        else:
            return False

    def is_enabled(self) -> bool:
        """Returns whether the element is enabled."""
        return not self.get_property("disabled")

    def send_keys(self, *value) -> None:
        """Simulates typing into the element.

        :Args:
            - value - A string for typing, or setting form fields.  For setting
              file inputs, this could be a local file path.

        Use this to send simple key events or to fill out form fields::

            form_textfield = driver.find_element(By.NAME, 'username')
            form_textfield.send_keys("admin")

        This can also be used to set file inputs.

        ::

            file_input = driver.find_element(By.NAME, 'profilePic')
            file_input.send_keys("path/to/profilepic.gif")
            # Generally it's better to wrap the file path in one of the methods
            # in os.path to return the actual path to support cross OS testing.
            # file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))
        """
        # transfer file to another machine only if remote driver is used
        # the same behaviour as for java binding
        raise NotImplementedError()

    @property
    def shadow_root(self) -> ShadowRoot:
        """Returns a shadow root of the element if there is one or an error.
        Only works from Chromium 96, Firefox 96, and Safari 16.4 onwards.

        :Returns:
          - ShadowRoot object or
          - NoSuchShadowRoot - if no shadow root was attached to element
        """
        raise NotImplementedError()

    # RenderedWebElement Items
    def is_displayed(self) -> bool:
        """Whether the element is visible to a user."""
        # Only go into this conditional for browsers that don't use the atom themselves
        raise NotImplementedError()

    @property
    def location_once_scrolled_into_view(self) -> dict:
        """THIS PROPERTY MAY CHANGE WITHOUT WARNING. Use this to discover where
        on the screen an element is so that we can click it. This method should
        cause the element to be scrolled into view.

        Returns the top lefthand corner location on the screen, or zero
        coordinates if the element is not visible.
        """
        "arguments[0].scrollIntoView(true); return arguments[0].getBoundingClientRect()"
        self.t.exec(self.t.path("scrollIntoView", obj=self._raw), args=[True])
        result = self.rect
        return {"x": round(result["x"]), "y": round(result["y"])}

    @property
    def size(self) -> dict:
        """The size of the element."""
        size = self.rect
        return {"height": size["height"], "width": size["width"]}

    def value_of_css_property(self, property_name) -> str:
        """The value of a CSS property."""
        raise NotImplementedError("you might use get_attribute instead")

    @property
    def location(self) -> dict:
        """The location of the element in the renderable canvas."""
        result = self.rect
        return {"x": round(result["x"]), "y": round(result["y"])}

    @property
    def rect(self) -> dict:
        """A dictionary with the size and location of the element."""
        result = self._exec(self._rect)["result"][0]
        del result['toJSON']
        return result

    @property
    def _rect(self):
        return self.t.exec(self.t.path("getBoundingClientRect", obj=self._raw))

    @property
    def aria_role(self) -> str:
        """Returns the ARIA role of the current web element."""
        raise NotImplementedError()

    @property
    def accessible_name(self) -> str:
        """Returns the ARIA Level of the current webelement."""
        raise NotImplementedError()

    @property
    def screenshot_as_base64(self) -> str:
        """Gets the screenshot of the current element as a base64 encoded
        string.

        :Usage:
            ::

                img_b64 = element.screenshot_as_base64
        """
        raise NotImplementedError()

    @property
    def screenshot_as_png(self) -> bytes:
        """Gets the screenshot of the current element as a binary data.

        :Usage:
            ::

                element_png = element.screenshot_as_png
        """
        return b64decode(self.screenshot_as_base64.encode("ascii"))

    def screenshot(self, filename) -> bool:
        """Saves a screenshot of the current element to a PNG image file.
        Returns False if there is any IOError, else returns True. Use full
        paths in your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to. This
           should end with a `.png` extension.

        :Usage:
            ::

                element.screenshot('/Screenshots/foo.png')
        """
        if not filename.lower().endswith(".png"):
            warnings.warn(
                "name used for saved screenshot does not match file " "type. It should end with a `.png` extension",
                UserWarning,
            )
        png = self.screenshot_as_png
        try:
            with open(filename, "wb") as f:
                f.write(png)
        except OSError:
            return False
        finally:
            del png
        return True

    @property
    def parent(self):
        """Internal reference to the WebDriver instance this element was found
        from."""
        return self._parent

    def __eq__(self, element):
        raise NotImplementedError()

    def __ne__(self, element):
        raise NotImplementedError()

    def _find_element(self, by=By.ID, value=None, base_element=None):
        from selenium_injector.types.by import By

        if not base_element:
            base_element = self
        if by == By.ID:
            by = By.CSS_SELECTOR
            value = f'[id="{value}"]'
        elif by == By.CLASS_NAME:
            by = By.CSS_SELECTOR
            value = f".{value}"
        elif by == By.NAME:
            by = By.CSS_SELECTOR
            value = f'[name="{value}"]'

        if by == By.XPATH:
            return self.t.path("singleNodeValue",
                               obj=self.t.exec(self.t.path("document.evaluate"), args=[
                                   self.t.value(value),
                                   base_element._raw, self.t.value(None),
                                   self.t.value(9),  # "XPathResult.FIRST_ORDERED_NODE_TYPE"
                                   self.t.value(None)
                               ])
                               )
        elif by == By.TAG_NAME:
            return self.t.exec(self.t.path("getElementsByTagName", obj=base_element._raw), args=[
                self.t.value(value)
            ])
        elif by == By.CSS_SELECTOR:
            return self.t.exec(self.t.path("querySelector", obj=base_element._raw), args=[
                self.t.value(value)
            ])
        else:
            raise ValueError("by needs to be selenium.webdriver.common.by.by.py")

    def find_element(self, by=By.ID, value=None, base_element=None):
        """Find an element given a By strategy and locator.

        :Usage:
            ::

                element = element.find_element(By.ID, 'foo')

        :rtype: WebElement
        """
        return self._exec(self._find_element(by=by, value=None))["result"][0]

    def find_elements(self, by=By.ID, value=None):
        """Find elements given a By strategy and locator.

        :Usage:
            ::

                element = element.find_elements(By.CLASS_NAME, 'foo')

        :rtype: list of WebElement
        """
        raise NotImplementedError()
