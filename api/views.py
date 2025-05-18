from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.shortcuts import render
import folium
from folium.plugins import MarkerCluster
import random
import requests

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def hello_api(request):
    return Response({
        "message": "Hello from API!",
        "status": "success"
    })




@api_view(['GET'])
def simple_map(request):

    PALETTE = [
        "#FF0000",  # Rouge
        "#00FF00",  # Vert
        "#0000FF",  # Bleu
        "#FFFF00",  # Jaune
        "#FFA500",  # Orange
        "#FF00FF",  # Magenta (ou Fuchsia)
        "#800080",  # Violet
    ]

    # Appeler le microservice ORS via HTTP
    ors_service_url = 'http://orsservice:80/api/v1/directions'  # URL interne de ton microservice ORS
    params = {
        'start': '6.1725,1.2314',
        'end': '6.1865,1.2200',
        'alternatives': 3
    }

    my_position= {
        "lat":6.1319 ,
        "lng":1.2221
    }

    try:
        response = requests.get(ors_service_url, params=params)
        routes = response.json()['routes']
    except Exception as e:
        return render(request, 'maps/map.html', {'map': f"<p>Erreur : {e}</p>"})

    # Créer la carte
    m = folium.Map(location=[6.18, 1.225], zoom_start=14)

    # Ajouter les itinéraires
    for i, route in enumerate(routes):
        coords = route['coordinates']
        color = random.choice(PALETTE)
        folium.PolyLine(coords, color=random.choice(PALETTE), weight=4, opacity=0.7,
                        tooltip=f"Itinéraire {i+1}").add_to(m)
        # folium.PolyLine(coords, color=f"#{random.randint(0, 0xFFFFFF):06x}", weight=4, opacity=0.7,
                        # tooltip=f"Itinéraire {i+1}").add_to(m)
       

    # Ajouter les points
    folium.Marker([6.1725, 1.2314], tooltip="Départ", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([6.1865, 1.2200], tooltip="Arrivée", icon=folium.Icon(color='red')).add_to(m)

    # Définir les coordonnées de la zone à éviter (polygone)
    # Définir les coordonnées des 3 zones à éviter (polygones)
    avoid_zones = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Zone 1 à éviter"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1.2245, 6.1684],
                            [1.2265, 6.1684],
                            [1.2265, 6.1696],
                            [1.2245, 6.1696],
                            [1.2245, 6.1684]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Zone 2 à éviter"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1.2180, 6.1811],
                            [1.2190, 6.1811],
                            [1.2190, 6.1822],
                            [1.2180, 6.1822],
                            [1.2180, 6.1811]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Zone 3 à éviter"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1.2290, 6.1730],
                            [1.2310, 6.1730],
                            [1.2310, 6.1760],
                            [1.2290, 6.1760],
                            [1.2290, 6.1730]
                        ]
                    ]
                }
            }
        ]
    }

    # Ajouter le polygone à la carte avec folium.GeoJson
    folium.GeoJson(avoid_zones, 
        name="Zones à éviter",
        style_function=lambda x: {
            'fillColor': '#ff0000',
            'color': '#ff0000',
            'weight': 2,
            'fillOpacity': 0.3
        }).add_to(m)



    map_html = m._repr_html_()
    return render(request, 'maps/map.html', {'map': map_html})


@api_view(['GET'])
def map_direction(request):
    
    default_coord_start = 6.1725,1.2314
    default_coord_end = 6.1865,1.2200
    # Récupérer les paramètres query dans l'URL
    coord_start = str(request.GET.get('start',default_coord_start)  )
    coord_end = str(request.GET.get('end',default_coord_end)  )
    alternatives = int(request.GET.get('alternatives', 3) ) 
    
    
    # ORS attend des coordonnées au format (lng, lat)
    #transforme les données de la requete en coordonnée
    latA, lonA = map(float, coord_start.split(","))
    latB, lonB = map(float, coord_end.split(","))
    # coords = [(lonA, latA), (lonB, latB)]


    PALETTE = [
        "#FF0000",  # Rouge
        "#150B73",  # bleu1
        "#0000FF",  # Bleu
        "#FF00FF",  # Magenta (ou Fuchsia)
        "#800080",  # Violet
    ]

    
    try:
        # Appeler le microservice ORS via HTTP
        ors_service_url = 'http://orsservice:80/api/v1/directions'  # URL interne de ton microservice ORS
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]

        # Préparer l'en-tête pour la requête vers l'API ORS
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        params = {
            'start': coord_start,
            'end': coord_end,
            'alternatives': 3
        }

        response = requests.get(ors_service_url, params=params ,headers = headers)
        routes = response.json()['routes']
        # Recuperer les coordonnées de la zone (polygone) à éviter
        avoid_zones = response.json()['avoid_polygons']
        
    except Exception as e:
        return render(request, 'maps/map.html', {'map': f"<p>Erreur : {e}</p>"})

    # Créer la carte
    m = folium.Map(location=[latA, lonA], zoom_start=14)

    # Ajouter les itinéraires
    for i, route in enumerate(routes):
        coords = route['coordinates']
        color = random.choice(PALETTE)
        folium.PolyLine(coords, color=random.choice(PALETTE), weight=4, opacity=0.7,
                        tooltip=f"Itinéraire {i+1}").add_to(m)
        # folium.PolyLine(coords, color=f"#{random.randint(0, 0xFFFFFF):06x}", weight=4, opacity=0.7,
                        # tooltip=f"Itinéraire {i+1}").add_to(m)
       

    # Ajouter les points
    folium.Marker([latA, lonA], tooltip="Départ", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([latB, lonB], tooltip="Arrivée", icon=folium.Icon(color='red')).add_to(m)

    # # Ajouter un cluster de marqueurs pour les incidents
    # marker_cluster = MarkerCluster().add_to(m)
    # # Ajouter un marqueur pour chaque incident proche
    # for issue in nearby_issues:
        
    #     folium.Marker(
    #         location=[issue["latitude"], issue["longitude"]],
    #         popup=f"ID: {issue['id']}<br>{issue['description']}",
    #         icon=folium.Icon(color='blue', icon='info-sign')
    #     ).add_to(marker_cluster)
        
        
    # Ajouter le polygone à la carte avec folium.GeoJson
    folium.GeoJson(avoid_zones, 
        name="Zones à éviter",
        style_function=lambda x: {
            'fillColor': '#ff0000',
            'color': '#ff0000',
            'weight': 2,
            'fillOpacity': 0.3
        }).add_to(m)

    # folium.Polygon(
    #     locations=polygon_coords,
    #     color='red',
    #     fill=True,
    #     fill_opacity=0.4
    #     popup="Zone 1 à éviter",      # Affiché au clic
    #     tooltip="Zone 1 à éviter"     # Affiché au survol
    # ).add_to(m)


    map_html = m._repr_html_()
    return render(request, 'maps/map.html', {'map': map_html})



@api_view(['GET'])
def map_with_road_issues_around(request):
    point_A = [6.1751,1.2123]   # Lomé - [latitude, longitude]
    center_lat = point_A[0]
    center_lon = point_A[1]
    
     # Récupérer les paramètres query dans l'URL
    lat = float(request.GET.get('lat',center_lat)  )
    lng = float(request.GET.get('lng',center_lon)  )
    radius = int(request.GET.get('radius', 2000) ) 
    
    
    
    # Carte autour de A 
    m = folium.Map(location=[lat, lng], zoom_start=14)
    
    # Ajouter un cluster de marqueurs pour les incidents
    marker_cluster = MarkerCluster().add_to(m)

    # Marqueurs
    folium.Marker(
        [lat, lng],
        tooltip="Départ - Salon",
        popup="Bienvenue à Lomé",
        icon=folium.Icon(color='green')
    ).add_to(m)

  
    # Récupération de tous les incidents routiers a proximité d'un point
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]

        # Préparer l'en-tête pour la requête vers l'API ORS
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        # Appeler le microservice ORS via HTTP
        params = {
            'lat': lat,
            'lng': lng,
            'radius': radius 
        }   
        print("Réponse ORS fhtjkyoyiytioyuopuouyity:")
        response = requests.get('http://orsservice:80/api/v1/road-issues', params=params, headers = headers) 
        
          # Debug : affiche la réponse JSON dans les logs
        print("Réponse ORS :", response.json())
        nearby_issues= response.json()['data']
    except Exception as e:
        return render(request, 'maps/map.html', {'map': f"<p>Erreur : {e}</p>"})
        # raise HTTPException(status_code=500, detail=f"Erreur ORS : {str(e)}")
   
    print(nearby_issues) 
    # Ajouter un marqueur pour chaque incident proche
    for issue in nearby_issues:
        
        folium.Marker(
            location=[issue["latitude"], issue["longitude"]],
            popup=f"ID: {issue['id']}<br>{issue['description']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    # Générer HTML dans une variable
    map_html = m._repr_html_()

    return render(request, 'maps/map.html', {'map': map_html})

@api_view(['GET'])
def map_showing_zone(request):

    # Appeler le microservice ORS via HTTP
    ors_service_url = 'http://orsservice:80/api/v1/directions'  # URL interne de ton microservice ORS
    params = {
        'start': '6.1725,1.2314',
        'end': '6.1865,1.2200',
        'alternatives': 3
    }

    PALETTE = [
        "#FF0000",  # Rouge
        "#00FF00",  # Vert
        "#0000FF",  # Bleu
        "#FFFF00",  # Jaune
        "#FFA500",  # Orange
        "#FF00FF",  # Magenta (ou Fuchsia)
        "#800080",  # Violet
    ]
    try:
        response = requests.get(ors_service_url, params=params)
        routes = response.json()['routes']
    except Exception as e:
        return render(request, 'maps/map.html', {'map': f"<p>Erreur : {e}</p>"})

    # Créer la carte
    m = folium.Map(location=[6.18, 1.225], zoom_start=14)

    # Ajouter les itinéraires
    for i, route in enumerate(routes):
        coords = route['coordinates']
        color = random.choice(PALETTE)
        folium.PolyLine(coords, color=random.choice(PALETTE), weight=4, opacity=0.7,
                        tooltip=f"Itinéraire {i+1}").add_to(m)
        # folium.PolyLine(coords, color=f"#{random.randint(0, 0xFFFFFF):06x}", weight=4, opacity=0.7,
                        # tooltip=f"Itinéraire {i+1}").add_to(m)
       

    # Ajouter les points
    folium.Marker([6.1725, 1.2314], tooltip="Départ", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([6.1865, 1.2200], tooltip="Arrivée", icon=folium.Icon(color='red')).add_to(m)

    # Définir les coordonnées de la zone à éviter (polygone)
    # Définir les coordonnées des 3 zones à éviter (polygones)
    avoid_zones = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Zone 1 à éviter"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1.2245, 6.1684],
                            [1.2265, 6.1684],
                            [1.2265, 6.1696],
                            [1.2245, 6.1696],
                            [1.2245, 6.1684]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Zone 2 à éviter"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1.2180, 6.1811],
                            [1.2190, 6.1811],
                            [1.2190, 6.1822],
                            [1.2180, 6.1822],
                            [1.2180, 6.1811]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "Zone 3 à éviter"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [1.2290, 6.1730],
                            [1.2310, 6.1730],
                            [1.2310, 6.1760],
                            [1.2290, 6.1760],
                            [1.2290, 6.1730]
                        ]
                    ]
                }
            }
        ]
    }

    # Ajouter le polygone à la carte avec folium.GeoJson
    folium.GeoJson(avoid_zones, 
        name="Zones à éviter",
        style_function=lambda x: {
            'fillColor': '#ff0000',
            'color': '#ff0000',
            'weight': 2,
            'fillOpacity': 0.3
        }).add_to(m)



    map_html = m._repr_html_()
    return render(request, 'maps/map.html', {'map': map_html})