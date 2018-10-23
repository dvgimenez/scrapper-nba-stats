###########################################
################## IMPORTACIÓ DE LLIBRERIES
###########################################

import requests
from bs4 import BeautifulSoup
import os
import csv
import re
import string




################################################
############################## funció get_link()
# Obtenció del link al qual es farà el scraper.
################################################
# var entrada:
# player_sel: jugador que es vol analitzar.
# season: temporada que es vol analitzar.
# var de sortida:
# link_pl_seas: link complet al qual es realitzarà el scraper.
#       i.e.: https://www.basketball-reference.com/players/g/gasolpa01.html

def get_link(player_sel, season):
    stop = False
    url = 'https://www.basketball-reference.com/players/'
    alph = string.ascii_lowercase #Creació de l'alfabet
    
    for letter in alph:
        url_alph = url + letter
        page_home = requests.get(url_alph)
        soup_home = BeautifulSoup(page_home.content, 'html.parser')
        players_list = soup_home.find_all('a',href=True)

        for player in players_list:
            if player.find(text = True) == player_sel: 
                link = player.get('href')
                link_player = url_alph + link[10:].split('.')[0] # link elimino /players/ i .htm
                link_pl_seas = link_player + '/gamelog/' + str(season)
                stop = True
                break
        if stop == True: break
    return(link_pl_seas)
	
	
	

################################################
############################## funció get_info()
# Obtenció de les dades per generar el dataset.
################################################
# var entrada:
# link_study: link obtingut de la funció get_link().
# var sortida:
# all_match: llista amb les dades extretes del jugador.

def get_info(link_study):
    page_study = requests.get(link_study)
    soup_study = BeautifulSoup(page_study.content, 'html.parser')
    
    all_tables = soup_study.find_all('table')
    for tables in all_tables:
        table = tables.find('tbody')

    all_match = []
    header_match = ['Date', 'Opp', 'W/L', 'time', '2P', '3P', '1P', 'Off Reb', 'Def Reb', 'Assist', 'Steal', 'Foul', 'Points', 'Game Score']
    all_match.append(header_match)

    for row in table.find_all("tr", id = True):
        cells = row.find_all('td')
        date = cells[1].find(text=True)
        opponent = cells[5].find(text=True)
        result = cells[6].find(text=True)[0] # és un string on la primera lletra indica W o L.
        minutes = cells[8].find(text=True)
        t3 = int(cells[12].find(text=True))
        t2 = int(cells[9].find(text=True)) - t3 # Total tirs de camp - tirs de 3
        t1 = int(cells[15].find(text=True))
        off_reb = int(cells[18].find(text=True))
        def_reb = int(cells[19].find(text=True))
        assist = int(cells[21].find(text=True))
        steal = int(cells[22].find(text=True))
        foul = int(cells[25].find(text=True))
        points = int(cells[26].find(text=True))
        score = float(cells[27].find(text=True))

        all_match.append([date, opponent, result, minutes, t2, t3, t1, off_reb, def_reb, assist, steal, foul, points, score])
 
    return(all_match)
	
	
	

################################################
############################### funció get_csv()
# Creació de l'arxiu csv
################################################
# var entrada:
# all_match: llista amb les dades extretes del jugador.
# player_sel: jugador que s'ha analitzat.
# season: temporada que s'ha analitzat

def get_csv(all_match, player_sel, season):
    player = player_sel.replace(' ', '_')
    filename = player + '_season_' + str(season) + '.csv'
    with open(filename, 'w', newline='') as csvFile:
        matchWriter = csv.writer(csvFile, delimiter = ';')
        for match in all_match:
            matchWriter.writerow(match)
    print('Dataset ' + filename + ' created ! !')
    return
	
	
	

################################################
########################## EXECUCIÓ DEL SCRAPER
# Sol·licitud de les variables d'entrada + crida
# de les funcions prèviament definides.
################################################

player = str(input('Please enter player name and surname (i.e. Pau Gasol): '))
season = str(input('Please enter season (i.e. 2018): '))

print('\n  Executing scraper\n')
try:
    link_study = get_link(player, season)
    try:
        info_matches = get_info(link_study)
    except Exception as e: print('ERROR: Season not found...')
except Exception as e: print('ERROR: Player not found...')
get_csv(info_matches, player, season)