import unittest
from types import SimpleNamespace
from unittest.mock import patch

import psutil

from svcboard.cli import _render_markdown
from svcboard.core import Service, scan


class ScanTests(unittest.TestCase):
    def test_scan_filters_listeners_and_sorts_results(self):
        connections = [
            SimpleNamespace(
                status=psutil.CONN_ESTABLISHED,
                laddr=SimpleNamespace(ip="127.0.0.1", port=9000),
                pid=10,
            ),
            SimpleNamespace(
                status=psutil.CONN_LISTEN,
                laddr=SimpleNamespace(ip="127.0.0.1", port=8100),
                pid=11,
            ),
            SimpleNamespace(
                status=psutil.CONN_LISTEN,
                laddr=SimpleNamespace(ip="0.0.0.0", port=8100),
                pid=12,
            ),
        ]

        with patch("svcboard.core.psutil.net_connections", return_value=connections):
            with patch("svcboard.core.psutil.Process") as process_type:
                process_type.return_value.name.return_value = "python"
                process_type.return_value.cmdline.return_value = ["python", "app.py"]
                services = scan()

        self.assertEqual([(s.port, s.host) for s in services], [
            (8100, "0.0.0.0"),
            (8100, "127.0.0.1"),
        ])
        self.assertEqual(services[0].name, "python")
        self.assertEqual(services[0].cmdline, "python app.py")

    def test_markdown_escapes_command_separators(self):
        service = Service(
            port=8100,
            host="127.0.0.1",
            proto="tcp",
            pid=None,
            name="python",
            cmdline="python app.py|--debug\nnext",
            hint=None,
        )

        markdown = _render_markdown([service])

        self.assertIn("python app.py\\|--debug next", markdown)


if __name__ == "__main__":
    unittest.main()
