from flask import Flask
import os

Flask('fake-app').run(port=os.environ['PORT'])
