import boto3 as boto3
import os,datetime
from datetime import datetime, timedelta
session = boto3.Session()
# ssmClient = session.client('ssm')
ssmClient = session.client('ssm',region_name='ap-southeast-1')
# # Get the value of a specific environment variable
#environment = os.environ.get('GLOBAL_ENV')
environment = "/dev"
#print("Environment:",environment)
storeParameterPath = environment+'/tms/'
storeParameterPath2 = environment+'/bulk-reporting/'

#For Local log Path
BASEPATH = os.getcwd()+'/'
#BASEPATH='/usr/local/Simpaisa-work/compliance-tms/'
#
# yesterday = datetime.now() - timedelta(days=1)
# START_DATE = yesterday.strftime('%Y-%m-%d 00:00:00')
# END_DATE = yesterday.strftime('%Y-%m-%d 23:59:59')
START_DATE = '2020-06-01 00:00:00'
END_DATE = '2026-01-30 23:59:59'

#MYSQL REMIT CREDENTIALS PARAMS
remitHost = ssmClient.get_parameter(Name=storeParameterPath+'remit-db-host', WithDecryption=True)['Parameter']['Value']
remitPassword = ssmClient.get_parameter(Name=storeParameterPath+'remit-db-pass', WithDecryption=True)['Parameter']['Value']
remitUsername = ssmClient.get_parameter(Name=storeParameterPath+'remit-db-username', WithDecryption=True)['Parameter']['Value']
remitDB = ssmClient.get_parameter(Name=storeParameterPath+'remit-db-name', WithDecryption=True)['Parameter']['Value']

sftpHost= ssmClient.get_parameter(Name=storeParameterPath+'sftp-host', WithDecryption=True)['Parameter']['Value']
sftpUsername= ssmClient.get_parameter(Name=storeParameterPath+'sftp-user', WithDecryption=True)['Parameter']['Value']
sftpPass= ssmClient.get_parameter(Name=storeParameterPath+'sftp-pass', WithDecryption=True)['Parameter']['Value']
sftpPort= ssmClient.get_parameter(Name=storeParameterPath+'sftp-port', WithDecryption=True)['Parameter']['Value']
sftpDir= ssmClient.get_parameter(Name=storeParameterPath+'sftp-directory', WithDecryption=True)['Parameter']['Value']

#MYSQL REMIT CREDENTIALS
MYSQLREMIT = {
    "HOST":remitHost,
    "USERNAME":remitUsername,
    "PASSWORD":remitPassword,
    "DB":remitDB
}

REMITTANCE_DIR = ssmClient.get_parameter(Name=storeParameterPath+'sftp-directory', WithDecryption=True)['Parameter']['Value']
