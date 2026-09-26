import unittest

from clash_lint.lint import lint_text

OK = """
mixed-port: 7890
proxies:
  - name: example
    type: ss
    server: example.com
    port: 443
rules:
  - DOMAIN-SUFFIX,example.com,DIRECT
"""


class LintTest(unittest.TestCase):
    def test_ok(self) -> None:
        self.assertEqual(lint_text(OK), [])

    def test_duplicate_name_and_bad_port(self) -> None:
        text = """
proxies:
  - {name: a, type: ss, server: example.com, port: 1}
  - {name: a, type: made-up, server: "", port: 0}
"""
        found = lint_text(text)
        messages = " ".join(item.message for item in found)
        self.assertIn("重复", messages)
        self.assertIn("不是已知的代理类型", messages)
        self.assertIn("缺少 server", messages)
        self.assertIn("端口", messages)

    def test_bad_yaml(self) -> None:
        found = lint_text("proxies: [")
        self.assertEqual(found[0].level, "error")
        self.assertIn("YAML", found[0].message)

    def test_rules_shape(self) -> None:
        text = "proxies: []\nrules:\n  - not-a-rule\n"
        found = lint_text(text)
        self.assertTrue(any("TYPE,value,policy" in item.message for item in found))


if __name__ == "__main__":
    unittest.main()
