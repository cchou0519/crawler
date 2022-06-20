# Usage 

## create deployment yaml
```
python create-deployment-yaml-v2.py --place_name HC --zoom_out_times 4 --is_pvp true --is_100 false \
                                    --survey_url "https://docs.google.com/spreadsheets/d/1LBhE66v6AJnsN4PtmdAiM2X6TMyK1yYyrefF0oqlOiU/" \
                                    --work_sheet_name "豪豪的特別條件區2"
```
return 
"create deployment-hc-pvp.yaml successful"

## deploy yaml
```
kubectl apply -f deployment-hc-pvp.yaml
```

