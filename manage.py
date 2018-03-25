import os
import configparser
from app import app

if __name__ == "__main__":
    repo_dir = os.path.dirname(os.path.realpath(__file__))

    # Load env variables from .env config file
    cp = configparser.SafeConfigParser()
    cp.read(os.path.join(repo_dir, ".env"))

    # Load the files variables into the environment
    for i in cp.items('flask'):
        os.environ[i[0].upper()] = i[1]

    # Start the flask dev server
app.run(debug=True, use_reloader=True)