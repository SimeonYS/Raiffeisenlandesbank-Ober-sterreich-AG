import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import RaioberostereichItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?(-{1,})?'

class RaifSpider(scrapy.Spider):
    name = 'raif'

    start_urls = ['https://www.raiffeisen.at/ooe/rlb/de/meine-bank/presse.html']

    def parse(self, response):
        links = response.xpath('//div[@class="contentBoxTeaser aem-GridColumn aem-GridColumn--default--6"]//a/@href').getall()[:-1]
        yield from response.follow_all(links, self.parse_archive)

    def parse_archive(self, response):
        for article in response.xpath('//section[@class="component-pictureText content-section component-spacer "]/div[@class="content-wrapper"]'):
            date = article.xpath('.//div[@class="text-wrapper rte"]/div/*[1]//text()').get()
            article_url = article.xpath('.//div[@class="cta-wrapper"]//a/@href').get()
            url = response.urljoin(article_url)
            yield response.follow(url, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(RaioberostereichItem())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//section[@class="component-page-title component-spacer"]//text()').getall()
        title = re.sub(pattern, "", ''.join(title).strip()).replace('       ','-')
        content = response.xpath('//div[@class="component-text rte "]//text()|//div[@class="text-wrapper rte"]//text()').getall()
        content = ''.join([text.strip('\n') for text in content if text.strip('\n')]).strip()
        content = re.sub(pattern, "", content)
        if ' | ' and ' |' in content:
            content = (re.split(' \| | \|',content))[1]


        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()

