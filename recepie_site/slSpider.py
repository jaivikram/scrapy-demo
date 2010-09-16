from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.item import Item, Field
import time
from scrapy.stats import stats
from scrapy.conf import settings
settings.overrides['CONCURRENT_REQUESTS_PER_SPIDER'] = 3
settings.overrides['WEBSERVICE_ENABLED'] = True
import re
import csv
recf = open('recepies.txt', 'w')

class MSSpider(CrawlSpider):
    name = "marthastewart.com"
    allowed_domains = [ "marthastewart.com"]
    attrs = {
        "name" : "//h1[@id='article_title']",
        "image" : "//div[@id='ms-col2-article-img-shadow-inner']/img",
        "short_description" : "//div[@id='article_short_description']/p",
        "prep_time" : "//div[@id='recipe_prep_time']/p",
        "serves" : "//div[@id='ms-col2-article-content']/div[@class='ms-col2-article-content-inner']/div[@class='ms-col2-article-body']/div[@class='ms-col2-article-body-inner']/div[@class='ms-col2-recipe-ingredients']/p",
        "ingredients" : "//div[@id='ms-col2-article-content']/div[@class='ms-col2-article-content-inner']/div[@class='ms-col2-article-body']/div[@class='ms-col2-article-body-inner']/div[@class='ms-col2-recipe-ingredients']/ul/li",
        "directions" : "//div[@id='ms-col2-article-content']/div[@class='ms-col2-article-content-inner']/div[@class='ms-col2-article-body']/div[@class='ms-col2-article-body-inner']/div[@class='ms-col2-recipe-directions']/ol/li/span"
        }
    rules = (
        Rule(SgmlLinkExtractor(\
                allow=(\
                    "http://www.marthastewart.com/recipe-finder\?vgnextoid=[a-zA-Z0-9]+&startSearch=true&searchTerm=&pageNum=[0-9]+"),\
                    unique = False), process_links = 'getNext'),
        Rule(SgmlLinkExtractor(\
                allow = (\
                    "http://www.marthastewart.com/recipe/[a-z-]+")),
             callback = 'parseItems'),
        )

    def getNext(self, links):
        return [links[-1]]

    def parseItems(self, response):
        hxs = HtmlXPathSelector(response)
        for attr,path in self.attrs.items():
            recf.writelines(['\n>>>', attr, '\n'])
            if attr != 'image':
                selected = '/text()'
            else:
                selected = '/@src'
            for each in hxs.select(path+selected).extract():
                recf.writelines(['\t', each, '\n'])
        recf.writelines(['\n-----------------------------------------------------\n',])

    def csvWriter(self, response):
        pass
            
headers = []
#csvwriter.writerow(headers)

SPIDER = MSSpider(start_urls = ["http://www.marthastewart.com/recipe-finder?vgnextoid=23c7fdaef3f36110VgnVCM1000003d370a0aRCRD&startSearch=true&searchTerm=&pageNum=1"])

"""
http://www.marthastewart.com/recipe-finder?vgnextoid=23c7fdaef3f36110VgnVCM1000003d370a0aRCRD&startSearch=true&searchTerm=&source=dummy&cuisine=dummy&cookingTime=dummy

http://www.marthastewart.com/recipe-finder?vgnextoid=23c7fdaef3f36110VgnVCM1000003d370a0aRCRD&startSearch=true&searchTerm=&pageNum=2
"""
