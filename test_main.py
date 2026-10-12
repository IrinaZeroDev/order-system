"""Тесты работы с базой заказов. Запуск: python -m unittest -v"""
import tempfile
import unittest
from pathlib import Path

import main


class OrdersTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = Path(tmp.name) / 'orders.db'
        main.init_db(self.db)

    def test_add_order_is_new(self):
        first = main.add_order('Анна', 'Торт «Наполеон»', self.db)
        second = main.add_order('  Пётр ', ' Пицца ', self.db)
        self.assertEqual((first, second), (1, 2))
        self.assertEqual(main.get_orders(self.db), [
            (1, 'Анна', 'Торт «Наполеон»', 'Новый'),
            (2, 'Пётр', 'Пицца', 'Новый'),
        ])

    def test_empty_fields_are_rejected(self):
        for name, details in (('', 'Пицца'), ('Анна', '   '), (' ', '')):
            with self.subTest(name=name, details=details):
                with self.assertRaises(ValueError):
                    main.add_order(name, details, self.db)
        self.assertEqual(main.get_orders(self.db), [])

    def test_sql_injection_is_stored_as_text(self):
        evil = "x', 'y', 'z'); DROP TABLE orders; --"
        main.add_order(evil, 'Пицца', self.db)
        self.assertEqual(main.get_orders(self.db)[0][1], evil)

    def test_init_db_twice_keeps_data(self):
        main.add_order('Анна', 'Торт', self.db)
        main.init_db(self.db)
        self.assertEqual(len(main.get_orders(self.db)), 1)


if __name__ == '__main__':
    unittest.main()
