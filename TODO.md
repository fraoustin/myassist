
## TODO

- jouer une playlist
- ajouter dans "le bureau"
- avoir le temps restant de la minuterie
- gérer et ajouter des tâches
- faire un gestionnaire de scénario
- gérer les question quelle heure est il? quelle date?
- envoyer un sms non prévu: envoie un sms à laure as tu pris du pain

- pb de silence dans 1 minute et lance france inter
- trouver un moyen de gérer les moteurs et le son

pour le deuxième utilisé un vieux raspberry ou acheter chez https://rer-electronic.fr/1021-cartes-raspberry-pi
pour relais https://rer-electronic.fr/1021-cartes-raspberry-pi

tester le double son et voir si usage de playlist

#!/usr/bin/env python3
import mpv

player = mpv.MPV(ytdl=True, input_default_bindings=True, input_vo_keyboard=True)

player.playlist_append('https://youtu.be/PHIGke6Yzh8')
player.playlist_append('https://youtu.be/Ji9qSuQapFY')
player.playlist_append('https://youtu.be/6f78_Tf4Tdk')

player.playlist_pos = 0

while True:
    # To modify the playlist, use player.playlist_{append,clear,move,remove}. player.playlist is read-only
    print(player.playlist)
    player.wait_for_playback()

ou alors la time position https://github.com/jaseg/python-mpv