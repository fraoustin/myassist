import os
import logging
import importlib
import configparser
from flask import Flask, render_template
from db import db
from auth import Auth, login_required
from info import Info
from static import Static
from paramapplication import ParamApplication
from core import Core
from robot import Robot


MYASSIST_LOGO = """
      #######
    ##       ##
   #           #
  #             #
 #  ##       ##  #
#  ####     ####  #
# ######   ###### #
# ############### #
#  ####     ####  #
#   ##       ##   #
 #               #
  #             #
   #####   #####
  #     ###     #
 #               #
 #               #
 #  #   ###   #  #
 # #     #     # #
  #      #      #
  #      #      #
   #############
"""

toBoolean = {'true': True, 'false': False}

MYASSIST_DIR = os.environ.get('MYASSIST_DIR', os.path.dirname(os.path.abspath(__file__)))
config = configparser.ConfigParser()
config.read(os.path.join(MYASSIST_DIR, 'myassist.cfg'))
if 'MYASSIST' not in config.keys():
    config['MYASSIST'] = {}
MYASSIST_PORT = int(os.environ.get('MYASSIST_PORT', config['MYASSIST'].get('Port', '5000')))
MYASSIST_DEBUG = toBoolean.get(os.environ.get('MYASSIST_DEBUG', config['MYASSIST'].get('Debug', 'false')), False)
MYASSIST_HOST = os.environ.get('MYASSIST_HOST', config['MYASSIST'].get('Host', '0.0.0.0'))
MYASSIST_LOGS = os.environ.get('MYASSIST_LOGS', config['MYASSIST'].get('Log', os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")))

app = Flask(__name__)
app.config["VERSION"] = "0.0.1"

app.config["APP_PORT"] = MYASSIST_PORT
app.config["APP_HOST"] = MYASSIST_HOST
app.config["APP_DEBUG"] = MYASSIST_DEBUG
app.config["APP_DIR"] = MYASSIST_DIR
app.config["APP_LOGS"] = MYASSIST_LOGS

# db SQLAlchemy
database_file = "sqlite:///{}".format(os.path.join(MYASSIST_DIR, "myassist.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('MYASSIST_DB', config['MYASSIST'].get('Db', database_file))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# generate robot
robot = Robot('Ava')

# register Auth
app.register_blueprint(Auth(url_prefix="/"))
app.config['APP_NAME'] = os.environ.get('MYASSIST_NAME', 'My Assist')
app.config['APP_DESC'] = os.environ.get('MYASSIST_DESC', 'Personnal Assistant')
# register Info
app.register_blueprint(Info(url_prefix="/"))
# register Static
MYASSIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
app.register_blueprint(Static(name="js", url_prefix="/javascripts/", path=os.path.join(MYASSIST_PATH, "javascripts")))
app.register_blueprint(Static(name="siimple", url_prefix="/siimple/", path=os.path.join(MYASSIST_PATH, "siimple")))
app.register_blueprint(Static(name="css", url_prefix="/css/", path=os.path.join(MYASSIST_PATH, "css")))
app.register_blueprint(Static(name="img", url_prefix="/img/", path=os.path.join(MYASSIST_PATH, "img")))
# register ParamApplication
app.register_blueprint(ParamApplication(url_prefix="/"))

# register MYASSIST
app.register_blueprint(Core(url_prefix="/"))
app.config['PLUGINS'] = []
for node in [node for node in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')) if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins', node)) and '_' not in node]:
    module = importlib.import_module('plugins.%s.main' % node)
    plugin = getattr(module, node.capitalize())(name=node, url_prefix="/")
    app.register_blueprint(plugin)
    app.config['PLUGINS'].append(plugin)
app.config['PLUGINS'].sort()


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    return render_template('index.html')


if __name__ == "__main__":
    print(MYASSIST_LOGO)
    print("MYASSIST %s" % app.config["VERSION"])
    db.init_app(app)
    with app.app_context():
        db.create_all()
    with app.app_context():
        for bp in app.blueprints:
            if 'init_db' in dir(app.blueprints[bp]):
                app.blueprints[bp].init_db()
    app.logger.setLevel(logging.DEBUG)
    app.run(host=MYASSIST_HOST, port=MYASSIST_PORT, debug=MYASSIST_DEBUG)
