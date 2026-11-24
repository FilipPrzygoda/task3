import pytest
from project.books.models import Book


# 1. Poprawne dane
def test_valid_book():
    book = Book("Pan Tadeusz", "Mickiewicz", 1834, "paper")
    assert book.name == "Pan Tadeusz"
    assert book.author == "Mickiewicz"
    assert book.year_published == 1834
    assert book.book_type == "paper"
    assert book.status == "available"


def test_valid_book_custom_status():
    book = Book("Lalka", "Prus", 1890, "ebook", status="borrowed")
    assert book.status == "borrowed"


# 2. Niepoprawne dane
def test_year_as_text():
    book = Book("Zła data", "Autor", "tysiąc osiemset", "paper")
    assert isinstance(book.year_published, int)


def test_empty_name():
    book = Book("", "Autor", 2000, "paper")
    assert book.name != ""


def test_empty_author():
    book = Book("Tytuł", "", 2000, "paper")
    assert book.author != ""


def test_none_values():
    book = Book(None, None, None, None)
    assert book.name is not None
    assert book.author is not None


def test_negative_year():
    book = Book("Przeszłość", "Autor", -500, "paper")
    assert book.year_published > 0


# 3. Wstrzyknięcie SQL i JavaScript
def test_sql_injection_name():
    payload = "'; DROP TABLE books; --"
    book = Book(payload, "Autor", 2000, "paper")
    assert "DROP TABLE" not in book.name


def test_sql_injection_author():
    payload = "Admin' OR '1'='1"
    book = Book("Tytuł", payload, 2000, "paper")
    assert "OR '1'='1" not in book.author


def test_js_injection_name():
    payload = "<script>alert('xss')</script>"
    book = Book(payload, "Autor", 2000, "paper")
    assert "<script>" not in book.name


def test_js_injection_book_type():
    payload = "<img src=x onerror=alert(1)>"
    book = Book("Tytuł", "Autor", 2000, payload)
    assert "onerror=" not in book.book_type


# 4. Warunki brzegowe i dane ekstremalne
def test_name_exactly_64_chars():
    book = Book("A" * 64, "Autor", 2000, "paper")
    assert len(book.name) == 64


def test_name_65_chars_over_limit():
    book = Book("A" * 65, "Autor", 2000, "paper")
    assert len(book.name) <= 64


def test_status_exactly_20_chars():
    book = Book("Status test", "Autor", 2000, "paper", status="A" * 20)
    assert len(book.status) == 20


def test_very_long_name():
    book = Book("A" * 100000, "Autor", 2000, "paper")
    assert len(book.name) <= 64


def test_year_huge_number():
    book = Book("Daleka przyszłość", "Autor", 10**12, "paper")
    assert book.year_published <= 2026


def test_null_bytes_in_name():
    book = Book("Tytuł\x00\x01", "Autor", 2000, "paper")
    assert "\x00" not in book.name


def test_unicode_and_emoji():
    book = Book("Книга 📚 日本語", "Autor", 2000, "paper")
    assert book.name == "Книга 📚 日本語"