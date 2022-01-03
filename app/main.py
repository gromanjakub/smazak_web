from flask import Flask,render_template,request
import time
import requests
import pandas
from bs4 import BeautifulSoup
import unidecode
import re
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from requests.exceptions import MissingSchema
import geocoder

app = Flask(__name__)

@app.route("/")
def home():
    
    return render_template("form.html")
    
restaurace1 = ""
restaurace2 = ""
restaurace3 = ""
vzdalenost1 = ""
vzdalenost2 = ""
vzdalenost3 = ""
@app.route('/result/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to 'home' to submit form"
    if request.method == 'POST':
        form_data = request.form
        #m = request.form["hledane_jidlo"] + request.form["mesto"]
        

        #return("m je " + m)


        mesto_raw = request.form["mesto"]
        mesto_raw2 = mesto_raw.replace(" ", "-")  # později oživit a smazat mesto dole
        mesto = unidecode.unidecode(mesto_raw2)

        if "Praha" in mesto_raw:
            mesto_raw = "Praha"
        
        #mesto = "Praha-2"
        if mesto.lower() == "praha":
            cast_prahy = input("Napište číslo části Prahy: ")
            mesto = mesto + "-" + cast_prahy
        
        stranka = "https://www.menicka.cz/" + mesto + ".html"
        
        #adresa_uzivatele = "U zvonařky 11, Praha, Česko"
        adresa_uzivatele = request.form["adresa_uzivatele"]
        adresa_uzivatele = adresa_uzivatele + "," + mesto_raw + "," + "Česko"
        
        #veskera_nabidka = {}
        nabidka_list = []
        
        hledane_jidlo = request.form["hledane_jidlo"]
        
        #hledane_jidlo = "řízek"
        
        if (hledane_jidlo.lower() == "smažák"):
            hledane_jidlo = "smažený sýr"
        
        podniky_s_jidlem = []
        
        
        def get_menicka():
            web = requests.get(stranka)
            content = web.content
            soup = BeautifulSoup(content, features="html.parser")
            global menicka
            menicka = soup.find_all('div', attrs={"class": "menicka_detail"})
            nazvy = soup.find_all('div', attrs={"class": "nazev"})
        
        
        def get_polozky(menicka):
            for menu in menicka:
                spinava_nabidka = menu.find_all('div', attrs={"class": "nabidka_1"})
                spinava_nabidka2 = menu.find_all('div', attrs={"class": "nabidka_2"})
        
                aktualni_nabidka = []
                for nabidka in spinava_nabidka:
                    nazev_podniku = menu.find_all(
                        'div', attrs={"class": "nazev"})[0].get_text()
                    cista_nabidka = nabidka.get_text().lower()
        
                    aktualni_nabidka.append(cista_nabidka)
                    nabidka_list.append(nazev_podniku)
                    nabidka_list.append(cista_nabidka)
        
                for nabidka in spinava_nabidka2:
                    nazev_podniku2 = menu.find_all(
                        'div', attrs={"class": "nazev"})[0].get_text()
                    cista_nabidka2 = nabidka.get_text().lower()
        
                    aktualni_nabidka.append(cista_nabidka2)
                    nabidka_list.append(nazev_podniku2)
                    nabidka_list.append(cista_nabidka2)
                # veskera_nabidka.update({nazev_podniku:aktualni_nabidka})
        
        
        def najdi_smazak(nabidka_list, podniky_s_jidlem):
            for jidlo in nabidka_list:
                if hledane_jidlo in jidlo:
                    pozice = nabidka_list.index(jidlo)
                    # print(nabidka_list[pozice-1])
                    podniky_s_jidlem.append(nabidka_list[pozice-1])
            podniky_s_jidlem = list(set(podniky_s_jidlem))
        
        
        get_menicka()
        get_polozky(menicka)
        najdi_smazak(nabidka_list, podniky_s_jidlem)
        
        # print(hledane_jidlo + " je dnes v menu následujících podniků: ")   #tady tisknu seznam podniků s daným jídlem
        #print(*list(set(podniky_s_jidlem)), sep="\n")
        
        
        def get_vzdalenost_new(adresa_podniku, adresa_uzivatele):
            geolocator = Nominatim(user_agent="test")
            souradnice_uzivatele = geocoder.osm(adresa_uzivatele).latlng
            souradnice_podniku = geocoder.osm(adresa_podniku).latlng
            #print("Vzdálenost mezi místy je " + str(round(geodesic((lok11, lok12), (lok21, lok22)).m,0)) + " m.")
            distance = round(geodesic(souradnice_uzivatele, souradnice_podniku).m, 0)
            return(distance)
        
        
        def get_odkazy_podniku(stranka):
            web = requests.get(stranka)
            content = web.content
            soup = BeautifulSoup(content, features="html.parser")
            nazvy = soup.find_all('div', attrs={"class": "nazev"})
        
            odkazy = []
            for nazev in nazvy:
                odkazy.append(nazev.find_all("a"))
        
            jmeno_odkaz = []
            for odkaz in odkazy:
                jmeno_odkaz.append(odkaz[0].get_text())
                jmeno_odkaz.append(odkaz[0].get("href"))
        
            pomocny_list_odkazy = []
            for a in podniky_s_jidlem:
                if a in jmeno_odkaz:
                    pomocny_list_odkazy.append(a)
                    indexaplus = jmeno_odkaz.index(a)+1
                    pomocny_list_odkazy.append(jmeno_odkaz[indexaplus])
        
            jen_odkazy = []
            for odkaz in pomocny_list_odkazy[1::2]:
                jen_odkazy.append(odkaz)
        
            return jen_odkazy
        # get_odkazy_podniku(stranka)
        
        
        spinave_jmeno_adresa = []
        adresy = []
        
        for odkaz in get_odkazy_podniku(stranka):
            try:
                web_odkazu = requests.get(odkaz)
                content_odkazu = web_odkazu.content
                odkaz_soup = BeautifulSoup(content_odkazu, features="html.parser")
                odkaz_adresa = odkaz_soup.find_all('div', attrs={"class": "adresa"})
                jmeno = odkaz_soup.find_all("h1")[0].get_text().strip()
                adresy.append(odkaz_adresa[0].get_text())
                spinave_jmeno_adresa.append(jmeno)
                spinave_jmeno_adresa.append(odkaz_adresa[0].get_text())
            except MissingSchema:
                pass
        
        jmeno_adresa = []
        
        
        def get_jmeno_adresa(spinave_jmeno_adresa):
        
            i = 0
            for f in spinave_jmeno_adresa:
                if i % 2 == 0:
                    jmeno_adresa.append(f)
                else:
                    adresa = f
                    split = adresa.split(",")
                    adresa = split[0] + "," + split[1] + \
                        ", " + split[3] + ", Czech Republic"
                    jmeno_adresa.append(adresa)
                i = i+1
        
           
        
        
        get_jmeno_adresa(spinave_jmeno_adresa)
        
        #adresa_podniku = spinave_jmeno_adresa[1]
        
        vzdalenosti = []
        cisla_vzdalenosti = []
        
        
        def get_vzdalenost_restaurace(jmeno_adresa):
        
            p = 1
        
            for a in jmeno_adresa:
                
                if p % 2 == 0:
                    time.sleep(0.5)
                    try:
                        m = get_vzdalenost_new(a, adresa_uzivatele)
                        vzdalenosti.append(m)
                        cisla_vzdalenosti.append(m)
                    except TypeError:
                        a.split(",")
                        asplit = a.split(",")
                        a = asplit[0] + "," + asplit[2]
                        m = get_vzdalenost_new(a, adresa_uzivatele)
                        cisla_vzdalenosti.append(m)
                else:
                    vzdalenosti.append(a)
                p = p+1
            return(cisla_vzdalenosti, vzdalenosti)
        
        
        get_vzdalenost_restaurace(jmeno_adresa)
        
        
        #def print_restaurace_vzdalenosti(cisla_vzdalenosti, vzdalenosti):
            
            
        seznam_nejblizsich_restauraci = []
    
        print("Kam na " + hledane_jidlo + " poblíž vás?")
    
        if cisla_vzdalenosti:  # dá true pokud je to neprázdné
            # vyberu nejmenší číslo z listu kde jsou jen čísla
            nejmensi = min(cisla_vzdalenosti)
            # najdu pozici toho čísla v seznamu kde je jméno i vzdálenost
            pozice_nejmensiho = vzdalenosti.index(nejmensi)
            index_nejmensiho = cisla_vzdalenosti.index(nejmensi)
            #return("Nejbližší restaurace je " + str(vzdalenosti[pozice_nejmensiho-1]) + ". " + "Vzdálenost: " + str(vzdalenosti[pozice_nejmensiho]) + "m.")  # jméno restaurace je vždycky nalevo
            restaurace1 = str(vzdalenosti[pozice_nejmensiho-1])
            vzdalenost1 = str(vzdalenosti[pozice_nejmensiho])
            seznam_nejblizsich_restauraci.append(vzdalenosti[pozice_nejmensiho-1])
            seznam_nejblizsich_restauraci.append(vzdalenosti[pozice_nejmensiho])
            cisla_vzdalenosti.pop(index_nejmensiho)
            #yield(restaurace1)
    
            if cisla_vzdalenosti:
                #print("cisla vzdalenosti:")
                #print( cisla_vzdalenosti )
    
                nejmensi = min(cisla_vzdalenosti)
                pozice_nejmensiho = vzdalenosti.index(nejmensi)
                index_nejmensiho = cisla_vzdalenosti.index(nejmensi)
                #return("Druhá nejbližší restaurace je " + str(vzdalenosti[pozice_nejmensiho-1]) + ". " + "Vzdálenost: " + str(vzdalenosti[pozice_nejmensiho]) + "m.")  # jméno restaurace je vždycky nalevo
                restaurace2 = str(vzdalenosti[pozice_nejmensiho-1])
                vzdalenost2 = str(vzdalenosti[pozice_nejmensiho])
                seznam_nejblizsich_restauraci.append(
                    vzdalenosti[pozice_nejmensiho-1])
                seznam_nejblizsich_restauraci.append(
                    vzdalenosti[pozice_nejmensiho])
                cisla_vzdalenosti.pop(index_nejmensiho)
    
                if cisla_vzdalenosti:
    
                    nejmensi = min(cisla_vzdalenosti)
                    pozice_nejmensiho = vzdalenosti.index(nejmensi)
                    index_nejmensiho = cisla_vzdalenosti.index(nejmensi)
                    #return("Třetí nejbližší restaurace je " + str(vzdalenosti[pozice_nejmensiho-1]) + ". " + "Vzdálenost: " + str(vzdalenosti[pozice_nejmensiho]) + "m.")  # jméno restaurace je vždycky nalevo
                    restaurace3 = str(vzdalenosti[pozice_nejmensiho-1])
                    vzdalenost3 = str(vzdalenosti[pozice_nejmensiho])
                    seznam_nejblizsich_restauraci.append(
                        vzdalenosti[pozice_nejmensiho-1])
                    seznam_nejblizsich_restauraci.append(
                        vzdalenosti[pozice_nejmensiho])
                else:
                    
                    return( "Vámi hledané jídlo se nachází jen v těchto dvou restauracích.")
    
            else:
                
                return("Vámi hledané jídlo se nacházi jen v této restauraci.")
        else:
            return(
                "Lituji, ale v daném městě / městské části není dnes v menu vámi hledané jídlo.")
            #return render_template('result.html',form_data = form_data)
        #def plpl():
        #    a = 2
        #    return("fefef" + str(a))

        
        #return(print_restaurace_vzdalenosti(cisla_vzdalenosti, vzdalenosti))
        #return("restaurace1 " + str(type(restaurace1)) + " " + restaurace1)  
        #return (str(restaurace1))
        #return  '{} {}'.format(restaurace1, vzdalenost1)
        return render_template('result.html', hledane_jidlo=hledane_jidlo, restaurace1 = restaurace1, vzdalenost1 = vzdalenost1
        ,restaurace2 = restaurace2, vzdalenost2 = vzdalenost2, restaurace3 = restaurace3, vzdalenost3 = vzdalenost3)
        return("plpl")
        #return render_template('result.html',form_data = form_data)
    
        
if __name__ == "main":          
    app.run(debug=True)
