"""
This file includes global contant.
"""
import os

CWD = os.getcwd()
DATA_DIR = os.path.join(CWD, 'data')
ID_TO_MOVIE_FILE_NAME = 'id_to_movie.csv'
ID_TO_MOVIE_FILE_PATH = os.path.join(DATA_DIR, ID_TO_MOVIE_FILE_NAME)
ID_TO_DETAIL_FILE_NAME = 'id_to_detail.pickle'
ID_TO_DETAIL_FILE_PATH = os.path.join(DATA_DIR, ID_TO_DETAIL_FILE_NAME)
TOKEN_TO_INDEX_FILE_NAME = 'token_to_index.pickle'
TOKEN_TO_INDEX_FILE_PATH = os.path.join(DATA_DIR, TOKEN_TO_INDEX_FILE_NAME)
