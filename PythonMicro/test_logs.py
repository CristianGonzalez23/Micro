import time
import requests
import pytest

ELASTICSEARCH_URL = "http://elasticsearch:9200"

def wait_for_elasticsearch(timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(ELASTICSEARCH_URL)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

@pytest.fixture(scope="module", autouse=True)
def setup():
    # Esperar hasta que Elasticsearch esté listo
    assert wait_for_elasticsearch(), "Elasticsearch no está listo"

def test_log_creation():
    # Aquí va el código para crear un log en Elasticsearch

    # Verificar que el log se haya registrado en Elasticsearch
    es_response = requests.get(ELASTICSEARCH_URL + "/_search")
    assert es_response.status_code == 200
    logs = es_response.json()["hits"]["hits"]
    assert len(logs) > 0, "No se encontraron logs en Elasticsearch"

    # Verificar que el log contenga la información esperada
    log_message = logs[0]["_source"]["message"]
    assert "Aplicación iniciada" in log_message, "El log no contiene el mensaje esperado"