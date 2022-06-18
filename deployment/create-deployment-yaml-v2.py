
place_name = "HC"
zoom_out_times = 4
is_100 = True
is_pvp = True

with open("deployment-template.yaml") as f:
    contents = f.read()
    contents = contents.replace("<place_name>", place_name)\
        .replace("<place_name_lower>", place_name.lower())\
        .replace("<zoom_out_times>", '"' + str(zoom_out_times) + '"')\
        .replace("<is_100>", '"' + str(is_100) + '"').replace("<is_pvp>", '"' + str(is_pvp) + '"')


with open("deployment-" + place_name.lower() + ".yaml", mode="w") as f:
    f.write(contents)



