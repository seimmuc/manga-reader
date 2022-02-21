## manga-reader
A very simple manga reader flask app.

---
### Installation
1. Install Python 3.10 with pip if you haven't already.
2. Install Pipenv by running `pip install --user pipenv` if you haven't already
3. Clone this repository into a new project directory
4. Run `pipenv install` from the project directory
5. To run the dev server use following:
    ##### Windows (cmd / batch)
    ```winbatch
    set FLASK_APP=mangareader;set FLASK_ENV=development;pipenv run flask run
    ```
    ##### Linux (sh / bash / zsh)
    ```shell
    export FLASK_APP=mangareader;export FLASK_ENV=development;pipenv run flask run
    ```
    Use Ctrl+C to stop the server.
