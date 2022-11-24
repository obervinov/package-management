import psycopg2
import time
from logger import log


class DB:

    def __init__(
        self, POSTGRES_DB: str = None,
        POSTGRES_USER: str = None,
        POSTGRES_PW: str = None,
        POSTGRES_URL: str = None,
        TIMEOUT_DB_INIT: int = 15
    ) -> None:

        self.dbname = POSTGRES_DB
        self.user = POSTGRES_USER
        self.password = POSTGRES_PW
        self.host = POSTGRES_URL
        self.timeout_db_init = TIMEOUT_DB_INIT
        # Waiting for database availability
        while True:
            try:
                log.info(
                    f"DB.__init__(): "
                    f"try connection to instance '{POSTGRES_URL}'"
                )
                psycopg2.connect(
                            dbname=self.dbname,
                            user=self.user,
                            password=self.password,
                            host=self.host
                )
            except psycopg2.OperationalError as ex:
                log.error(
                    f"DB.__init__(): "
                    f"connection to instance '{POSTGRES_URL}' faild: {ex}"
                )
                log.warning(
                    f"DB.__init__(): "
                    f"waitng timeout {self.timeout_db_init}s"
                )
                time.sleep(self.timeout_db_init)
                continue
            break

    # Function for selecting rows in a table
    def select_db_all(self, table_name: str = None):
        log.info(
            "DB.select_db_all(): "
            "creating connection"
        )
        conn = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host
        )
        cursor = conn.cursor()
        cursor.execute(
                f"SELECT * FROM public.{table_name} ORDER BY id"
        )
        log.info(
            f"DB.select_db_all(): "
            f"selecting data for public.{table_name}"
        )
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        return records

    # Function for creating rows in a table
    def insert_db(
            self,
            table_name: str = None,
            colum_name: str = None,
            values: str = None
    ):
        log.info(
            "DB.insert_db(): "
            "creating connection"
        )
        conn = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host
        )
        cursor = conn.cursor()
        cursor.execute(
                f"INSERT INTO public.{table_name} ({colum_name}) VALUES ({values})"
        )
        log.info(
            f"DB.insert_db(): "
            f"inserting data for public.{table_name}"
        )
        conn.commit()
        cursor.close()
        conn.close()

        return "insert_db - done"

    # Function for updating rows in a table
    def update_db(
            self,
            table_name: str = None,
            colum_name: str = None,
            values: str = None,
            filters: str = None
    ):
        log.info(
            "DB.update_db(): "
            "creating connection"
        )
        conn = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host
        )
        cursor = conn.cursor()
        cursor.execute(
                f"UPDATE public.{table_name} SET {colum_name} = '{values}' WHERE {filters}"
        )
        log.info(
            "DB.update_db(): "
            f"updating data for public.{table_name}"
        )
        conn.commit()
        cursor.close()
        conn.close()

        return "update_db - done"

    # Function for deleting rows in a table
    def delete_db(self, table_name: str = None, id_value: int = None):
        log.info(
            "DB.delete_db(): "
            "creating connection"
        )
        conn = psycopg2.connect(
                        dbname=self.dbname,
                        user=self.user,
                        password=self.password,
                        host=self.host
        )
        cursor = conn.cursor()
        cursor.execute(
                f"DELETE FROM public.{table_name} WHERE id = {id_value}"
        )
        log.info(
            "DB.delete_db(): "
            f"deleting data for public.{table_name}"
        )
        conn.commit()
        cursor.close()
        conn.close()

        return "delete_db - done"
