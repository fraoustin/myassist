import os
import time
from flask import current_app, render_template, request
from flask_login import login_required, current_user
from plugins import Plugin
from robot import Robot, Singleton
import yaml
from db import db
from db.models import ParamApp
import chess
import chess.engine
import chess.svg
import urllib.request

__version__ = "0.0.1"

COORDINATOR = 'in'


class MasterChess(metaclass=Singleton):

    def __init__(self, eng, fen, pieces, port=5000):
        self._engine = chess.engine.SimpleEngine.popen_uci(eng)
        self._board = chess.Board()
        if len(fen) > 0:
            self._board.set_fen(fen)
        self._pieces = pieces
        self._last_move = None
        self._port = port

    def new_play(self):
        self._board = chess.Board()
        self._last_move = None

    @property
    def svg(self):
        if self._last_move is not None:
            return chess.svg.board(self._board, lastmove=self._last_move)
        return chess.svg.board(self._board)

    @property
    def fen(self):
        return self._board.fen()

    def move(self, mov):
        self._board.push_san(mov)
        if self._board.is_check() is False:
            result = self._engine.play(self._board, chess.engine.Limit(time=0.1))
            self._board.push(result.move)
            self._last_move = result.move
            Robot().emit_event("", "say:%s %s" % (self._pieces[self._board.piece_at(chess.parse_square(self._board.uci(result.move)[2:])).symbol().upper()][0], result.move.uci()))

        if self._board.is_check() is True:
            time.sleep(1)
            Robot().emit_event("", "say:check")
        if self._board.is_checkmate() is True:
            time.sleep(1)
            Robot().emit_event("", "say:mate")
        self.save()

    def save(self):
        req = urllib.request.Request("http://127.0.0.1:%s/api/chess/save" % self._port)
        handle = urllib.request.urlopen(req)
        handle.close()

    @property
    def legal_moves(self):
        return [(self._board.uci(mv), self._pieces[self._board.piece_at(chess.parse_square(self._board.uci(mv)[0:2])).symbol()][0]) for mv in self._board.legal_moves]

    @property
    def is_check(self):
        return self._board.is_check()

    @property
    def is_checkmate(self):
        return self._board.is_checkmate()


@login_required
def mchess():
    return render_template('chess.html', user=current_user, plugins=current_app.config['PLUGINS'], master=MasterChess())


@login_required
def chess_svg():
    return MasterChess().svg


@login_required
def chess_play():
    chess_move(request.form.get('query', ''))
    return {'status': 'ok'}, 200


def chess_move(answer, mov):
    MasterChess().move(mov)
    training_chess()


def training_chess():
    global COORDINATOR
    for train in Robot().trainings('chessmove'):
        Robot().remove_training(train['answer'], train['response'])
    for move in MasterChess().legal_moves:
        Robot().training(move[0], "chessmove:%s" % move[0])
        Robot().training("%s %s" % (move[1], move[0]), "chessmove:%s" % move[0])
        Robot().training("%s %s %s" % (move[1], move[0][0:2], move[0][2:]), "chessmove:%s" % move[0])
        Robot().training("%s %s %s %s %s" % (move[1], move[0][0], move[0][1], move[0][2], move[0][3]), "chessmove:%s" % move[0])
        Robot().training("%s %s %s %s" % (move[1], move[0][0:2], COORDINATOR, move[0][2:]), "chessmove:%s" % move[0])
        Robot().training("%s %s %s %s %s %s" % (move[1], move[0][0], move[0][1], COORDINATOR, move[0][2], move[0][3]), "chessmove:%s" % move[0])


def chess_save():
    param = ParamApp.get("chess")
    param.value = MasterChess().fen
    param.save()
    return {'status': 'ok'}, 200


def new_play(answer, response):
    MasterChess().new_play()
    training_chess()
    MasterChess().save()


class Mchess(Plugin):
    def __init__(self, *args, **kw):
        Plugin.__init__(self, *args, **kw)
        self.before_app_first_request(self._init)
        self.add_url_rule('/mchess', 'mchess', mchess, methods=['GET'])
        self.add_url_rule('/api/chess/play', 'chess play', chess_play, methods=['POST'])
        self.add_url_rule('/api/chess/save', 'chess save', chess_save, methods=['GET'])
        self.add_url_rule('/api/chess/svg', 'chess svg', chess_svg, methods=['GET'])
        self.pieces = {}
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "files", "basic.yaml"), "r") as stream:
            try:
                doc = yaml.safe_load(stream)
                play = doc['chatbot']['chess']
                for answer in play['answers']:
                    Robot().training(answer, "chess")
                for piece in doc['chatbot']['piece']:
                    self.pieces[piece] = doc['chatbot']['piece'][piece]
                global COORDINATOR
                COORDINATOR = doc['chatbot']['coordinator']['in'][0]
            except yaml.YAMLError as exc:
                print(exc)
        Robot().add_event("chess", new_play)
        Robot().add_event("chessmove", chess_move)

    def init_db(self):
        if ParamApp.get("basic_stockfish") is None:
            db.session.add(ParamApp(key="basic_stockfish", value="/usr/games/stockfish"))
            db.session.commit()
        if ParamApp.get("chess") is None:
            db.session.add(ParamApp(key="chess", value=""))
            db.session.commit()
        MasterChess(eng=ParamApp.getValue("basic_stockfish"), fen=ParamApp.getValue("chess"), pieces=self.pieces)
        training_chess()

    def _init(self):
        MasterChess()._port = current_app.config['APP_PORT']
