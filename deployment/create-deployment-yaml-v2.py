

place_name = "HC"
zoom_out_times = 3
is_100 = False
is_pvp = True

with open("deployment-template.yaml") as f:
    contents = f.read()
    contents = contents.replace("<place_name>", place_name)\
        .replace("<zoom_out_times>", str(zoom_out_times))\
        .replace("<is_100>", str(is_100)).replace("<is_pvp>", str(is_pvp))


with open("deployment-" + place_name + ".yaml", mode="w") as f:
    f.write(contents)


