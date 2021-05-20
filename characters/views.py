from datetime import datetime
import io
import csv

from django.core.files.base import ContentFile
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.views.generic import DetailView, ListView, View

import petl as etl

from apiclient.clients import PeopleAPIClient, PlanetsAPIClient
from .models import Collection


class CollectionListView(ListView):
    model = Collection
    context_object_name = 'collections'


class CollectionDetailView(DetailView):
    model = Collection
    context_object_name = 'collection'

    def get(self, request, pk):
        response = super().get(request, pk)
        if 'HTTP_X_REQUESTED_WITH' in request.META and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            template = loader.get_template('characters/collection_detail_table.html')
            template_render = template.render(response.context_data)
            data = {
                'html': template_render,
                'more': response.context_data['more'],
            }
            return JsonResponse(data)
        else:
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character_table = etl.fromcsv(self.get_object().csv_file.path)

        context['headers'] = etl.header(character_table)
        context['headers_all'] = context['headers']

        page = int(self.request.GET.get('page', '1'))
        data = etl.rowslice(character_table, 10 * (page - 1), 9 + 10 * (page - 1))
        data = etl.data(data)

        context['more'] = True
        if len(character_table) < page * 10:
            context['more'] = False

        context['content'] = list(data)

        return context


class CollectionAggregateView(DetailView):
    model = Collection
    context_object_name = 'collection'

    def get(self, request, pk):
        filters = self.request.GET.getlist('filters[]')
        if len(filters) < 1:
            return HttpResponseRedirect(reverse('characters:collection', kwargs={'pk': pk}))
        else:
            return super().get(request, pk)

    def get_context_data(self, **kwargs):
        filters = self.request.GET.getlist('filters[]')

        context = super().get_context_data(**kwargs)
        character_table = etl.fromcsv(self.get_object().csv_file.path)

        context['headers'] = filters
        context['headers_all'] = etl.header(character_table)

        if len(filters) == 1:
            filters = filters[0]
        context['content'] = list(etl.data(etl.aggregate(character_table, key=filters, aggregation=len)))
        context['count'] = True

        return context


class CollectionNewView(View):
    def get(self, request):
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
        Collection().csv_file.save(collection_name, ContentFile(csv_output.getvalue()))

        return HttpResponseRedirect(reverse('characters:homepage'))
