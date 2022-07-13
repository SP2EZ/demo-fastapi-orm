# This Script creates a session with the Database so that SQL commands can be executed
# Library Used : psycopg3
# pip install psycopg[binary]
# Psycopg3 (successor of psycopg2) is a newly designed PostgreSQL database adapter for the Python programming language

import psycopg
from psycopg import rows
import time
from . import config

""" Comment below for Using Testing DB """ 

try:
    # Connect to an existing database
    conn = psycopg.connect(host=config.settings.DATABASE_HOSTNAME, dbname=config.settings.DB_NAME, user=config.settings.DB_USERNAME, password=config.settings.DB_PASSWORD, port=config.settings.DB_PORT, row_factory=rows.dict_row)
    cursor = conn.cursor()
    print("Live Database Connected !!!")
except Exception as error:
    print("Live Database Connection Failed, Error Encountered :")
    print(error)
    time.sleep(15) # This will attempt to reconnect to database every 15 sec if any Connection Issue arises
    #conn.rollback()
#else:
#    conn.commit()
#finally:
#    conn.close()


""" Comment below for Using Live DB """
"""
try:
    # Connect to an existing database
    conn = psycopg.connect(host=config.settings.DATABASE_HOSTNAME, dbname=config.settings.DB_NAME_TEST, user=config.settings.DB_USERNAME, password=config.settings.DB_PASSWORD, port=config.settings.DB_PORT, row_factory=rows.dict_row)
    cursor = conn.cursor()
    print("Test Database Connected !!!")
except Exception as error:
    print("Test Database Connection Failed, Error Encountered :")
    print(error)
    time.sleep(15)

"""