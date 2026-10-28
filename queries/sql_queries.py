import lib.config as cfg

START_DATE = cfg.START_DATE
END_DATE = cfg.END_DATE

sql_queries = {
    "std_customerstatus": "SELECT * FROM tms_customer_status",
    "std_branch": "SELECT id,description,code,display_name,zone_id FROM tms_branches;",
    "std_channel": "SELECT * FROM tms_channels;",
    "std_zone": "SELECT * FROM tms_zones;",
    "std_transactiontype": "SELECT * FROM tms_transaction_types;",
    "std_accounttype": "SELECT * FROM tms_account_types;",
    "std_ccy_isocodes": "SELECT * FROM tms_currency_codes;",
    "std_country_isocodes": "SELECT * FROM tms_country_iso_codes;",
    "std_language": "SELECT * FROM tms_language_types;",
    "std_accountstatus": "SELECT * FROM tms_account_status;",
    "std_customertype": "SELECT * FROM tms_customer_type;",
    "std_addresstype": "SELECT id,description,code,display_name,master,zone_id FROM tms_address_type;",
    "std_transactionstatus": "SELECT id,description,code,display_name,zone_id FROM tms_transaction_status;",

    "std_account": f""" SELECT DISTINCT tsa.sender_id, tsa.account_no, tsa.account_type, tsa.description,DATE_FORMAT(tsa.opening_date, '%Y%m%d') AS opening_date,DATE_FORMAT(tsa.closing_date, '%Y%m%d') AS closing_date, tsa.status, tsa.branch_id, tsa.channel_id, tsa.zone_id, tsa.monitored, tsa.risk_level_id, tsa.currency_code_id, tsa.account_subtype, tsa.iban FROM tms_sender_account tsa INNER JOIN remit_customer_info r ON (tsa.account_no = r.remitterNationalId OR tsa.account_no = r.beneficiaryAccountNo) 
    INNER JOIN remittances rem ON rem.remitReference = r.reference WHERE rem.state = 'remitted' AND rem.remitDate >= '{START_DATE}' AND rem.remitDate <= '{END_DATE}'""",


    "std_customer": f"""SELECT DISTINCT tc.id, tc.first_name, tc.middle_name, tc.title, tc.alternative_name,
            tc.customer_type_id, tc.customer_subtype_id, '' as active, tc.status_id, tc.branch_id,
            tc.monitored, tc.fatca, tc.risk_level_id, tc.registration, tc.residency, tc.language,
            tc.national, tc.zone_id, tc.photo
            FROM tms_customer tc
            INNER JOIN tms_sender_merchant_account sma ON sma.customer_id = tc.id
            INNER JOIN tms_sender_account tsa ON tsa.sender_id = sma.account_id
            INNER JOIN remit_customer_info r ON (tsa.account_no = r.remitterNationalId OR tsa.account_no = r.beneficiaryAccountNo)
            INNER JOIN remittances rem ON rem.remitReference = r.reference
            WHERE rem.state = 'remitted' AND rem.remitDate >= '{START_DATE}' AND rem.remitDate <= '{END_DATE}'""",
    "std_customer_physical": f"""SELECT DISTINCT tcp.id, tcp.gender, tcp.marital_status, tcp.number_of_children,
        tcp.fathers_name, tcp.mother_name, tcp.spouse_name,
        DATE_FORMAT(tcp.date_of_birth, '%Y%m%d') AS date_of_birth,
        LEFT(REPLACE(tcp.city_of_birth, '|', ','), 50) AS city_of_birth, tcp.country_of_birth,
        tcp.pep, tcp.vip, tcp.employee, tcp.identification_type, tcp.identification_number,
        tcp.identification_expiry, tcp.identification_issuer, tcp.nationality, tcp.other_nationality,
        tcp.sector, tcp.occupation, tcp.secondary_occupation, tcp.occupation_description,
        tcp.social_security, '' AS tax_id, tcp.zone_id
        FROM tms_customer_physical tcp
        INNER JOIN tms_sender_merchant_account sma ON sma.customer_id = tcp.id
        INNER JOIN tms_sender_account tsa ON tsa.sender_id = sma.account_id
        INNER JOIN remit_customer_info r ON (tsa.account_no = r.remitterNationalId OR tsa.account_no = r.beneficiaryAccountNo)
        INNER JOIN remittances rem ON rem.remitReference = r.reference
        WHERE rem.state = 'remitted' AND rem.remitDate >= '{START_DATE}' AND rem.remitDate <= '{END_DATE}'""",

    "std_customer_account": f"""SELECT DISTINCT sma.account_id, sma.customer_id, sma.id_connection,
            DATE_FORMAT(sma.start_date, '%Y%m%d'), DATE_FORMAT(sma.end_date, '%Y%m%d'), sma.zone_id
            FROM tms_sender_merchant_account sma
            INNER JOIN tms_sender_account tsa ON tsa.sender_id = sma.account_id
            INNER JOIN remit_customer_info r ON (tsa.account_no = r.remitterNationalId OR tsa.account_no = r.beneficiaryAccountNo)
            INNER JOIN remittances rem ON rem.remitReference = r.reference
            WHERE rem.state = 'remitted' AND rem.remitDate >= '{START_DATE}' AND rem.remitDate <= '{END_DATE}'""",
    # "std_customer": f"""SELECT id, first_name, middle_name, title, alternative_name, customer_type_id, customer_subtype_id, '' as active, status_id, branch_id, monitored, fatca, risk_level_id, registration, residency, language, national, zone_id, photo FROM tms_customer WHERE created_date >= '{START_DATE}' AND created_date <= '{END_DATE}' """,
    # "std_customer_physical": f""" SELECT id, gender, marital_status, number_of_children, fathers_name, mother_name, spouse_name, DATE_FORMAT(date_of_birth, '%Y%m%d') AS date_of_birth, LEFT(REPLACE(city_of_birth, '|', ','), 50) AS city_of_birth,country_of_birth, pep, vip, employee, identification_type, identification_number, identification_expiry, identification_issuer, nationality, other_nationality, sector, occupation, secondary_occupation, occupation_description, social_security, '' AS tax_id, zone_id FROM tms_customer_physical WHERE created_date >= '{START_DATE}' AND created_date <= '{END_DATE}' """,
    # "std_account": f""" SELECT sender_id, account_no, account_type, description, DATE_FORMAT(opening_date, '%Y%m%d') AS opening_date, DATE_FORMAT(closing_date, '%Y%m%d') AS closing_date, status, branch_id, channel_id, zone_id, monitored, risk_level_id, currency_code_id, account_subtype, iban FROM tms_sender_account WHERE created_date >= '{START_DATE}' AND created_date <= '{END_DATE}' """,
    # "std_customer_account": f""" SELECT account_id, customer_id, id_connection, DATE_FORMAT(start_date, '%Y%m%d'), DATE_FORMAT(end_date, '%Y%m%d'), zone_id FROM tms_sender_merchant_account WHERE start_date >= '{START_DATE}' AND start_date <= '{END_DATE}' """,
    "std_connectiontype": "SELECT * FROM tms_connection_types;",
    "std_transaction": f"""WITH CombinedData AS (
        SELECT 
        DATE_FORMAT(remmit.remitDate, '%Y%m%d') AS remitDate, 
        DATE_FORMAT(remmit.remitDate, '%H%i%s') AS remitTime, 
        tsa.sender_id, 
        (SELECT sender_id FROM tms_sender_account WHERE account_no = remmit_info.beneficiaryAccountNo) AS beneficiaryAccountNo, 
        (SELECT id FROM tms_transaction_types WHERE id = 1) AS transaction_type_id, 
        (SELECT id FROM tms_channels ORDER BY id DESC LIMIT 1) AS channel_id, 
        ROUND(remmit.remitAmount / ((SELECT exchange FROM tms_exchange_rate WHERE from_currency = 'CAD' AND to_currency = 'PKR' ORDER BY id DESC LIMIT 1))) AS remit_amount, 
        remmit.remitAmount AS original_amount, 
        (SELECT currency_code FROM tms_currency_codes WHERE currency_code = 'CAD' LIMIT 1) AS currency_code, 
        'D' AS entry_type, 
        '' AS source, 
        concat(remmit.remittanceId,'_1') as remittanceId, 
        '' AS source_addiotional, 
        'DW' AS description, 
        'CA' AS from_country, 
        'PK' AS to_country, 
        (SELECT id FROM tms_zones WHERE id = 1) AS zone_id, 
        (SELECT id FROM tms_transaction_status WHERE code = 'SUCCESS') AS success, 
        ROW_NUMBER() OVER (ORDER BY remmit.remitDate) AS row_num 
        FROM remittances AS remmit 
        JOIN remit_customer_info AS remmit_info ON remmit_info.reference = remmit.remitReference 
        JOIN tms_sender_account AS tsa ON tsa.account_no = remmit_info.remitterNationalId 
        WHERE remmit.state = 'remitted' AND remmit.remitDate >= '{START_DATE}' AND remmit.remitDate <= '{END_DATE}' 
        UNION ALL 
        SELECT 
        DATE_FORMAT(remmit.remitDate, '%Y%m%d') AS remitDate, 
        DATE_FORMAT(remmit.remitDate, '%H%i%s') AS remitTime, 
        (SELECT sender_id FROM tms_sender_account WHERE account_no = remmit_info.beneficiaryAccountNo) AS beneficiaryAccountNo, 
        tsa.sender_id, 
        (SELECT id FROM tms_transaction_types WHERE id = 2) AS transaction_type_id, 
        (SELECT id FROM tms_channels ORDER BY id DESC LIMIT 1) AS channel_id, 
        ROUND(remmit.remitAmount / ((SELECT exchange FROM tms_exchange_rate WHERE from_currency = 'CAD' AND to_currency = 'PKR' ORDER BY id DESC LIMIT 1))) AS remit_amount, 
        remmit.remitAmount AS original_amount, 
        (SELECT currency_code FROM tms_currency_codes WHERE currency_code = 'CAD' LIMIT 1) AS currency_code, 
        'C' AS entry_type, 
        '' AS source, 
        concat(remmit.remittanceId,'_2') as remittanceId, 
        '' AS source_addiotional, 
        'DW' AS description, 
        'PK' AS from_country, 
        'CA' AS to_country, 
        (SELECT id FROM tms_zones WHERE id = 1) AS zone_id, 
        (SELECT id FROM tms_transaction_status WHERE code = 'SUCCESS') AS success, 
        ROW_NUMBER() OVER (ORDER BY remmit.remitDate) AS row_num 
        FROM remittances AS remmit 
        JOIN remit_customer_info AS remmit_info ON remmit_info.reference = remmit.remitReference 
        JOIN tms_sender_account AS tsa ON tsa.account_no = remmit_info.remitterNationalId 
        WHERE remmit.state = 'remitted' AND remmit.remitDate >= '{START_DATE}' AND remmit.remitDate <= '{END_DATE}' 
        ) 
        SELECT remitDate, remitTime, sender_id, beneficiaryAccountNo, transaction_type_id, channel_id, remit_amount, 
        original_amount, currency_code, entry_type, source, remittanceId, source_addiotional, 
        description, from_country, to_country, zone_id, success 
        FROM CombinedData ORDER BY row_num, entry_type;""",
}

