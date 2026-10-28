import os
import time


import lib.banks as banks
import lib.config as cfg
import mysql.connector
import logging, datetime
from queries import sql_queries

x = datetime.datetime.now()
GLOGGER = logging.getLogger('GENERAL')
# GLOG_FILENAME = cfg.BASEPATH+'logs/general-'+x.strftime("%Y%m%d")+'.log'
GLOG_FILENAME = cfg.BASEPATH + '/logs/general.log'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=GLOG_FILENAME,
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
# schema = cfg.pgSchema
import paramiko

START_DATE = cfg.START_DATE
END_DATE = cfg.END_DATE

print("Running...")
GLOGGER.info("Running...")


def tms_exchange_rate():
    try:

        GLOGGER.info(f'running tms_exchange_rate method')
        mydb = get_mysqldb_by_operator("remittance")
        conn = mydb.cursor()
        sql_query = """
        INSERT INTO tms_exchange_rate (from_currency, to_currency, exchange, from_date, to_date, zone_id)
        SELECT 
            fromCurrency, 
            toCurrency, 
            rate, 
            DATE(NOW()), 
            DATE(NOW()) + INTERVAL 1 DAY, 
            1 
        FROM fx_rate
        WHERE 
            fromCurrency = 'CAD' 
            AND toCurrency = 'PKR' 
            AND active = 1
            AND NOT EXISTS (
                SELECT 1 FROM tms_exchange_rate 
                WHERE 
                    from_currency = fx_rate.fromCurrency 
                    AND to_currency = fx_rate.toCurrency 
                    AND from_date = DATE(NOW())
                    AND to_date = DATE(NOW()) + INTERVAL 1 DAY
            )
        ORDER BY id DESC 
        LIMIT 1;
        """

        conn.execute(sql_query)
        mydb.commit()


    except Exception as e:
        print(f"Error occurred tms_customer: {str(e)}")
        logging.error(f"Error occurred tms_customer: {str(e)}")
        return False


def tms_sender_account():
    global merchant_id
    try:
        print("running tms_sender_account")
        GLOGGER.info('running tms_sender_account')

        mydb = get_mysqldb_by_operator("remittance")
        conn = mydb.cursor()

        # Step 1: Insert remitter records
        remitter_insert_sql = """
            INSERT IGNORE INTO tms_sender_account (
                account_no, title, account_type, created_date, opening_date, 
                status, branch_id, zone_id, channel_id, currency_code_id, id_connection
            )
            SELECT 
                r.remitterNationalId, r.remitterName, 2, r.createdDate, r.createdDate,
                (SELECT id FROM tms_account_status LIMIT 1),
                1,
                (SELECT id FROM tms_zones WHERE id = 1),
                (SELECT id FROM tms_channels ORDER BY id DESC LIMIT 1),
                (SELECT currency_code FROM tms_currency_codes WHERE currency_code = 'CAD' LIMIT 1),
                1
            FROM remit_customer_info r
            WHERE r.createdDate BETWEEN %s AND %s
        """
        conn.execute(remitter_insert_sql, (START_DATE, END_DATE))

        # Step 2: Insert beneficiary records in one query
        beneficiary_insert_sql = """
            INSERT IGNORE INTO tms_sender_account (
                account_no, title, account_type, created_date, opening_date,
                status, branch_id, zone_id, channel_id, currency_code_id, customer_id, id_connection
            )
            SELECT DISTINCT
                r.beneficiaryAccountNo,
                r.beneficiaryName,
                2,
                r.createdDate,
                r.createdDate,
                (SELECT id FROM tms_account_status LIMIT 1),
                1,
                (SELECT id FROM tms_zones WHERE id = 1),
                (SELECT id FROM tms_channels ORDER BY id DESC LIMIT 1),
                (SELECT currency_code FROM tms_currency_codes WHERE currency_code = 'CAD' LIMIT 1),
                s.sender_id,
                5
            FROM remit_customer_info r
            INNER JOIN tms_sender_account s ON s.account_no = r.remitterNationalId
            WHERE s.id_connection = 1 
              AND  r.createdDate, BETWEEN %s AND %s
        """
        conn.execute(beneficiary_insert_sql, (START_DATE, END_DATE))

        mydb.commit()
        print(f"✅ Inserted remitter and beneficiary accounts.")
        GLOGGER.info('Inserted remitter and beneficiary accounts.')

    except mysql.connector.Error as e:
        logging.error(f"Error tms_sender_account: {str(e)}")
        return False


def tms_sender_merchant_account():
    try:
        print("running tms_sender_merchant_account")
        GLOGGER.info('running tms_sender_merchant_account')

        mydb = get_mysqldb_by_operator("remittance")
        conn = mydb.cursor()

        # Insert all records in one query instead of looping
        insert_query = """
            INSERT IGNORE INTO tms_sender_merchant_account (
                account_id, customer_id, type_id, start_date, zone_id, id_connection
            )
            SELECT 
                sender_id, sender_id, 1, created_date, zone_id, id_connection
            FROM tms_sender_account 
            WHERE created_date BETWEEN %s AND %s
        """

        conn.execute(insert_query, (START_DATE, END_DATE))
        rows_inserted = conn.rowcount

        mydb.commit()
        print(f"✅ Inserted {rows_inserted} records into tms_sender_merchant_account")
        GLOGGER.info(f'Inserted {rows_inserted} records into tms_sender_merchant_account')

    except mysql.connector.Error as e:
        logging.error(f"Error tms_sender_merchant_account: {str(e)}")
        print(f"Error tms_sender_merchant_account: {str(e)}")


def tms_customer():
    try:
        print("running tms_customer method")
        GLOGGER.info('running tms_customer method')
        mydb = get_mysqldb_by_operator("remittance")
        conn = mydb.cursor()

        # Step 1: Insert customers in one query
        insert_sql = """
            INSERT IGNORE INTO tms_customer (
                id, beneficiary_name, title, customer_type_id, status_id, 
                branch_id, zone_id, id_connection, created_date
            )
            SELECT
                tsa.sender_id,
                tsa.account_no,
                tsa.title,
                (SELECT id FROM tms_customer_type WHERE code = 'ID2'),
                1,
                1,
                (SELECT id FROM tms_zones WHERE id = 1),
                tsa.id_connection,
                tsa.created_date
            FROM tms_sender_account tsa
            WHERE tsa.created_date BETWEEN %s AND %s
        """
        conn.execute(insert_sql, (START_DATE, END_DATE))

        # Step 2: Update alternative_name for remitters (id_connection = 1)
        update_remitter_sql = """
            UPDATE tms_customer tc
            INNER JOIN tms_sender_account tsa ON tc.id = tsa.sender_id
            INNER JOIN remit_customer_info rci ON rci.remitterNationalId = tsa.account_no
            SET tc.alternative_name = rci.merchantId
            WHERE tsa.id_connection = 1 
              AND tsa.created_date BETWEEN %s AND %s
        """
        conn.execute(update_remitter_sql, (START_DATE, END_DATE))
        remitter_updates = conn.rowcount

        # Step 3: Update alternative_name for beneficiaries (id_connection = 5)
        update_beneficiary_sql = """
            UPDATE tms_customer tc
            INNER JOIN tms_sender_account tsa ON tc.id = tsa.sender_id
            INNER JOIN remit_customer_info rci ON rci.beneficiaryAccountNo = tsa.account_no
            SET tc.alternative_name = rci.merchantId
            WHERE tsa.id_connection = 5 
              AND tsa.created_date BETWEEN %s AND %s
        """
        conn.execute(update_beneficiary_sql, (START_DATE, END_DATE))
        beneficiary_updates = conn.rowcount

        mydb.commit()
        print(f"✅ Updated {remitter_updates} remitters and {beneficiary_updates} beneficiaries with merchant IDs")
        GLOGGER.info(f'Updated {remitter_updates} remitters and {beneficiary_updates} beneficiaries with merchant IDs')

    except Exception as e:
        print(f"Error occurred tms_customer: {str(e)}")
        logging.error(f"Error occurred tms_customer: {str(e)}")
        return False


def tms_customer_physical():
    try:
        print("Inserting data into tms_customer_physical")
        GLOGGER.info('Inserting data into tms_customer_physical')
        mydb = get_mysqldb_by_operator("remittance")
        conn = mydb.cursor()

        # Insert for remitters (id_connection = 1) - one query handles all nationality logic
        insert_remitters_sql = """
            INSERT IGNORE INTO tms_customer_physical (
                id, nationality, city_of_birth, country_of_birth, zone_id, created_date
            )
            SELECT 
                tsa.sender_id,
                CASE 
                    WHEN LENGTH(rci.remitterNationality) = 2 THEN rci.remitterNationality
                    WHEN LENGTH(rci.remitterNationality) = 3 THEN 
                        COALESCE((SELECT country_code FROM tms_country_iso_codes WHERE code_alpha_3 = rci.remitterNationality LIMIT 1), 'N/A')
                    WHEN LENGTH(rci.remitterNationality) > 3 THEN 
                        COALESCE((SELECT country_code FROM tms_country_iso_codes WHERE display_name = rci.remitterNationality LIMIT 1), 'US')
                    ELSE 'N/A'
                END as nationality,
                rci.remitterCity,
               CASE 
                    WHEN LENGTH(rci.remitterNationality) = 2 THEN rci.remitterNationality
                    WHEN LENGTH(rci.remitterNationality) = 3 THEN 
                        COALESCE((SELECT country_code 
                                  FROM tms_country_iso_codes 
                                  WHERE code_alpha_3 = rci.remitterNationality 
                                  LIMIT 1), 'N/A')
                    WHEN LENGTH(rci.remitterNationality) > 3 THEN 
                        COALESCE((SELECT country_code 
                                  FROM tms_country_iso_codes 
                                  WHERE display_name = rci.remitterNationality 
                                  LIMIT 1), 'US')
                    ELSE 'N/A'
                END AS country_of_birth,
                (SELECT id FROM tms_zones WHERE id = 1),
                tsa.created_date
            FROM tms_sender_account tsa
            INNER JOIN remit_customer_info rci ON rci.remitterNationalId = tsa.account_no
            WHERE tsa.id_connection = 1 
              AND tsa.created_date BETWEEN %s AND %s
        """
        conn.execute(insert_remitters_sql, (START_DATE, END_DATE))
        remitter_inserts = conn.rowcount

        # Insert for beneficiaries (id_connection = 5) - one query handles all nationality logic
        insert_beneficiaries_sql = """
            INSERT IGNORE INTO tms_customer_physical (
                id, nationality, city_of_birth, country_of_birth, zone_id, created_date
            )
            SELECT 
                tsa.sender_id,
                CASE 
                    WHEN LENGTH(rci.beneficiaryNationality) = 2 THEN rci.beneficiaryNationality
                    WHEN LENGTH(rci.beneficiaryNationality) = 3 THEN 
                        COALESCE((SELECT country_code FROM tms_country_iso_codes WHERE code_alpha_3 = rci.beneficiaryNationality LIMIT 1), 'N/A')
                    WHEN LENGTH(rci.beneficiaryNationality) > 3 THEN 
                        COALESCE((SELECT country_code FROM tms_country_iso_codes WHERE display_name = rci.beneficiaryNationality LIMIT 1), 'US')
                    ELSE 'N/A'
                END as nationality,
                rci.beneficiaryAddress,
                CASE 
                    WHEN LENGTH(rci.beneficiaryNationality) = 2 THEN rci.beneficiaryNationality
                    WHEN LENGTH(rci.beneficiaryNationality) = 3 THEN 
                        COALESCE((SELECT country_code 
                                  FROM tms_country_iso_codes 
                                  WHERE code_alpha_3 = rci.beneficiaryNationality 
                                  LIMIT 1), 'N/A')
                    WHEN LENGTH(rci.beneficiaryNationality) > 3 THEN 
                        COALESCE((SELECT country_code 
                                  FROM tms_country_iso_codes 
                                  WHERE display_name = rci.beneficiaryNationality 
                                  LIMIT 1), 'US')
                    ELSE 'N/A'
                END AS country_of_birth,
                (SELECT id FROM tms_zones WHERE id = 1),
                tsa.created_date
            FROM tms_sender_account tsa
            INNER JOIN remit_customer_info rci ON rci.beneficiaryAccountNo = tsa.account_no
            WHERE tsa.id_connection = 5 
              AND tsa.created_date BETWEEN %s AND %s
        """
        conn.execute(insert_beneficiaries_sql, (START_DATE, END_DATE))
        beneficiary_inserts = conn.rowcount

        mydb.commit()
        print(f"✅ Inserted {remitter_inserts} remitter and {beneficiary_inserts} beneficiary physical records")
        GLOGGER.info(f'Inserted {remitter_inserts} remitter and {beneficiary_inserts} beneficiary physical records')

    except Exception as e:
        logging.error(f"Error occurred tms_customer_physical: {str(e)}")
        print(f"Error occurred tms_customer_physical: {str(e)}")
        return False

def generate_txt():
    try:
        mydb = get_mysqldb_by_operator("remittance")
        conn = mydb.cursor()
        queries = sql_queries.sql_queries
        banks_list = banks.banks

        tms_exchange_rate()
        tms_sender_account()
        tms_sender_merchant_account()
        tms_customer()
        tms_customer_physical()

        for key, query in queries.items():

            if key == "std_transaction":
                banks_str = ', '.join(f"'{bank}'" for bank in banks_list)
                query = query.replace("'DW'", f"CASE WHEN remmit.bankName IN ({banks_str}) THEN 'DW' ELSE 'BA' END")

            try:
                conn.execute(query)
                results = conn.fetchall()

                if results:
                    txt_file, full_pathfile = get_file_name(key, 'txt')

                    with open(full_pathfile, 'w', newline='', encoding='utf-16') as file:
                        for row in results:
                            file.write('|'.join('' if val is None else str(val) for val in row) + '\r\n')

                    print('Generating ' + key + '.txt ......done')
                    GLOGGER.info('Generating ' + key + '.txt ......done')
                    save_generate_and_upload_file(txt_file, key)
                else:
                    print(f'No results found for key: {key}. Skipping file generation.')
                    GLOGGER.warning(f'No results found for key: {key}. Skipping file generation.')

            except Exception as e:
                print(f"Error executing '{key}': {e}")
                GLOGGER.error(f"Error executing '{key}': {e}")
                # ✅ After loop — append missing to all affected txt files and re-upload



    except Exception as e:
        logging.error(f"Error generating CSV: {str(e)}")
        return False

# def generate_txt():
#     try:
#         mydb = get_mysqldb_by_operator("remittance")
#         conn = mydb.cursor()
#         queries = sql_queries.sql_queries
#         banks_list = banks.banks
#         tms_exchange_rate()
#         tms_sender_account()
#         tms_sender_merchant_account()
#         tms_customer()
#         tms_customer_physical()
#
#         for key, query in queries.items():
#
#             if key == "std_transactions":
#                 banks_str = ', '.join(f"'{bank}'" for bank in banks_list)
#                 query = query.replace("'DW'", f"CASE WHEN remmit.bankName IN ({banks_str}) THEN 'DW' ELSE 'BA' END")
#
#             try:
#                 conn.execute(query)
#                 results = conn.fetchall()
#
#                 if results:
#                     txt_file, full_pathfile = get_file_name(key, 'txt')
#
#                     with open(full_pathfile, 'w', newline='', encoding='utf-16') as file:
#                         for row in results:
#                             file.write('|'.join('' if val is None else str(val) for val in row) + '\r\n')
#
#                     print('Generating ' + key + '.txt ......done')
#                     GLOGGER.info('Generating ' + key + '.txt ......done')
#                     save_generate_and_upload_file(txt_file, key)
#                 else:
#                     print(f'No results found for key: {key}. Skipping file generation.')
#                     GLOGGER.warning(f'No results found for key: {key}. Skipping file generation.')
#
#             except Exception as e:
#                 print(f"Error executing '{key}': {e}")
#
#     except Exception as e:
#         logging.error(f"Error generating CSV: {str(e)}")
#         return False


def save_generate_and_upload_file(file_name, file_):
    from datetime import datetime
    sftp_username = cfg.sftpUsername
    sftp_password = cfg.sftpPass
    sftp_host = cfg.sftpHost
    sftp_port = int(cfg.sftpPort)

    try:
        transport = paramiko.Transport((sftp_host, sftp_port))
        transport.connect(username=sftp_username, password=sftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        remoteDir = '/'
        try:
            sftp.chdir(remoteDir)
            file_path = str(file_name)
            file_name_with_extension = os.path.basename(file_path)
            local_file = file_name
            remote_file = '/' + str(file_name_with_extension)
            sftp.put(local_file, remote_file)
            sftp.close()
            transport.close()
            print(file_ + ".txt uploading to sftp......done")
            GLOGGER.info(file_ + ".txt uploading to sftp......done")
        except IOError as e:
            print(f"Error sftp: {e}")

    except Exception as e:
        print(f"Error: {e}")


def get_mysqldb_by_operator(dbType):
    # GLOGGER.info('get_mysqldb_by_operator trigger %s %s',dbType)
    if dbType == "remittance":

        try:
            mydb = mysql.connector.connect(
                host=cfg.MYSQLREMIT.get("HOST"),
                user=cfg.MYSQLREMIT.get("USERNAME"),
                password=cfg.MYSQLREMIT.get("PASSWORD"),
                database=cfg.MYSQLREMIT.get("DB"),
                charset='utf8',
                use_unicode=True,
                autocommit=True
            )
            # mydb = mysql.connector.connect(
            #     host="localhost",  # Use "127.0.0.1" if "localhost" doesn't work
            #     user="root",  # Change to your MySQL username
            #     password="",  # Change to your MySQL password
            #     database="tms",  # Change to your MySQL database name
            #     charset="utf8",
            #     use_unicode=True,
            #     autocommit=True
            # )
            if not mydb.is_connected():
                print("DB error")
            else:
                return mydb
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
    else:
        # GLOGGER.info('get_mysqldb_by_operator Condition failed')
        return 'ERROR'


def get_file_name(query_key, file_type):
    if (query_key == 'std_connection_type'):
        query_key = 'std_connectiontype'
    file_name = f'reports/{query_key}.{file_type}'.lower()
    full_pathfile = os.path.join(cfg.BASEPATH, file_name)

    return file_name, full_pathfile


if __name__ == "__main__":
    generate_txt()