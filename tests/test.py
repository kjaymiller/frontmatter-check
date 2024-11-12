import pyyaml

BASE_YAML = pyyaml.loads("""
---
    "name": "Jay Miller",
    "number": 25,
    "multiline_string": "It was the best of times
it was the worst of times",
---

This is some text
""")

CHECKING_YAML = """
"name":
"number":
"multiline_string":
"""
