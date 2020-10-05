import logging
import cfnresponse
import psycopg2
import boto3
import sys
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


client = boto3.client("logs")


def run_sql_commands(db_host, db_name, db_user, db_password):
    # Connect to the database

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logging.info("db_host reported: %s", db_host)
    logging.info("db_name reported: %s", db_name)
    logging.info("db_user reported: %s", db_user)
    logging.info("db_password reported: %s", db_password)

    #try:
    conn_string = "host=%s user=%s password=%s dbname=%s" % \
        (db_host, db_user, db_password, db_name)
    conn = psycopg2.connect(conn_string)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    logger.info("SUCCESS: conn to RDS Postgres instance succeeded")
    #except:
    #    logger.error("ERROR: Could not connect to Postgres instance.")

    with conn.cursor() as cursor:
        sql = "DROP DATABASE IF EXISTS powertext_pegasus;"
        cursor.execute(sql)
    conn.commit()

    with conn.cursor() as cursor:
        # Create a new record
        sql = "CREATE DATABASE powertext_pegasus;"
        cursor.execute(sql)
        # conn is not autocommit by default. So you must commit to save
        # your changes.
    conn.commit()

    with conn.cursor() as cursor:
        sql = "GRANT ALL PRIVILEGES ON DATABASE powertext_pegasus TO postgres;"
        cursor.execute(sql)
    conn.commit()

    conn.close()

    return


def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    host = event['ResourceProperties']['PostgresDbHost']
    name = event['ResourceProperties']['PostgresDbName']
    username = event['ResourceProperties']['PostgresDbUsername']
    password = event['ResourceProperties']['PostgresDbPassword']
    response_data = {}
    try:

        if event['RequestType'] == 'Delete':
            logger.info('Deleted!')
            response_data['Data'] = "SUCCESS"
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            return

        if event['RequestType'] == 'Create':
            run_sql_commands(host, name, username, password)
            logger.info('It worked!')
            response_data['Data'] = "SUCCESS"
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            return

    except Exception:
        logger.exception('Signaling failure to CloudFormation.')
        response_data['Data'] = "FAILED"
        cfnresponse.send(event, context, cfnresponse.FAILED, {})
