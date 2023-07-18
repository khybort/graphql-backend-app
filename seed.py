import sys

from mongoengine import connect

import core.seeders as seeders

client = connect("app", host="mongodb://mongo:27017/")

TABLES = {
    "roles": seeders.role,
    "users": seeders.user,
}


def seed(table=None):
    if table:
        TABLES[table].seed()
        print(f"Seeded {table}")
        sys.exit(0)
    for seeder in TABLES.values():
        seeder.seed()
        print(f"Seeded {seeder.__name__}")


def delete_all(table=None):
    if table:
        TABLES[table].delete_all()
        print(f"Deleted all {table}")
        sys.exit(0)
    for seeder in TABLES.values():
        seeder.delete_all()
        print(f"Deleted all {seeder.__name__}")


def drop_all():
    client.drop_database("app")


def validate_table(table):
    if table not in TABLES:
        print(f"Table {table} not found")
        help()
        sys.exit(1)


def update(table):
    if table:
        TABLES[table].update()
        print(f"Updated {table}")
        sys.exit(0)
    else:
        for seeder in TABLES.values():
            seeder.update()
            print(f"Updated {seeder.__name__}")


def help():
    print("Usage: seed.py [option] [table]")
    print("Options:")
    print("\tseed\t\tSeed the database with default data")
    print("\tdelete\t\tDelete all data from the database")
    print("\tdrop\t\tDrop the database")
    print("\tupdate\t\tUpdate the database with default data")
    print("Tables:")
    for table in TABLES:
        print(f"\t{table}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        help()
    table = None
    if len(sys.argv) > 2:
        table = sys.argv[2]
        validate_table(table)
    if sys.argv[1] == "seed":
        seed(table)
    elif sys.argv[1] == "delete":
        delete_all(table)
    elif sys.argv[1] == "drop":
        drop_all()
    elif sys.argv[1] == "update":
        update(table)
