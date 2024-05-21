#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from pathlib import Path
import ind
import unittest


# Для индивидуального задания лабораторной
# работы 2.21 добавьте тесты с использованием
# модуля unittest, проверяющие операции по работе
# с базой данных. Вариант 29


class CreateDBtests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nТестирование функции, создающей базу данных.")
        print("-----------------------------------")

    @classmethod
    def tearDownClass(cls):
        print("OK")
        print("-----------------------------------")

    def setUp(self):
        self.db_path = Path("create_test.db")

    def tearDown(self):
        if self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            conn.close()
            self.db_path.unlink()

    def test_create_db(self):
        '''Тестирование работы функции, создающей базу данных.'''
        ind.create_db(self.db_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        self.assertIn(('routes',), tables)
        self.assertIn(('end_stations',), tables)
        conn.close()


class AddTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nТестирование функции добавления маршрута.")
        print("-----------------------------------")

    @classmethod
    def tearDownClass(cls):
        print("OK")
        print("-----------------------------------")

    def setUp(self):
        self.db_path = Path("test_add.db")

    def tearDown(self):
        if self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            conn.close()
            self.db_path.unlink()

    def test_add_route(self):
        '''Тестирование работы функции, добавляющей маршрут в базу данных.'''
        ind.create_db(self.db_path)
        ind.add_route(self.db_path, "Stavropol", "Krasnodar", 1)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT routes.start_name, end_stations.station_title,
            routes.route_number
            FROM routes
            INNER JOIN end_stations ON
            end_stations.station_id = routes.station_id
            """
        )
        route = cursor.fetchone()
        self.assertIsNotNone(route)
        self.assertEqual(route[0], "Stavropol")
        self.assertEqual(route[1], "Krasnodar")
        self.assertEqual(route[2], 1)

        conn.close()


class SelectTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nТестирование функций выделения маршрутов.")
        print("-----------------------------------")

    @classmethod
    def tearDownClass(cls):
        print("OK")
        print("-----------------------------------")

    def setUp(self):
        self.db_path = Path("select_tests.db")
        ind.create_db(self.db_path)

    def tearDown(self):
        if self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            conn.close()
            self.db_path.unlink()

    def test_select_routes(self):
        '''Тестирование вывода маршрутов с заданным параметром.'''
        ind.add_route(self.db_path, "A", "B", 1)
        ind.add_route(self.db_path, "B", "C", 2)
        ind.add_route(self.db_path, "C", "D", 3)
        routes = ind.select_routes(self.db_path, "B")
        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0]["start"], "A")
        self.assertEqual(routes[0]["end"], "B")
        self.assertEqual(routes[0]["number"], 1)
        self.assertEqual(routes[1]["start"], "B")
        self.assertEqual(routes[1]["end"], "C")
        self.assertEqual(routes[1]["number"], 2)

    def test_select_all(self):
        '''Тестирование вывода всех маршрутов.'''
        ind.add_route(self.db_path, "A", "B", 1)
        ind.add_route(self.db_path, "C", "D", 2)
        routes = ind.select_all(self.db_path)
        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0]["start"], "A")
        self.assertEqual(routes[0]["end"], "B")
        self.assertEqual(routes[0]["number"], 1)
        self.assertEqual(routes[1]["start"], "C")
        self.assertEqual(routes[1]["end"], "D")
        self.assertEqual(routes[1]["number"], 2)


if __name__ == '__main__':
    unittest.main()
