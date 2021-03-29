import scrapy

from scrapy.loader import ItemLoader

from ..items import LedyardbankItem
from itemloaders.processors import TakeFirst


class LedyardbankSpider(scrapy.Spider):
	name = 'ledyardbank'
	start_urls = ['https://ledyardbank.com/News.aspx?year=2020']

	def parse(self, response):
		post_links = response.xpath('//p[@class="news"]')
		for post in post_links:
			url = post.xpath('./a/@href').get()
			date = post.xpath('./text()[normalize-space()]').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//div[@class="news-nav"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="main-inner-content"]/h1/text()').get()
		description = response.xpath('//div[@class="newsBody"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=LedyardbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
