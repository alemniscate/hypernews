from django.shortcuts import render
from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import redirect
from hypernews.settings import NEWS_JSON_PATH
from django.views.decorators.csrf import csrf_exempt
import os
import json
import random
import datetime
import re

def get_linklist():
    with open(NEWS_JSON_PATH) as json_file:
        news_list = json.load(json_file)

    link_list = [news["link"] for news in news_list]        
    return link_list

def get_newsdata(id):
    with open(NEWS_JSON_PATH) as json_file:
        news_list = json.load(json_file)

    link = '<a target="_blank" target="_blank" href="/news/">news</a>'
    for news in news_list:
        if news["link"] == int(id):
            text = f"<h2>{news['title']}</h2>"
            text += f"<p>{news['created']}</p>"
            text += f"<p>{news['text']}</p>"
            text += link
            return text

    return None

def get_date(news):
    created = news["created"].split()
    return created[0]

def get_newslist(restrict_title):
    print(os.path.abspath(NEWS_JSON_PATH))
    with open(NEWS_JSON_PATH) as json_file:
        news_list = json.load(json_file)
    
    news_list.sort(key=lambda s: s["created"], reverse=True)
    news_dict = {}
    i = 0
    while i < len(news_list):
        date_key = get_date(news_list[i])
        date_value = []
        while i < len(news_list) and date_key == get_date(news_list[i]):
            news = news_list[i]
            article_dict = {}
            article_dict["title"] = news["title"]
            article_dict["text"] = news["text"]
            article_dict["link"] = "/news/" + str(news["link"]) + "/"
            if not restrict_title or re.search(restrict_title, news["title"]): 
                date_value.append(article_dict)
            i += 1
        if date_value:    
            news_dict[date_key] = date_value
    
    return news_dict

class MaintenanceView(View):
    def get(self, request, *args, **kwargs):
        return redirect("/news/")

class NewsPageView(View):  
    def get(self, request, *args, **kwargs):
        id = kwargs["id"] 
        text = get_newsdata(id)           
        return HttpResponse(text)

class NewsView(View):  
    def get(self, request, *args, **kwargs):
        try:
            title = request.GET["q"]
        except:
            title = None
        print(title) 
        news_dict = get_newslist(title)  
        return render(request, "news.html", {'news_dict': news_dict})
 
    def search_title(self, title):
        with open(NEWS_JSON_PATH) as json_file:
            news_list = json.load(json_file)

        for news in news_list:
            if news["title"] == title:
                return news["link"]

        return None

class NewsCreateView(View):
    def post(self, request, *args, **kwargs):
        title = request.POST["title"]
        text = request.POST["text"]
        link = self.get_newlink()
        date = self.get_today()
        self.add_news(date, title, text, link)
        return redirect("/news/")

    def get(self, request, *args, **kwargs):
        return render(request, 'create.html')

    def get_newlink(self):
        linklist = get_linklist()
        num = random.randint(1, 100_000_000)
        while num in linklist:
            num = random.randint(1, 100_000_000)
        return num

    def get_today(self):
        dt = datetime.datetime.now()
        return f"{dt.year}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02}:{dt.second:02}"

    def add_news(self, date, title, text, link):
        news = {}
        news["created"] = date
        news["title"] = title
        news["text"] = text
        news["link"] = link

        with open(NEWS_JSON_PATH) as json_file:
            news_list = json.load(json_file)

        news_list.append(news)

        with open(NEWS_JSON_PATH, 'w') as json_file:
            json.dump(news_list, json_file, indent=4)