import unittest
from urllib.request import urlopen

from browser import HOME_URL, address_to_url
from quantum_app.app import create_server


class AddressToUrlTests(unittest.TestCase):
    def test_keeps_complete_https_url(self):
        self.assertEqual(address_to_url("https://example.com/a"), "https://example.com/a")

    def test_adds_https_to_domain(self):
        self.assertEqual(address_to_url("example.com"), "https://example.com")

    def test_supports_localhost(self):
        self.assertEqual(address_to_url("localhost:8000"), "http://localhost:8000")

    def test_converts_words_to_search(self):
        self.assertEqual(
            address_to_url("quantum computing"),
            "https://www.google.com/search?q=quantum+computing",
        )

    def test_empty_address_uses_home(self):
        self.assertEqual(address_to_url("  "), HOME_URL)


class QuantumEngineTests(unittest.TestCase):
    def test_quantum_engine_serves_embedded_app(self):
        server = create_server()
        try:
            host, port = server.server_address
            import threading

            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            with urlopen(f"http://{host}:{port}/", timeout=2) as response:
                page = response.read().decode()
            self.assertIn("Quantum Circuit Lab", page)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
