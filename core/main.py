from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from db.models import ParamApp
from db import db
import logging
from robot import RobotHandler, Robot

__version__ = '0.1.0'


@login_required
def core():
    return render_template('core.html', user=current_user, plugins=current_app.config['PLUGINS'])


@login_required
def logs():
    logger = logging.getLogger()
    handler = [handler for handler in logger.handlers if isinstance(handler, RobotHandler) is True][0]
    return render_template('logs.html', user=current_user, plugins=current_app.config['PLUGINS'], logs=handler.logs, handler=handler)


@login_required
def clear():
    logger = logging.getLogger()
    handler = [handler for handler in logger.handlers if isinstance(handler, RobotHandler) is True][0]
    handler.clear()
    return {'status': 'ok'}, 200


class Core(Blueprint):
    def __init__(self, name='core', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/', 'core', core, methods=['GET'])
        self.add_url_rule('/logs', 'logs', logs, methods=['GET'])
        self.add_url_rule('/api/logs/clear', 'logs clear', clear, methods=['GET'])

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except Exception:
            app.logger.error("init core on register is failed")

    def init_db(self):
        if ParamApp.get("basic_langue") is None:
            db.session.add(ParamApp(key="basic_langue", value="fr"))
            db.session.commit()
        if ParamApp.get("basic_name") is None:
            db.session.add(ParamApp(key="basic_name", value=Robot().name))
            db.session.commit()
        if ParamApp.get("basic_mic langue") is None:
            db.session.add(ParamApp(key="basic_mic langue", value="fr-FR"))
            db.session.commit()
        if ParamApp.get("basic_mic timeout") is None:
            db.session.add(ParamApp(key="basic_mic timeout", value="0"))
            db.session.commit()
        if ParamApp.get("basic_mic energy_threshold") is None:
            db.session.add(ParamApp(key="basic_mic energy_threshold", value="0"))
            db.session.commit()
        if ParamApp.get("basic_similarity level") is None:
            db.session.add(ParamApp(key="basic_similarity level", value="0.9"))
            db.session.commit()
        if ParamApp.get("basic_and operator") is None:
            db.session.add(ParamApp(key="basic_and operator", value="et"))
            db.session.commit()
        Robot().name = ParamApp.getValue("basic_name")
        Robot().mic.lang = ParamApp.getValue("basic_mic langue")
        Robot().mic.timeout = int(ParamApp.getValue("basic_mic timeout"))
        Robot().mic.energy_threshold = int(ParamApp.getValue("basic_mic energy_threshold"))
        Robot().level = ParamApp.getValue("basic_similarity level")
        Robot().andoperator = ParamApp.getValue("basic_and operator")
        try:
            Robot().mic.start()
        except Exception:
            pass
