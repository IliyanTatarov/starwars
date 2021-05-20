from datetime import datetime
import csv
import io

import petl as etl

from apiclient.clients import PeopleAPIClient, PlanetsAPIClient


def get_character_table(csv_path):
    character_table = etl.fromcsv(csv_path)
    headers = etl.header(character_table)
    total_characters = len(character_table)

    return character_table, headers, total_characters


def aggregate_character_table(csv_path, filters):
    if len(filters) == 1:
        filters = filters[0]

    character_table, headers, total_characters = get_character_table(csv_path)
    data = etl.data(etl.aggregate(character_table, key=filters, aggregation=len))

    return headers, data, total_characters


def paginate_character_table(csv_path, page):
    character_table, headers, total_characters = get_character_table(csv_path)
    data = etl.data(etl.rowslice(character_table, 10 * (page - 1), 9 + 10 * (page - 1)))

    return headers, data, total_characters


def fetch_character_data():
    characters_header = [
        'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender', 'homeworld', 'date',
    ]
    characters = [
        characters_header,
    ]

    planets_cache = {}

    people_client = PeopleAPIClient()
    planets_client = PlanetsAPIClient()

    page = 1
    while True:
        response = people_client.get_people({'page': page})

        if 'results' in response and len(response['results']) > 0:
            for result in response['results']:
                character = list()

                for header in characters_header:
                    if header in ['height', 'mass']:
                        try:
                            character.append(int(result[header].replace(',', '')))
                        except:
                            character.append(result[header])
                    elif header == 'homeworld':
                        planet_id = result['homeworld'].split('/')[-2]
                        if planet_id in planets_cache:
                            planet_name = planets_cache[planet_id]
                        else:
                            planet_name = planets_client.get_item(int(planet_id))['name']
                            planets_cache[planet_id] = planet_name
                        character.append(planet_name)

                    elif header == 'date':
                        character.append(result['edited'])

                    else:
                        character.append(result[header])

                characters.append(character)

        else:
            break

        page += 1
        if not response['next']:
            break

    character_table = etl.wrap(characters)
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerows(character_table)

    collection_name = f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}.csv'

    return collection_name, csv_output
