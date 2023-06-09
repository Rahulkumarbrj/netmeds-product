import requests
from bs4 import BeautifulSoup
import csv
import re

allProductLinks = []
site = "https://www.netmeds.com"


# getting raw data
def rawfilename():
    global csvFile
    filename = str(input("Enter the raw data file name: "))
    csvFile = str(input("Enter the title for CSV file: "))
    with open(f"{filename}", "r") as f:
        return f.read()

# triggering


def triggerer():
    try:
        rawdata = rawfilename()
        soup = BeautifulSoup(rawdata, 'html.parser')
        link = soup.findAll(name="a", class_="category_name")
        for lin in link:
            allProductLinks.append(site+lin["href"])
    except Exception as e:
        print(e)
        triggerer()


triggerer()


def productFinder(jURL):
    ''' This function will get the URL of
          every products and process the data 
          and get the data of fields and 
          append that data in the finalProductData'''
    try:
        r1 = requests.get(jURL)
        htmlContent1 = r1.text
        soup = BeautifulSoup(htmlContent1, 'html.parser')
        hsnTextData = soup.find(name="div", string='Hsn Code')
        HSN = hsnTextData.find_next_sibling()
        productPannel = soup.find(class_="product-top")
        imageUrl = productPannel.find(name="figure", class_="largeimage")
        img = imageUrl.find("img")
        companydata = productPannel.find(name="span", class_="drug-manu")
        company = companydata.find(name="a")
        name = productPannel.find(name="h1", class_="black-txt")
        essentials = productPannel.find(name="div", class_="essentials")
        priceff = essentials.find(name="span", class_="final-price")
        MRP = essentials.find(name="span", class_="price")

        if MRP:
            price = MRP.find(name="strike").text
        else:
            price = priceff.text

        fprice = price
        pp = fprice.replace("₹", "")
        pp = pp.replace("MRP", "")
        nameprefix = name.text
        imagename = re.sub('[^A-Za-z0-9]+', '_', nameprefix)
        data1 = soup.findAll(class_="druginfo_tab")
        data2 = soup.findAll(class_="inner-content")
        summery = []
        summeryValues = []
        for data in data1:
            summery.append(data.text)
        for value in data2:
            summeryValues.append(value)

        datamod = dict(zip(summery, summeryValues))
        response = requests.get(img['src'])
        open(f"{imagename}.png", "wb").write(response.content)
        field_names = [
            'name', 'price', 'Description', 'Key Benefits', 'How to use',
            'Safety Information/Precaution', 'Other Information', 'company', 'HSN',
            'image', "weight"
        ]
        dataf = {
            "name":
            name.text,
            "price":
            pp,
            "Description":
            datamod.get("Description", "nodata"),
            "Key Benefits":
            datamod.get("Key Benefits", "nodata"),
            "How to use":
            datamod.get("How to use", "nodata"),
            "Safety Information/Precaution":
            datamod.get("Safety Information/Precaution", "nodata"),
            "Other Information":
            datamod.get("Other Information", "nodata"),
            "company":
            company.text,
            "HSN":
            HSN.text,
            "image":
            f"{imagename}.jpg",
            "weight":
            1
        }
        with open(f'{csvFile}.csv', 'a') as csv_file:
            dict_object = csv.DictWriter(csv_file, fieldnames=field_names)
            dict_object.writerow(dataf)
    except Exception as e:
        print(e)


i = 0
for url in allProductLinks:
    i = i+1
    print(f'{i}/{len(allProductLinks)}')
    productFinder(url)
