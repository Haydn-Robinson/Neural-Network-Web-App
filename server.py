from neuralnetworkwebapp.persistence import init_manager
import os
from os.path import join, dirname
from dotenv import load_dotenv

if __name__ == '__main__':

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    print(dotenv_path)

    if os.environ.get('ON_HEROKU') == 'True':
        MANAGER_HOST = ''
        MANAGER_PORT= int(os.environ.get("PORT"))
    else:
        MANAGER_HOST = '127.0.0.1'
        MANAGER_PORT= 22109

    MANAGER_AUTHKEY = bytes(os.environ.get('MANAGER_AUTHKEY'), 'utf8')

    init_manager(MANAGER_HOST, MANAGER_PORT, MANAGER_AUTHKEY)
