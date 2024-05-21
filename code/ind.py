#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Использовать SQLite для хранения данных
# Вариант 29

import argparse
import sqlite3
import typing as t
from pathlib import Path


def display_routes(staff: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список маршрутов
    """
    if staff:
        line = "+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 20, "-" * 10
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^20} | {:^10} |".format(
                "№", "Начальный пункт", "Конечный пункт", "Номер"
            )
        )
        print(line)

        for idx, route in enumerate(staff, 1):
            print(
                "| {:>4} | {:<30} | {:<20} | {:>8} |".format(
                    idx,
                    route.get("start", ""),
                    route.get("end", ""),
                    route.get("number", 0),
                )
            )
            print(line)
    else:
        print("Список  маршрутов пуст.")


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Таблица с конечными станциями.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS end_stations (
            station_id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_title TEXT NOT NULL
        )
        """
    )
    # Таблица с начальными станциями и номерами маршрутов.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_name TEXT NOT NULL,
            station_id INTEGER NOT NULL,
            route_number INTEGER NOT NULL,
            FOREIGN KEY(station_id) REFERENCES end_stations(station_id)
        )
        """
    )
    conn.close()


def add_route(
    database_path: Path, start_name: str, end_stations: str, number: int
) -> None:
    """
    Добавить маршрут.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT station_id FROM end_stations WHERE station_title = ?
        """,
        (end_stations,),
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO end_stations (station_title) VALUES (?)
            """,
            (end_stations,),
        )
        station_id = cursor.lastrowid
    else:
        station_id = row[0]

    cursor.execute(
        """
        INSERT INTO routes (start_name, station_id, route_number)
        VALUES (?, ?, ?)
        """,
        (start_name, station_id, number),
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех маршруты.
    """
    conn = sqlite3.connect(database_path)
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
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "start": row[0],
            "end": row[1],
            "number": row[2],
        }
        for row in rows
    ]


def select_routes(database_path: Path, station) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все маршруты, начальный или
    конечный пункт которых равен заданному.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT routes.start_name, end_stations.station_title,
        routes.route_number
        FROM routes
        INNER JOIN end_stations ON
        end_stations.station_id = routes.station_id
        WHERE routes.start_name = ? OR end_stations.station_title = ?
        """,
        (station, station,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "start": row[0],
            "end": row[1],
            "number": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "routes.db"),
        help="The data file name",
    )

    parser = argparse.ArgumentParser("routes")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new route"
    )
    add.add_argument(
        "-s",
        "--start",
        action="store",
        required=True,
        help="The start station name",
    )
    add.add_argument(
        "-e",
        "--end",
        action="store",
        required=True,
        help="The end station name",
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        required=True,
        help="Number of route",
    )

    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display all routes"
    )

    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Select the routes"
    )
    select.add_argument(
        "--sr",
        action="store",
        required=True,
        help="Select the route",
    )
    args = parser.parse_args(command_line)

    db_path = Path(args.db)
    create_db(db_path)
    if args.command == "add":
        add_route(db_path, args.start, args.end, args.number)

    elif args.command == "display":
        display_routes(select_all(db_path))

    elif args.command == "select":
        display_routes(select_routes(db_path, args.sr))
        pass


if __name__ == "__main__":
    main()
