from datetime import datetime
import io
import csv

from django.core.files.base import ContentFile
from django.http.response import HttpResponseRedirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, View

import petl as etl

from apiclient.clients import PeopleAPIClient, PlanetsAPIClient
from .models import Collection


class CollectionListView(ListView):
    model = Collection
    context_object_name = 'collections'


class NewCollectionView(View):
    def get(self, request):
        characters_header = [
            'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year', 'gender', 'homeworld', 'date',
        ]
        characters = [
            characters_header,
        ]

        planets_cache = {

        }
        
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
        Collection().csv_file.save(collection_name, ContentFile(csv_output.getvalue()))

        return HttpResponseRedirect(reverse('characters:homepage'))
