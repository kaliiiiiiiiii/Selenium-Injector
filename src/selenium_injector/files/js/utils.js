globalThis.utils = {"find_element":{}}

utils.find_element.ByXpath = function(path) {
    var element = document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
    if(!(element)){throw new Error("Element by XPATH:"+path+" not found!")};
    return element;
}
