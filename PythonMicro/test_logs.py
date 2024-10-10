import pytest
import requests
import time

# URL de la aplicación Flask
BASE_URL = "http://localhost:5000"

# URL de Elasticsearch
ELASTICSEARCH_URL = "http://localhost:9200/app-logs-*/_search"

# Función para esperar hasta que Elasticsearch esté listo
def wait_for_elasticsearch(timeout=60, interval=5):
    for _ in range(timeout // interval):
        try:
            response = requests.get(ELASTICSEARCH_URL)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(interval)
    return False

@pytest.fixture(scope="module", autouse=True)
def setup():
    # Esperar hasta que Elasticsearch esté listo
    assert wait_for_elasticsearch(), "Elasticsearch no está listo"

def test_log_creation():
    # Enviar una solicitud a la aplicación Flask
    response = requests.get(f"{BASE_URL}/usuarios/")
    assert response.status_code == 200

    # Esperar un momento para que el log se registre en Elasticsearch
    time.sleep(2)

    # Verificar que el log se haya registrado en Elasticsearch
    es_response = requests.get(ELASTICSEARCH_URL)
    assert es_response.status_code == 200
    logs = es_response.json()["hits"]["hits"]
    assert len(logs) > 0, "No se encontraron logs en Elasticsearch"

    # Verificar que el log contenga la información esperada
    log_message = logs[0]["_source"]["message"]
    assert "Aplicación iniciada" in log_message, "El log no contiene el mensaje esperado"