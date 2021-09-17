from neuralnetworkwebapp import create_app
import waitress
from os.path import join, dirname
from dotenv import load_dotenv

if __name__ == '__main__':

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    waitress.serve(create_app())

