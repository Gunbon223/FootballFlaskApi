from flask import Flask
from config import create_app
app = create_app("Football Management System")


if __name__ == '__main__':
    app.run()
