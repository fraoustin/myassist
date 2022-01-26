from flask import Blueprint, flash, redirect, url_for, request, render_template, current_app
from flask_login import login_required, current_user
from auth import checkAdmin, User
import json
import os
import shutil
import time
import logging
import threading


__version__ = '0.1.0'

LEVEL_LOG = {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}


@login_required
def core():
    return render_template('core.html', user=current_user)


class Core(Blueprint):
    def __init__(self, name='core', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/', 'core', core, methods=['GET'])

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except Exception:
            app.logger.error("init core on register is failed")
