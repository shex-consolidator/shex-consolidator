class Namespace(object):
    def __init__(self, namespace_declaration):
        self._prefix, self._url = self._parse_declaration(namespace_declaration)

    def _parse_declaration(self, declaration: str):  # example --> PREFIX dc: <http://purl.org/dc/terms/>
        declaration = declaration.strip()
        prefix = declaration[7:declaration.find(":")].strip()
        url = declaration[declaration.find("<") + 1:declaration.rfind(">")]
        return prefix, url

    @property
    def prefix(self):
        return self._prefix

    @property
    def url(self):
        return self._url