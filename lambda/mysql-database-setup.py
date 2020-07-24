import logging
import cfnresponse
import pymysql
import pymysql.cursors
import boto3

client = boto3.client("logs")


def run_sql_commands(db_host, db_name, db_user, db_password):
    # Connect to the database
    connection = pymysql.connect(host=db_host,
                                 user=db_user,
                                 password=db_password,
                                 db=db_name,
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "CREATE DATABASE wordpress DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
            cursor.execute(sql)
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

        with connection.cursor() as cursor:
            sql = "CREATE USER 'aaron'@'localhost' IDENTIFIED BY 'aaronrules';"
            cursor.execute(sql)
        connection.commit()

        with connection.cursor() as cursor:
            sql = "GRANT ALL ON wordpress.* TO 'aaron'@'localhost';"
            cursor.execute(sql)
        connection.commit()

    finally:
        connection.close()
    return


def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    host = event['ResourceProperties']['MySQLDbHost']
    name = event['ResourceProperties']['MySQLDbName']
    username = event['ResourceProperties']['MySQLDbUsername']
    password = event['ResourceProperties']['MySQLDbPassword']
    run_sql_commands(host, name, username, password)
    try:

        if event['RequestType'] == 'Delete':
            logger.info('Deleted!')
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
            return

        logger.info('It worked!')
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})

    except Exception:
        logger.exception('Signaling failure to CloudFormation.')
        cfnresponse.send(event, context, cfnresponse.FAILED, {})
