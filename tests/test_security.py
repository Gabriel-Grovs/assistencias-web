"""Testes de segurança da aplicação Flask (login, rate-limiting, anti-injection, headers)."""

import unittest
from app import app, _LOGIN_FAILURES, _clear_failures


class SecurityTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        _LOGIN_FAILURES.clear()

    def tearDown(self):
        _LOGIN_FAILURES.clear()

    def test_security_headers_present(self):
        """Verifica se headers de segurança estão presentes nas respostas."""
        response = self.client.get("/login")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertIn("Content-Security-Policy", response.headers)

    def test_login_success(self):
        """Login com senha correta deve autenticar e redirecionar para index."""
        response = self.client.post("/login", data={"password": "123gabriel"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/")

    def test_login_invalid_password(self):
        """Senha incorreta deve retornar erro com contagem de tentativas."""
        response = self.client.post("/login", data={"password": "wrongpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Senha incorreta", response.get_data(as_text=True))

    def test_sql_injection_attempt_blocked(self):
        """Tentativas clássicas de SQL Injection devem ser detectadas e bloqueadas com 400."""
        sqli_payloads = [
            "' OR '1'='1",
            "' UNION SELECT null, null--",
            "admin'--",
            "'; DROP TABLE users--",
        ]
        for payload in sqli_payloads:
            response = self.client.post("/login", data={"password": payload})
            self.assertEqual(response.status_code, 400)
            self.assertIn("injeção maliciosa", response.get_data(as_text=True))

    def test_null_byte_injection_blocked(self):
        """Tentativa com null bytes deve ser rejeitada imediatamente."""
        response = self.client.post("/login", data={"password": "pass\x00word"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Entrada inválida", response.get_data(as_text=True))

    def test_rate_limiting_lockout(self):
        """Após 5 falhas consecutivas, o IP deve ser bloqueado com status 429."""
        for _ in range(5):
            self.client.post("/login", data={"password": "wrongpassword"})

        # A 6ª tentativa deve ser bloqueada por rate limit
        response = self.client.post("/login", data={"password": "wrongpassword"})
        self.assertEqual(response.status_code, 429)
        self.assertIn("bloqueado temporariamente", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
