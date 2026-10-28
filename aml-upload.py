
import lib.config as cfg
import logging, datetime
x = datetime.datetime.now()
import os
from datetime import datetime
GLOGGER = logging.getLogger('GENERAL')
GLOG_FILENAME = cfg.BASEPATH+'/logs/general.log'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' , filename=GLOG_FILENAME,  datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
import paramiko
reports_folder = "reports/"


def uploadTmsFiles():

    try:
        for file_name in os.listdir(reports_folder):
            if file_name.endswith(".txt"):
                full_path = os.path.join(reports_folder, file_name)
                key = os.path.splitext(file_name)[0]  # Remove .txt extension
                sendToFtp(full_path, key)

    except Exception as e:
        print(f"Error processing report files: {e}")
        GLOGGER.error(f"Error processing report files: {e}")


def mkdir_p(sftp, remote_directory):
    dirs = remote_directory.strip('/').split('/')
    path = ''
    for folder in dirs:
        path += '/' + folder
        try:
            sftp.stat(path)
        except FileNotFoundError:
            sftp.mkdir(path)

def sendToFtp(file_name, file_):
    from datetime import datetime
    sftp_username = cfg.sftpUsername
    sftp_password = cfg.sftpPass
    sftp_host = cfg.sftpHost
    sftp_port = int(cfg.sftpPort)
    remote_path = cfg.sftpDir
    try:
        transport = paramiko.Transport((sftp_host, sftp_port))
        transport.connect(username=sftp_username, password=sftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        remoteDir = '/'
        try:
            sftp.chdir(remoteDir)
        except IOError as e:
            print(f"Error sftp: {e}")
        file_path = str(file_name)
        file_name_with_extension = os.path.basename(file_path)
        local_file =  file_name
        remote_file = '/'+str(file_name_with_extension)
        sftp.put(local_file, remote_file)
        sftp.close()
        transport.close()
        print(file_ + ".txt uploading to sftp......done")
        GLOGGER.info(file_ + ".txt uploading to sftp......done")
    except Exception as e:
        print(f"Error sendToFtp: {e}")
if __name__ == "__main__":
    uploadTmsFiles()
# def sendToFtp(file_name, file_):
#     from datetime import datetime
#     sftp_username = cfg.sftpUsername
#     sftp_password = cfg.sftpPass
#     sftp_host = cfg.sftpHost
#     sftp_port = int(cfg.sftpPort)
#     remote_path = cfg.sftpDir
#
#     try:
#         transport = paramiko.Transport((sftp_host, sftp_port))
#         transport.connect(username=sftp_username, password=sftp_password)
#         sftp = paramiko.SFTPClient.from_transport(transport)
#         current_date = datetime.now().strftime("%d-%m-%Y")
#         remote_folder = f"{remote_path}/{current_date}/"
#         try:
#             sftp.chdir(remote_folder)
#         except IOError:
#             sftp.mkdir(remote_folder)
#         s3_path = cfg.BASEPATH + str(file_name)
#         file_name_with_extension = os.path.basename(s3_path)
#         remote_file_path = f"{remote_folder}{file_name_with_extension}"
#         sftp.put(s3_path, remote_file_path)
#         sftp.close()
#         transport.close()
#         print(file_ + ".txt uploading to sftp......done")
#         GLOGGER.info(file_ + ".txt uploading to sftp......done")
#     except Exception as e:
#         print(f"Error: {e}")
#
# if __name__ == "__main__":
#     uploadTmsFiles()