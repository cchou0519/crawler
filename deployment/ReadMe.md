# Usage 

## create deployment yaml
```
python create-deployment-yaml-v2.py --place_name HC --zoom_out_times 4 --is_pvp true --is_100 false
```
return 
"create deployment-hc-pvp.yaml successful"

## deploy yaml
```
kubectl apply -f deployment-hc-pvp.yaml
```

