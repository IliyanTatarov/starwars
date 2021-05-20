from django.core.files.base import ContentFile
from django.http.response import HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.views.generic import DetailView, ListView, View

from .models import Collection
from .services import aggregate_character_table, paginate_character_table, fetch_character_data


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
        csv_path = self.get_object().csv_file.path
        page = int(self.request.GET.get('page', '1'))
        
        headers, characters_data, total_characters = paginate_character_table(csv_path, page)

        context['headers'] = headers
        context['headers_all'] = headers

        context['more'] = True
        if total_characters < page * 10:
            context['more'] = False

        context['content'] = list(characters_data)

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
        context = super().get_context_data(**kwargs)
        csv_path = self.get_object().csv_file.path
        filters = self.request.GET.getlist('filters[]')

        headers, characters_data, _ = aggregate_character_table(csv_path, filters)

        context['headers'] = filters
        context['headers_all'] = headers
        context['content'] = characters_data
        context['count'] = True

        return context


class CollectionNewView(View):
    def get(self, request):
        collection_name, csv_output = fetch_character_data()
        Collection().csv_file.save(collection_name, ContentFile(csv_output.getvalue()))

        return HttpResponseRedirect(reverse('characters:homepage'))
