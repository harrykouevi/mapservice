from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.shortcuts import render
import folium
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
    # Appeler le microservice ORS via HTTP
    ors_service_url = 'http://orsservice:80/api/v1/route'  # URL interne de ton microservice ORS
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



@api_view(['GET'])
def simple_mapi(request):
      # Points A et B
    point_A = [6.1725, 1.2314]  # Lomé - salon
    point_B = [6.1865, 1.2200]  # Ex : Marché d’Adawlato

    # Carte centrée entre A et B
    center_lat = (point_A[0] + point_B[0]) / 2
    center_lon = (point_A[1] + point_B[1]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Marqueurs
    folium.Marker(
        point_A,
        tooltip="Départ - Salon",
        popup="Bienvenue à Lomé",
        icon=folium.Icon(color='green')
    ).add_to(m)

    folium.Marker(
        point_B,
        tooltip="Arrivée",
        popup="Marché d’Adawlato",
        icon=folium.Icon(color='red')
    ).add_to(m)

    # Générer 5 itinéraires simulés
    for i in range(5):
        route = [point_A]
        for j in range(3):  # 3 points intermédiaires
            lat = point_A[0] + (point_B[0] - point_A[0]) * (j+1)/4 + random.uniform(-0.0015, 0.0015)
            lon = point_A[1] + (point_B[1] - point_A[1]) * (j+1)/4 + random.uniform(-0.0015, 0.0015)
            route.append([lat, lon])
        route.append(point_B)

        folium.PolyLine(
            route,
            color=f"#{random.randint(0, 0xFFFFFF):06x}",
            weight=4,
            opacity=0.8,
            tooltip=f"Itinéraire {i+1}"
        ).add_to(m)


    # Générer HTML dans une variable
    map_html = m._repr_html_()

    return render(request, 'maps/map.html', {'map': map_html})
