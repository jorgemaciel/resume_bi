from src.google_drive import GoogleDrive

from src.resume_cv import ResumeAnalyzer
import os
from dotenv import load_dotenv
import glob
import random

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

pdf_directory = '../cv_pdf/cv1'


def download_cv_from_google_drive(service_account_file='../credentials.json',
                                  folder_name='Realize o upload do seu currículo aqui (PDF, máximo 10 mb): (File responses)',
                                  local_folder_path='../cv_pdf',
                                  folder_id='1Z4hPkYkCUTdZ3uWZhfp8si9luA-bGmHDfIunk-lZlF1PlSHco6L4ED6qGdTGXI6yICQMehqG'):
    """
    Downloads CVs from a specified Google Drive folder.

    Args:
        service_account_file (str, optional): Path to the service account credentials file. Defaults to '../credentials.json'.
        folder_name (str, optional): Name of the Google Drive folder to download from. Defaults to 'Realize o upload do seu currículo aqui (PDF, máximo 10 mb): (File responses)'.
        local_folder_path (str, optional): Path to the local directory where CVs will be saved. Defaults to '../cv_pdf'.
        folder_id (str, optional): ID of the Google Drive folder. Defaults to '1Z4hPkYkCUTdZ3uWZhfp8si9luA-bGmHDfIunk-lZlF1PlSHco6L4ED6qGdTGXI6yICQMehqG'.
    """
    drive = GoogleDrive(service_account_file, folder_name)
    drive.download_folder(folder_id, local_folder_path)


def generate_random_word(length=5, include_special=False):
    """
    Generates a random word.

    Args:
        length (int, optional): Length of the word. Defaults to 5.
        include_special (bool, optional): Whether to include special characters. Defaults to False.

    Returns:
        str: A random word.
    """

    alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890'
    if include_special:
        alphabet += '~!@#$%^&*()_+=-`|}{[]\:;?><,./'

    word = ''.join(random.choice(alphabet) for _ in range(length))
    return word


def analyze_resumes(pdf_directory, google_api_key):
    """
    Analyzes all PDF resumes in the specified directory using the provided Google API key.

    Args:
        pdf_directory (str): The path to the directory containing the PDF files.
        google_api_key (str): Your Google API Key.
    """

    for pdf_file in glob.glob(os.path.join(pdf_directory, '*.pdf')):
        collection_name = generate_random_word(length=8)
        analyzer = ResumeAnalyzer(google_api_key=google_api_key, collection_name=collection_name)
        print(f"Analyzing resume: {pdf_file}")
        analyzer.analyze_resume(pdf_file)


if __name__ == '__main__':
    #download_cv_from_google_drive()
    analyze_resumes(pdf_directory, google_api_key)