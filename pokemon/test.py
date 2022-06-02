import requests
from bs4 import BeautifulSoup
import re

res = requests.get('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_evolution_family')
# print(res.text)

soup = BeautifulSoup(res.text, "html.parser")

# print(soup.prettify())
soup_tables = soup.select('table.roundy tbody')
for soup_table in soup_tables:

    tr_list = soup_table.select('tr')
    print(len(tr_list))

    for tr in tr_list:
        td_list = tr.select('td')
        print("---")
        for td in td_list:
            a = td.find_all('a', title=re.compile("\(Pokémon\)"))
            if len(a) > 0:
                pokemon = a[0].select("span")[0].text
                print(pokemon)

            # if _t == "":
            #     a_list = td.select('a')
            #     for a in a_list:
            #         print(a["title"])
    breakpoint()

