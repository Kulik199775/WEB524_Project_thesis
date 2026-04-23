from django.core.management import BaseCommand
import pyodbc
from config.settings import USER, PASSWORD, HOST, DRIVER, PAD_DATABASE, DATABASE


class Command(BaseCommand):

    def handle(self, *args, **options):
        ConnectionString = (
            f"DRIVER={DRIVER};"
            f"SERVER={HOST};"
            f"DATABASE={PAD_DATABASE};"
            f"UID={USER};"
            f"PWD={PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;")

        try:
            conn = pyodbc.connect(ConnectionString)
        except pyodbc.Error as err:
            print(err)
        else:
            conn.autocommit = True
            try:
                conn.execute(fr'CREATE DATABASE {DATABASE};')
                print(f'База данных {DATABASE} успешно создана')
            except pyodbc.Error as err:
                print(err)
