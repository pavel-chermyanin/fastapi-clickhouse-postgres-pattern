import http.server
import os
import socketserver
import webbrowser

PORT = 8080
DIRECTORY = "."


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


def serve_schema():
    """Запускает локальный сервер для просмотра схемы базы данных."""
    if not os.path.exists("db_schema.html"):
        print(
            "Ошибка: файл db_schema.html не найден. Сначала запустите: python scripts/generate_schema.py"
        )
        return

    # Разрешаем повторное использование адреса (полезно при перезапусках в Docker)
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/db_schema.html"
        print(f"Сервер визуализации БД запущен на {url}")
        print("Нажмите Ctrl+C для остановки.")

        # Пытаемся открыть браузер, если мы не в Docker
        if not os.path.exists("/.dockerenv"):
            try:
                webbrowser.open(url)
            except Exception:
                pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")


if __name__ == "__main__":
    serve_schema()
