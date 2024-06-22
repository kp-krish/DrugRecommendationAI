import scrapy
from pathlib import Path

class DrugsInfo(scrapy.Spider):
    name = "Info"
    
    def start_requests(self):
        urls=[]
        for i in range(1,112):
            ur='https://go.drugbank.com/drugs?approved=1&c=name&d=up&page='+f'{i}'
            urls.append(ur)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        table=response.css(".table>tbody")
        medicines=table.css("tr")
        for medicine in medicines:
            comp=''
            mname=medicine.css("tr>td.name-value>strong>a::text").get()
            comps=medicine.css("tr>td.weight-value::text").getall()
            subs=medicine.css("tr>td.weight-value>sub::text").getall()
            for i in range(len(subs)):
                comp+=comps[i+1]
                comp+=subs[i]
            if(len(comps)-len(subs)>=2):    
                comp+=comps[-1]
            desc=medicine.css("tr>td.description-value::text").get()
            yield{
                'DrugName':mname,
                'ChemicalComposition':comp,
                'Description':desc,
            }
            