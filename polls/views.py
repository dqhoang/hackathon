import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
import feedparser
import requests
import os

from .models import Question, Choice


# Create your views here.

class IndexView(generic.ListView):
    """docstring for IndexView"""
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions"""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': "You fucked up"
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args(p.id, )))


def FeedsView(request):
    catalog = "https://greengov.data.ca.gov/catalog.rss"
    feed = feedparser.parse(catalog)
    items = [{
                 'resource': x['link'].rpartition('/')[2],
                 'link': "https://greengov.data.ca.gov/resource/{0}.json".format(x['link'].rpartition('/')[2])}
             for x in feed['entries']]
    for row in feed['entries']:
        resource = row['link'].rpartition('/')[2]
        link = "https://greengov.data.ca.gov/resource/{0}.json".format(resource)
        myFile = open('{0}.json'.format(resource), 'w')
        response = requests.get(link, headers={'X-App-Token': 'eZ54Yp2ubYQAEO2IvzxR7pPQu'})

    return HttpResponse(items)


def getList(request):
    objects = [dict(file=f) for f in os.listdir('polls/dump/')]

    return HttpResponse(json.dumps(objects), content_type='application/json')

def getData(request, resource):
    f = open('polls/dump/{0}.json'.format(resource), 'r')
    data = json.loads(f.read())
    return HttpResponse(json.dumps(data))
