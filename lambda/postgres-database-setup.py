import logging
import cfnresponse
import psycopg2
import boto3

client = boto3.client("logs")


def run_sql_commands(db_host, db_name, db_user, db_password):
    # Connect to the database

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    try:
        conn_string = "host=%s user=%s password=%s dbname=%s" % \
            (db_host, db_user, db_password, db_name)
        conn = psycopg2.connect(conn_string)

        logger.info("SUCCESS: conn to RDS Postgres instance succeeded")

    except:
        logger.error("ERROR: Could not connect to Postgres instance.")

    with conn.cursor() as cursor:
        sql = "DROP DATABASE IF EXISTS powertext_pegasus"
        cursor.execute(sql)
    conn.commit()

    with conn.cursor() as cursor:
        # Create a new record
        sql = "CREATE DATABASE powertext_pegasus DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
        cursor.execute(sql)
        # conn is not autocommit by default. So you must commit to save
        # your changes.
    conn.commit()

    with conn.cursor() as cursor:
        sql = "DROP USER IF EXISTS 'postgres'@'localhost';"
        cursor.execute(sql)
    conn.commit()

    with conn.cursor() as cursor:
        sql = "CREATE USER 'postgres'@'localhost' IDENTIFIED BY 'postgres';"
        cursor.execute(sql)
    conn.commit()

    with conn.cursor() as cursor:
        sql = "GRANT ALL ON powertext_pegasus.* TO 'postgres'@'localhost';"
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
            logger.info('It worked!')
            run_sql_commands(host, name, username, password)
            response_data['Data'] = "SUCCESS"
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            return

    except Exception:
        logger.exception('Signaling failure to CloudFormation.')
        response_data['Data'] = "FAILED"
        cfnresponse.send(event, context, cfnresponse.FAILED, {})
