from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.item import Item, Field

class GithubProfile(Item):
    name = Field()
    memeber_since = Field()
    public_repo_count = Field()
    followers_count = Field()
    public_repos = Field()

class GithubFollowers(Item):
    name = Field()
    followers = Field()

class GithubFollowing(Item):
    name = Field()
    following_people = Field()
    following_repos = Field()
    
USER = 'jaivikram'
BASE_URL = "http://github.com/%s" % USER
class GithubProfileSpider(CrawlSpider):
    name = 'github.com'
    allowed_domains = ['github.com',]
    rules = (
        Rule(SgmlLinkExtractor(
                allow = ("%s$" % BASE_URL , ),
                ),
             callback = 'parseMain', follow = True ),
        Rule(SgmlLinkExtractor(
                allow = ("%s/(followers)|(following)" % BASE_URL , ),
                deny = ("%s/followers\?locale=[a-z]+" % BASE_URL, 
                        "%s/following\?locale=[a-z]+" % BASE_URL, )
                ),
             callback = 'parseFollow', follow = True ),
        )
    item = None

    def parseFollow(self, response):
        hxs = HtmlXPathSelector(response)
        if response.url == "%s/followers" % BASE_URL:
            followers = hxs.select("//ul[@id='watchers' and @class='members']/li/a[2]/text()").extract()
            print("followers: \n", followers)
        elif response.url == "%s/following" % BASE_URL:
            following_people = hxs.select("//ul[@id='watchers' and @class='members']/li/a[2]/text()").extract()
            temp = hxs.select("//div[@id='main']/div[2][@class='site']/div[2][@class='columns userrepos']/div[2][@class='repos']/ul[@class='repo_list']/li[@class='public source']/a")
            following_repos = []
            for t in temp:
                user, repo = t.select("span/text()").extract()
                following_repos.append({'user': user, 'repo': repo})
            print("following_people: \n", following_people)
            print("following_repos: \n", following_repos)            

    def parseMain(self, response):
        hxs = HtmlXPathSelector(response)
        name = hxs.select("//div[@id='main']/div[2][@class='site']/div[1][@class='pagehead userpage mine']").extract()[0]
        member_since = hxs.select("//div[@id='main']/div[2][@class='site']/div[2][@class='columns profilecols']/div[1][@class='first vcard']/dl[2]/dd").extract()[0]
        public_repo_count = hxs.select("//div[@id='main']/div[2][@class='site']/div[2][@class='columns profilecols']/div[2][@class='last']/ul[@class='stats']/li[1]/a/strong").extract()[0]
        followers_count = hxs.select("//div[@id='main']/div[2][@class='site']/div[2][@class='columns profilecols']/div[2][@class='last']/ul[@class='stats']/li[2]/a/strong").extract()[0]
        public_repos_element = hxs.select("//div[@id='main']/div[2][@class='site']/div[4][@class='columns profilecols']/div[1][@class='first']/ul[@class='repositories']/li").extract()
        public_repos = []
        for repo in public_repos_element:
            public_repo = {}
            public_repo['name'] =  repo.select("h3/a").extract()[0]
            public_repo['watchers'] = repo.select("ul[@class='repo-stats']/li[1][@class='watchers']/a/text()").extract()[0]
            public_repo['forks'] = repo.select("ul[@class='repo-stats']/li[2][@class='forks']/a").extract()[0]
            public_repo['description'] = repo.select("div[@class='body']/p[1][@class='description']").extract()[0]
            public_repo['activity'] = repo.select("div[@class='body']/p[2][@class='updated-at']/abbr[@class='relatize relatized']").extract()[0]
            public_repos.append(public_repo)
        print("name: %s\n member_since: %s\n public_repo_count: %s\n "+\
                  "followers_count: %s\n public_repos: \n %s" % \
                  (name, member_since, public_repo_count, followers_count,
                   public_repos))
        

SPIDER = GithubProfileSpider(start_urls = [BASE_URL,])

