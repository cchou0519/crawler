import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


df = pd.read_csv("config/pm_list.csv", header=0, usecols=[2, 3])
# print(df)
trans_dict = df.set_index('英文').T.to_dict('index')['名稱']

area_dict = {
    "Kantonian": "關都",
    "Alolan": "阿羅拉",
    "Hisuian": "洗翠",
    "Galarian": "伽勒爾",
    "Johtonian": "城都",
    "Unovan": "合眾"
}

# print(eng)

# _str = "Bulbasaur"
_str = "Glastrier"
rep = trans_dict[_str] if _str in trans_dict else _str
# trantab = str.maketrans(eng, cht)
#
# print(_str.translate(trantab))


res = requests.get('https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_evolution_family')
# print(res.text)

soup = BeautifulSoup(res.text, "html.parser")

# print(soup.prettify())
soup_tables = soup.select('table.roundy tbody')
families = []

for soup_table in soup_tables:

    tr_list = soup_table.select('tr')

    for tr in tr_list:
        td_list = tr.select('td')
        # print("---")
        family = []
        for td in td_list:
            a = td.find_all('a', title=re.compile("\(Pokémon\)"))
            if len(a) > 0:
                pokemon_eng = a[0].select("span")[0].text
                pokemon_cht = trans_dict[pokemon_eng] if pokemon_eng in trans_dict else pokemon_eng

                _split = pokemon_cht.split("(")
                if len(_split) > 1:
                    print(len(_split), _split)
                    pm_name = _split[0].strip()
                    pokemon_cht = trans_dict[pm_name] if pm_name in trans_dict else pm_name

                    area_eng = _split[1][:-1]
                    area = area_dict[area_eng] if area_eng in  area_dict else area_eng
                    pokemon_cht += "-" + area
                # print(pokemon)
                family.append(pokemon_cht)
        if len(family) > 0:
            families.append(family)

# print(families)
# print(len(families))

pd.DataFrame(families).to_csv("config/family.csv", header=None, index=False, encoding='utf-8-sig')


