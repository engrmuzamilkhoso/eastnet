import boto3 as boto3
import os,datetime



#BASEPATH='/usr/localsimpaisa//backend/bulk-reporting/'
#For Local log Path
BASEPATH = os.getcwd()+'/'

session = boto3.Session()
ssmClient = session.client('ssm')

# Get the value of a specific environment variable
environment = os.environ.get('GLOBAL_ENV')

print("Environment:",environment)
storeParameterPath = environment+'/portal/backend/'

#POSTGRES CREDENTIALS PARAMS
pgHost = ssmClient.get_parameter(Name=storeParameterPath+'pg_host', WithDecryption=True)['Parameter']['Value']
pgPassword = ssmClient.get_parameter(Name=storeParameterPath+'pg_password', WithDecryption=True)['Parameter']['Value']
pgUsername = ssmClient.get_parameter(Name=storeParameterPath+'pg_username', WithDecryption=True)['Parameter']['Value']
pgPort = ssmClient.get_parameter(Name=storeParameterPath+'pg_port', WithDecryption=True)['Parameter']['Value']
mongodbUri = ssmClient.get_parameter(Name=storeParameterPath+'mongodb_uri', WithDecryption=True)['Parameter']['Value']
pgDB = ssmClient.get_parameter(Name=storeParameterPath+'pg_database', WithDecryption=True)['Parameter']['Value']
pgSchema = ssmClient.get_parameter(Name=storeParameterPath+'pg_schema', WithDecryption=True)['Parameter']['Value']


#MYSQL DCB CREDENTIALS PARAMS
dcbHost = ssmClient.get_parameter(Name=storeParameterPath+'dcb_host', WithDecryption=True)['Parameter']['Value']
dcbPassword = ssmClient.get_parameter(Name=storeParameterPath+'spring.datasource.dcb.password', WithDecryption=True)['Parameter']['Value']
dcbUsername = ssmClient.get_parameter(Name=storeParameterPath+'spring.datasource.dcb.username', WithDecryption=True)['Parameter']['Value']
dcbDB = ssmClient.get_parameter(Name=storeParameterPath+'dcb_db', WithDecryption=True)['Parameter']['Value']

#MYSQL WALLET CREDENTIALS PARAMS
walletHost = ssmClient.get_parameter(Name=storeParameterPath+'wallet_host', WithDecryption=True)['Parameter']['Value']
walletPassword = ssmClient.get_parameter(Name=storeParameterPath+'spring.datasource.wallet.password', WithDecryption=True)['Parameter']['Value']
walletUsername = ssmClient.get_parameter(Name=storeParameterPath+'spring.datasource.wallet.username', WithDecryption=True)['Parameter']['Value']
walletDB = ssmClient.get_parameter(Name=storeParameterPath+'wallet_db', WithDecryption=True)['Parameter']['Value']

#MYSQL DISB CREDENTIALS PARAMS
disbHost = ssmClient.get_parameter(Name=storeParameterPath+'disb_host', WithDecryption=True)['Parameter']['Value']
disbPassword = ssmClient.get_parameter(Name=storeParameterPath+'spring.datasource.disp.password', WithDecryption=True)['Parameter']['Value']
disbUsername = ssmClient.get_parameter(Name=storeParameterPath+'spring.datasource.disp.username', WithDecryption=True)['Parameter']['Value']
disbDB = ssmClient.get_parameter(Name=storeParameterPath+'disp_db', WithDecryption=True)['Parameter']['Value']

#MYSQL DCB CREDENTIALS
MYSQLDCB = {
    "HOST":dcbHost,
    "USERNAME":dcbUsername,
    "PASSWORD":dcbPassword,
    "DB":dcbDB
}

#MYSQL WALLET CREDENTIALS
MYSQLWALLET = {
    "HOST":walletHost,
    "USERNAME":walletUsername,
    "PASSWORD":walletPassword,
    "DB":walletDB
}

#MYSQL DISB CREDENTIALS
MYSQLDISB = {
    "HOST":disbHost,
    "USERNAME":disbUsername,
    "PASSWORD":disbPassword,
    "DB":disbDB
}
