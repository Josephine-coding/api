# API : Authentification, Docker et Monitoring


Simple api qui renvoie le sentiment d'une phrase envoyée, avec mise en place de l'authentification (tuto Fastapi), de Docker et de monitoring (opentelemetry, jaeger et grafana)

```
    ├── app                    # Contains the api
    ├── database               # Contains the database
    ├── schemas                # Contains the pydantic models needed for the API
    ├── utils                  # Contains the fonctions
    └── Dockerfile             # To build the docker image
```
