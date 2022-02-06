from flask import Blueprint, render_template, current_app, request, redirect, url_for
from flask_login import login_required
from auth import checkAdmin
from core.main import Core

from db import db
from db.models import ParamApp

__version__ = '0.1.0'

PARAMS = []


def get_params():
    return [param for param in ParamApp.all(sortby=ParamApp.key) if param.key.startswith("basic_")]


@login_required
@checkAdmin()
def view():
    params = {}
    params['APP_DESC'] = current_app.config.get("APP_DESC", "")
    params['APP_NAME'] = current_app.config.get("APP_NAME", "")
    params['APP_VERSION'] = current_app.config.get("VERSION", "")
    params['APP_HOST'] = current_app.config.get("APP_HOST", "")
    params['APP_PORT'] = current_app.config.get("APP_PORT", "")
    params['APP_DEBUG'] = current_app.config.get("APP_DEBUG", "")
    params['APP_DIR'] = current_app.config.get("APP_DIR", "")
    params['APP_LOGS'] = current_app.config.get("APP_LOGS", "")
    return render_template('paramapp.html', plugins=current_app.config['PLUGINS'], params_app=get_params(), **params)


@login_required
@checkAdmin()
def update():
    for paramregister in get_params():
        paramregister.value = request.form.get(paramregister.key, '')
        paramregister.save()
    [current_app.blueprints[blueprint] for blueprint in current_app.blueprints if isinstance(current_app.blueprints[blueprint], Core)][0].init_db()
    return redirect(url_for('paramapplication.view'))


class ParamApplication(Blueprint):
    def __init__(self, name='paramapplication', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/settings', 'view', view, methods=['GET'])
        self.add_url_rule('/settings', 'update_settings', update, methods=['POST'])

    def init_db(self):
        for param in PARAMS:
            if ParamApp.get(param) is None:
                db.session.add(ParamApp(key=param, value=''))
                db.session.commit()
                current_app.logger.info("create param register %s" % param)

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except Exception:
            app.logger.error("init register on register is failed")
