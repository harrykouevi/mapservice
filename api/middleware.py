import requests
from django.http import JsonResponse
from django.urls import resolve

class BearerTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Liste des noms de vues protégées (définis dans urls.py)
        self.protected_views = [
            # "map_with_road_issues_around",
           
            # etc.
        ]

        # URL de vérification du token dans le microservice
        # self.auth_check_url = os.getenv("MICRO_SERVICE_AUTH_URL") + "/api/check-token"
        self.auth_check_url = "http://user-service" + "/api/check-token"

    def __call__(self, request):
        resolved_view = resolve(request.path_info)

        if resolved_view.url_name in self.protected_views:
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'detail': 'Token manquant ou invalide.'}, status=401)

            token = auth_header.split(' ')[1]

            try:
                # Requête vers le microservice pour vérifier le token
                response = requests.get(
                    self.auth_check_url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    },
                    timeout=5
                )

                if response.status_code != 200:
                    return JsonResponse({'detail': 'Token invalide ou expiré.'}, status=403)

            except requests.RequestException:
                return JsonResponse({'detail': 'Erreur de connexion au service d\'authentification.'}, status=500)

        return self.get_response(request)
