from django.shortcuts import render_to_response, render
from article.models import Article
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.views.generic.base import TemplateView
from forms import ArticleForm
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from haystack.query import SearchQuerySet

from django.template import RequestContext
from django.contrib import messages

import logging
logr = logging.getLogger(__name__)

# Create your views here.

def hello(request):
	name = "Sujay"
	html = "<html><body>Hi %s, this seems to have worked!</body></html>" % name
	return HttpResponse(html)

def hello_template(request):
	name = "Sujay"
	t = get_template('hello.html')
	html = t.render(Context({'name': name}))
	return HttpResponse(html)

def hello_template_simple(request):
	name = "Sujay"
	return render_to_response('hello.html', {'name': name})

class HelloTemplate(TemplateView):
	template_name = 'hello_class.html'
	def get_context_data(self, **kwargs):
		context = super(HelloTemplate, self).get_context_data(**kwargs)
		context['name'] = 'Sujay'
		return context

def articles(request):
	language = 'en-IN'
	session_language = 'en-IN'

	if 'lang' in request.COOKIES:
		language = request.COOKIES['lang']

	if 'lang' in request.session:
		session_language = request.session['lang']

	args = {}
	args.update(csrf(request))

	args['articles'] = Article.objects.all()
	args['language'] = language
	args['session_language'] = session_language

	return render_to_response('articles.html', args)

def article(request, article_id=1):
	#return render_to_response('article.html',
	#						 {'article': Article.objects.get(id=article_id) },
	#						 context_instance=RequestContext(request))
	return render(request, 'article.html',
				 {'article': Article.objects.get(id=article_id) })

def language(request, language='en-IN'):
	response = HttpResponse("setting language to %s" % language)

	response.set_cookie('lang', language)

	request.session['lang'] = language

	return response

def create(request):
	if request.POST:
		form = ArticleForm(request.POST, request.FILES)
		if form.is_valid():
			a = form.save()

			messages.add_message(request, messages.SUCCESS, "Your Article was added")

			return HttpResponseRedirect('/articles/all')
	else:
		form = ArticleForm()

	args = {}
	args.update(csrf(request))

	args['form'] = form
	return render_to_response('create_article.html', args)

def delete_comment(request, comment_id):
	c = Comment.objects.get(id=comment_id)

	article_id = c.article.id

	c.delete()

	messages.add_message(request,
						 settings.DELETE_MESSAGE,
						 "Your comment was deleted")

	return HttpResponseRedirect("/article/get/%s" % article_id)

def like_article(request, article_id):
	if article_id:
		a = Article.objects.get(id=article_id)
		count = a.likes
		count += 1
		a.likes = count
		a.save()

	return HttpResponseRedirect('/articles/get/%s' % article_id)

def search_titles(request):
	#if request.method == "POST":
	#	search_text = request.POST['search_text']
	#else:
	#	search_text = ''

	#articles = Article.objects.filter(title__contains=search_text)

	articles = SearchQuerySet().autocomplete(content_auto=request.POST.get('search_text', ''))

	return render_to_response('ajax_search.html', {'articles': articles})