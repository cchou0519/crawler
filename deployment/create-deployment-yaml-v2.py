import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser()
parser.add_argument("--place_name", help="input where, such as HC, TP, TC ...",
                    type=str)
parser.add_argument("--zoom_out_times", type=int)
parser.add_argument("--is_pvp", type=str2bool)
parser.add_argument("--is_100", type=str2bool)
parser.add_argument("--survey_url", type=str)
parser.add_argument("--work_sheet_name", type=str)


args = parser.parse_args()

place_name = args.place_name
zoom_out_times = args.zoom_out_times
is_100 = args.is_100
is_pvp = args.is_pvp
survey_url = args.survey_url
work_sheet_name = args.work_sheet_name

if is_100:
    tag_100 = "-100"
else:
    tag_100 = ""

if is_pvp:
    tag_pvp = "-pvp"
else:
    tag_pvp = ""

with open("deployment-template.yaml") as f:
    contents = f.read()
    contents = contents.replace("<place_name>", place_name)\
        .replace("<place_name_lower>", place_name.lower())\
        .replace("<zoom_out_times>", '"' + str(zoom_out_times) + '"')\
        .replace("<is_100>", '"' + str(is_100) + '"').replace("<is_pvp>", '"' + str(is_pvp) + '"')\
        .replace("<100_tag>", tag_100).replace("<pvp_tag>", tag_pvp)\
        .replace("<survey_url>", '"' + survey_url + '"').replace("<work_sheet_name>", '"' + work_sheet_name + '"')


with open("deployment-" + place_name.lower() + tag_100 + tag_pvp + ".yaml", mode="w") as f:
    f.write(contents)
    print("create", "deployment-" + place_name.lower() + tag_100 + tag_pvp + ".yaml", "successful")
