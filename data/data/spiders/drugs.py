import scrapy
from pathlib import Path

class DrugsSpider(scrapy.Spider):
    name = "Drugs"
    
    def start_requests(self):
        urls=['https://drugs.com/condition/myocardial-infarction.html?page_all=1']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        gnames=[]
        page=response.url.split("/")[-1]
        table=response.css(".ddc-table-secondary")
        drugs=table.css(".ddc-table-row-medication")
        drugInfo=table.css(".ddc-table-row-medication-info")
        for info in drugInfo:
            gnamei=info.css("td>dl>dd::text").get()
            gnames.append(gnamei)
        i=0
        for drug in drugs:
            dname=drug.css("th>span>a::text").get()
            rating=drug.css("td>span::text").get().strip()
            gname=gnames[i]
            i=i+1
            yield{
                'DrugName': dname,
                'Rating': rating,
                'genericName': gname,
                'Disease':'Heart Attack',
            }
