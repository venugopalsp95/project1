from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from . import util
import random
from markdown2 import Markdown
from django.urls import reverse
markdowner = Markdown()


class Post(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(
        attrs={'placeholder': 'Enter title'}))
    text = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'height:400px'}), label='')


class Edit(forms.Form):
    text = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'height:400px'}), label='')


class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Search Wiki', 'style': 'width: 100 %'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })


def entry(request, title):
    entries = util.list_entries()
    if title in entries:
        page = util.get_entry(title)
        page_converted = markdowner.convert(page)
        context = {
            'page': page_converted,
            'title': title,
            'form': SearchForm()
        }
        return render(request, "encyclopedia/entry.html", context)
    else:
        return render(request, "encyclopedia/error.html", {"msg": "The requested page was not found", "form": SearchForm()})


def search(request):
    if request.method == "POST":
        entries = util.list_entries()
        entries_found = []
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            for entry in entries:
                if query.lower() == entry.lower():
                    title = entry
                    entry = util.get_entry(title)
                    return HttpResponseRedirect(reverse("entry", args=[title]))
                if query.lower() in entry.lower():
                    entries_found.append(entry)
            return render(request, "encyclopedia/search.html", {
                "results": entries_found,
                "query": query,
                "form": SearchForm()

            })
    return render(request, "encyclopedia/search.html", {
        "results": "",
        "query": "",
        "form": SearchForm()
    })


def create(request):
    if request.method == 'POST':
        form = Post(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
            entries = util.list_entries()
            if title in entries:
                return render(request, "encyclopedia/error.html", {"form": SearchForm(), "msg": "Page already exist"})
            else:
                util.save_entry(title, text)
                page = util.get_entry(title)
                page_converted = markdowner.convert(page)
                context = {
                    'form': SearchForm(),
                    'page': page_converted,
                    'title': title
                }
                return render(request, "encyclopedia/entry.html", context)

    else:
        return render(request, "encyclopedia/create.html", {"form": SearchForm(), "post": Post()})


def edit(request, title):
    if request.method == 'GET':
        page = util.get_entry(title)
        context = {
            'form': SearchForm(),
            'edit': Edit(initial={'text': page}),
            'title': title
        }
        return render(request, "encyclopedia/edit.html", context)
    else:
        form = Edit(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            util.save_entry(title, text)
            page = util.get_entry(title)
            page_converted = markdowner.convert(page)
            context = {
                'form': SearchForm(),
                'page': page_converted,
                'title': title
            }
            return render(request, "encyclopedia/entry.html", context)


def randomPage(request):
    if request.method == 'GET':
        entries = util.list_entries()
        num = random.randint(0, len(entries)-1)
        page_random = entries[num]
        page = util.get_entry(page_random)
        page_converted = markdowner.convert(page)
        context = {
            'form': SearchForm(),
            'page': page_converted,
            'title': page_random
        }
        return render(request, "encyclopedia/entry.html", context)
