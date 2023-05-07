import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):

    name = "hhru"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text=Data&ored_clusters=true",
                  "https://hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text=Data&ored_clusters=true"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@class='serp-item__title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parsers)

    def vacancy_parsers(self, response: HtmlResponse):
        url = response.url
        title = response.xpath("//h1[@data-qa='vacancy-title']/text()").get()
        raw_salary = response.xpath("//div[@data-qa='vacancy-salary']/span/text()").getall()
        item = JobparserItem(url=url, title=title, salary=raw_salary)
        yield item
