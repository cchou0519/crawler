import pygsheets

gc = pygsheets.authorize(service_account_file='config/google-sheet-key.json')

survey_url = 'https://docs.google.com/spreadsheets/d/1LBhE66v6AJnsN4PtmdAiM2X6TMyK1yYyrefF0oqlOiU/edit#gid=1745896057'
sh = gc.open_by_url(survey_url)
wks2 = sh.worksheet_by_title("豪豪的特別條件區")
c = wks2.get_as_df([["ID", "4*"]]).astype('str')

tracker = list(c["ID"].loc[c['4*'].str.contains('X')])


print(tracker)
print(len(tracker))