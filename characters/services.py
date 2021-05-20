from datetime import datetime
import csv
import io

import petl as etl

from apiclient.clients import PeopleAPIClient, PlanetsAPIClient


def get_characters_table(csv_path):
    characters_table = etl.fromcsv(csv_path)
    headers = etl.header(characters_table)
    total_characters = len(characters_table)

    return characters_table, headers, total_characters


def aggregate_characters_table(csv_path, filters):
    if len(filters) == 1:
        filters = filters[0]

    characters_table, headers, total_characters = get_characters_table(csv_path)
    data = etl.data(etl.aggregate(characters_table, key=filters, aggregation=len))

    return headers, data, total_characters


def paginate_characters_table(csv_path, page):
    characters_table, headers, total_characters = get_characters_table(csv_path)
    data = etl.data(etl.rowslice(characters_table, 10 * (page - 1), 10 + 10 * (page - 1)))

    return headers, data, total_characters

def fetch_characters_data():
    people_client = PeopleAPIClient()

    characters_data = list()
    page = 1
    while True:
        response = people_client.get_people({'page': page})
        if 'results' in response and len(response['results']) > 0:
            characters_data += response['results']
        else:
            break
        
        page += 1
        if not response['next']:
            break
    
    return characters_data

def replace_homeworld_planet_name(characters_table):
    planets_client = PlanetsAPIClient()
    planets = {}
    
    homeworld_urls = set(characters_table['homeworld'])

    for homeworld_url in homeworld_urls:
        homeworld_id = homeworld_url.split('/')[-2]
        planets[homeworld_url] = planets_client.get_item(int(homeworld_id))['name']

    characters_table = etl.convert(characters_table, 'homeworld', lambda homeworld_url: planets[homeworld_url])    

    return characters_table


def get_table(characters_data):
    characters_headers = [
        'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender', 'homeworld', 'edited',
    ]
    characters_table = etl.fromdicts(characters_data, characters_headers)
    characters_table = etl.rename(characters_table, 'edited', 'date')
    characters_table = etl.convert(
        characters_table,
        'date',
        lambda date_field: datetime.strptime(date_field, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
    )
    
    characters_table = replace_homeworld_planet_name(characters_table)

    return characters_table

def fetch_characters_csv():
    characters_data = fetch_characters_data()       

    characters_table = get_table(characters_data)
    csv_output = io.StringIO(newline='')
    csv_writer = csv.writer(csv_output, lineterminator='\n')
    csv_writer.writerows(characters_table)

    collection_name = f'{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}.csv'

    return collection_name, csv_output
