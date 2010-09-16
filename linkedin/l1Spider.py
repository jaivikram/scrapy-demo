from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.item import Item, Field
import time
from scrapy.stats import stats
from scrapy.conf import settings
settings.overrides['CONCURRENT_REQUESTS_PER_SPIDER'] = 300
settings.overrides['WEBSERVICE_ENABLED'] = True
import csv
csvwriter = csv.writer(open('items.csv', 'wb'))

class LinkedinSpider(CrawlSpider):
    name = "au.linkedin.com"
    allowed_domains = [ "linkedin.com"]
    attrs = {
        "first_name": "//h1[@id='name']/span[@class='fn n']/span[@class='given-name']/text()",
        "family_name": "//h1[@id='name']/span[@class='fn n']/span[@class='family-name']/text()",
        "locality": "//body/div[@class='hresume']/div[@class='profile-header']/div[@class='masthead vcard contact']/div[@class='content']/div[@class='info']/div[@class='adr']/p[@class='locality']/text()",
        "connections" : "//div[@id='overview']/dl/dd[@class='connections']/strong/text()",
        "recommended": "//div[@id='overview']/dl/dd[@class='recommended']/strong/text()",
        "websites": "//div[@id='overview']/dl/dd/ul/li/a[@class='url']/@href", 
        "interested_in" :  "//div[@id='contact-settings']/ul/li/text()",
        "summary" : "//div[@id='summary']/p[@class='summary']/text()",
        "specialities" : "//div[@id='summary']/p[@class='skills']/text()",
        "honors": "//div[@id='additional-information']/p[@class='honors']/text()",
        "education": "//div[@id='education']/ul[@class='vcalendar']/li[@class='education vevent vcard']",
        "experience": "//div[@id='experience']/ul[@class='vcalendar']/li[@class='experience vevent vcard']",
        }
    deep_items = {
        'education' : {
            "title" : "h3[@class='summary fn org']",
            "degree": "div[@class='description']/p/span[@class='degree']",
            "major" : "div[@class='description']/p/span[@class='major']",
            "dtstart": "div[@class='description']/p/abbr[@class='dtstart']",
            "dtend":"div[@class='description']/p/abbr[@class='dtend']",
            "activities":"dl[@class='activities-societies']/dd"
            },
        'experience' : {
            "title": "h3[@class='title']",
            "organization": "h4[@class='org summary']",
            "organization_details": "p[@class='organization-details']",
            "dtstart": "p[@class='period']/abbr[@class='dtstart']",
            "dtstamp": "p[@class='period']/abbr[@class='dtstamp']",
            "dtend": "p[@class='period']/abbr[@class='dtend']",
            "description": "p[@class='description']",
            }
        }
    rules = (
        Rule(SgmlLinkExtractor(\
                allow=(\
                    'http://au.linkedin.com/directory/people/[b-z].html'))),
        Rule(SgmlLinkExtractor(\
                allow=(\
                    'http://au.linkedin.com/directory/people/au/[A-Z][1-9][1-9]?.html'))),
        Rule(SgmlLinkExtractor(\
                allow = (\
                    'http://au.linkedin.com/directory/people/au/[a-z][a-z-1-9]+.html'))),
        Rule(SgmlLinkExtractor(\
                allow = (\
                    'http://au.linkedin.com/pub/dir/[a-z]+/[a-z]+'))),
        Rule(SgmlLinkExtractor(\
                allow = (\
                    'http://au.linkedin.com/pub/[a-z-]+/[a-z0-9-]+/[a-z0-9-]+/[a-z0-9-]+')),
             callback = 'parseItems'),
        Rule(SgmlLinkExtractor(\
                allow = (\
                    'http://www.linkedin.com/in/[a-z]+')),
             callback = 'parseItems'),
        )

    def cleanData(self, data):
        if type(data) != type([]):
            return data.strip(' \n')
        else:
            return ",".join([each.strip(' \n') for each in data])

    def parseItems(self, response):
        hxs = HtmlXPathSelector(response)
        self.profile = {}
        for k,v in self.attrs.items():
            temp = hxs.select(v)
            if k in ['experience', 'education']:
                exps = []
                for exp in temp:
                    texp = {}
                    for attr,path in self.deep_items[k].items():
                        try:
                            texp[attr] = self.cleanData(exp.select(path+'/text()').extract())
                        except Exception,e:
                            self.log(e)
                            continue
                    exps.append(texp)
                self.profile[k] = exps
            elif k == 'locality':
                try:
                    loc = temp.extract()[0]
                except IndexError,e:
                    try:
                        xp = "//body/div[@class='hresume']/div[@class='profile-header']/div[@class='masthead vcard contact portrait']/div[@class='content']/div[@class='info']/div[@class='adr']/p[@class='locality']/text()"
                        loc = hxs.select(xp).extract()[0]
                    except IndexError:
                        xp = "//div[@id='nameplate']/div[@class='adr']/p[@class='country-name']/text()"
                        loc = hxs.select(xp).extract()[0]
                self.profile[k] = self.cleanData(loc)
            else:
                try:
                    self.profile[k] = self.cleanData(temp.extract())
                except Exception, e:
                    self.log(e)
                    continue
        self.csvWriter(response)

    def csvWriter(self, response):
        try:
            gen_cols = self.attrs.keys()
            gen_cols.sort()
            ed_cols = self.deep_items['education'].keys()
            ed_cols.sort()
            ex_cols = self.deep_items['experience'].keys()
            ex_cols.sort()
            cols = {'general': gen_cols, 'education': ed_cols, 'experience': ex_cols}
            def formatChunks(tp):
                return '\n------------\n'.join(['\n'.join(["%s: %s" % (k, each[k]) for k in cols[tp]])
                                                for each in self.profile[tp]])
            edn = formatChunks('education')
            exp = formatChunks('experience')
            gen_attrs = [self.profile[each] for each in gen_cols
                         if each not in ['education', 'experience']]
            csv_attr = [response.url]
            csv_attr.extend(gen_attrs)
            csv_attr.extend([edn, exp])
            self.log(csv_attr)
            csvwriter.writerow(csv_attr)
        except Exception, e:
            self.log(e)
            
headers = ["URL"]
temp = [each for each in LinkedinSpider.attrs.keys()
        if each not in ['education', 'experience']]
temp.sort()
headers.extend(temp)
headers.extend(["Education", "Experience"])
csvwriter.writerow(headers)

SPIDER = LinkedinSpider(start_urls = ["http://au.linkedin.com/directory/people/a.html"])



