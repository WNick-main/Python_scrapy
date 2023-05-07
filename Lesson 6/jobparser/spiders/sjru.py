import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):

    name = "sjru"
    allowed_domains = ["www.superjob.ru"]
    start_urls = ["https://www.superjob.ru/vakansii/inzhener.html",
                  "https://www.superjob.ru/vacancy/search/?keywords=Data"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        adv_list = response.xpath("//div[@class='f-test-search-result-item']")
        for adv in adv_list:
            link = adv.xpath(".//a[contains(@class,'f-test-link-')]/@href").get()
            if link:
                yield response.follow(link, callback=self.vacancy_parsers)

    def vacancy_parsers(self, response: HtmlResponse):
        url = response.url
        title = response.xpath("//h1/text()").get()
        raw_salary = response.xpath("//h1//parent::div/span/span/text()").getall()
        item = JobparserItem(url=url, title=title, salary=raw_salary)
        yield item
