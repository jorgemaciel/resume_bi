from src.google_drive import GoogleDrive


service_account_file = '../credentials.json'
folder_name = 'Realize o upload do seu currículo aqui (PDF, máximo 10 mb): (File responses)'
local_folder_path = '../cv_pdf'

drive = GoogleDrive(service_account_file, folder_name)
folder_id = '1Z4hPkYkCUTdZ3uWZhfp8si9luA-bGmHDfIunk-lZlF1PlSHco6L4ED6qGdTGXI6yICQMehqG'

drive.download_folder(folder_id, local_folder_path)