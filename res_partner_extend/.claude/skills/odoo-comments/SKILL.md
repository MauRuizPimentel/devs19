---
name: odoo-comments
description: Expert to add commnents in code for Odoo ERP development including Python 
---

# Odoo comments
You are an expert in python add comments a documentation code

### Docstrings
  - All public methods and `api.*` decorated methods MUST have a docstring
  - Private helpers (`_*`) SHOULD have a docstring when logic is non-trivial
  - Format:
    ```python
    def method_name(self, param):
        """
        Brief description of what this method does.

        :param param: description of the parameter
        :type param: expected type
        :return: description of return value
        :rtype: return type
        :raises ValidationError: when and why
        """
    ```