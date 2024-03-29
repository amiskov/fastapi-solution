import json
import pathlib

import requests
from jsonschema import validate
from jsonschema.validators import RefResolver

films_url = 'http://localhost:8000/api/v1/films'
film_id = 'e4f1672d-329d-4167-86e0-28f459aff68f'


def validate_payload(payload: str, schema_name: str) -> None:
    """
    Validate payload with selected schema.
    """
    schemas_dir = str(
        f'{pathlib.Path(__file__).parent.absolute()}/schemas',
    )
    schema = json.loads(
        pathlib.Path(f'{schemas_dir}/{schema_name}').read_text())
    validate(
        payload,
        schema,
        resolver=RefResolver(
            'file://' + str(
                pathlib.Path(f'{schemas_dir}/{schema_name}').absolute()),
            schema,  # it's used to resolve the file inside schemas correctly
        ),
    )


def test_film_details_endpoint() -> None:
    """Tests film details endpoint."""
    response = requests.get(films_url + '/' + film_id)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    validate_payload(response.json(), 'film.json')


def test_films_endpoint() -> None:
    """Tests film list endpoint."""
    response = requests.get(films_url)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    validate_payload(response.json(), 'films.json')
