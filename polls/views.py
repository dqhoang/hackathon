from django.http		import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts	import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views 		import generic

import feedparser
import json
from itertools import *
import urllib
import requests

from .models 			import Question, Choice

# Create your views here.

class IndexView(generic.ListView):
	"""docstring for IndexView"""
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'
	def get_queryset(self):
		"""Return the last five published questions"""
		return Question.objects.order_by('-pub_date')[:5]
		

#def index(request):
#	latest_question_list = Question.objects.order_by('-pub_date')[:5]
#	context = {'latest_question_list': latest_question_list}
#	return render(request, 'polls/index.html', context)
	#return HttpResponse("Hello, World. This is Polls Index")

#def detail(request, question_id):
## Proper Way:
#	try:
#		question = Question.objects.get(pk=question_id)
#	except Question.DoesNotExist:
#		raise Http404("Question does not exist")

## Shortcut:
#	question = get_object_or_404(Question, pk=question_id)
#	return render(request, 'polls/detail.html', {'question': question})
	#return HttpResponse("Youre looking at question %s." % question_id)

class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'

class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'

#def results(request, qquesiton_id):
#	response = "Youre looking at the results of question %s" 
#	return HttpResponse(response % question_id)

def vote(request, question_id):
	p = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = p.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		# Redisplay the question voting form
		return render(request, 'polls/detail.html', {
			'question':p,
			'error_message': "You fucked up"
			})
	else:
		selected_choice.votes += 1
		selected_choice.save()
		return HttpResponseRedirect(reverse('polls:results', args(p.id,)))


def FeedsView(request):
	catalog = "https://greengov.data.ca.gov/catalog.rss"
	feed = feedparser.parse( catalog )
	items = [{
		'resource' : x['link'].rpartition('/')[2],
		'link' : "https://greengov.data.ca.gov/resource/{0}.json".format(x['link'].rpartition('/')[2] )}
		for x in feed['entries']]
	f = open('dump.json', 'w')
	for row in feed['entries']:
		resource = row['link'].rpartition('/')[2]
		link = "https://greengov.data.ca.gov/resource/{0}.json".format(resource)	
		myFile = open('{0}.json'.format(resource), 'w')
		response = requests.get(link, headers={'X-App-Token':'eZ54Yp2ubYQAEO2IvzxR7pPQu'})

		myFile.write(json.dumps(response.json()))
		myFile.close()
		f.write("{0}\n".format(link))
	f.close()
	return HttpResponse(json.dumps(feed['entries']))
	