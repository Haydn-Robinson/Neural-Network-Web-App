from neuralnetworkwebapp import create_app
from os.path import join, dirname
from dotenv import load_dotenv

if __name__ == '__main__':

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    app = create_app()
    app.run(debug=True)