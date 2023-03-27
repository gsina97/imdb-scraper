from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import dateutil.parser as dparser

IterList = []
MonthList = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
             'November', 'December']

TitleList, YearList, RatingList, LinkList, BudgetList, GrossList, NetList, DateList, MonthDataList = [], [], [], [], [], [], [], [], []


def first_scrape(df1):
    # to get the numbers to loop through in url
    # for x in range(2000, 2100):
    for x in range(1000, 2100):
        if (x % 50) == 1:
            IterList.append(x)

    for n in IterList:
        print("Scraping " + str(n))
        # beautifulsoup things
        url = "https://www.imdb.com/search/title/?title_type=feature&num_votes=5000,&genres=horror&view=simple&sort=release_date,asc&start=%s&ref_=adv_nxt" % n
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        # look up data needed
        title = soup.findAll('span', {'class': 'lister-item-header'}, {'title'})
        year = soup.findAll('span', {'class': 'lister-item-year text-muted unbold'})
        rating = soup.findAll('div', {'class': 'col-imdb-rating'})
        link = soup.find_all('a')

        # cleaning and appending to lists
        for i in title:
            TitleList.append(i.get_text()[7:-9].replace('\n', ' '))
            # print(i.get_text()[7:-9].replace('\n', ' '))

        for i in year:
            YearList.append(re.sub("\D", "", i.get_text()))

        for i in rating:
            # print(i.get_text().replace(' ', ''))
            RatingList.append(re.sub(r'\s+', '', i.get_text()))
            # print(re.sub(r'\s+', '', i.get_text()))

        for i in link:
            if "/title/tt" in i.get('href'):
                if (i.get('href')) not in LinkList:
                    LinkList.append(i.get('href'))

    # print(len(LinkList))
    # adding all the lists to df
    data = {
        "Title": TitleList,
        "Year": YearList,
        "Rating": RatingList,
        "Link": LinkList
    }

    df1 = pd.DataFrame(data)
    return df1
    # print(df1)


testList = ["/title/tt12873562/", "/title/tt13314558/"]


# second_scrape is to look through the urls for each of the movies to get money and date data
def second_scrape(df2):
    for n in LinkList:
        # for n in testList:
        url = "https://www.imdb.com%s" % n
        # add this header because imdb hates scrapers
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        money = soup.findAll('li', {'class': 'ipc-metadata-list__item sc-6d4f3f8c-2 fJEELB'})
        date = soup.findAll('li', {'data-testid': 'title-details-releasedate'})

        # this is to append nothing to the list so it doesn't mess up dataframe
        budgetBool = False
        grossBool = False

        print("Scraping " + url + "...")
        for i in money:
            if "Budget" in i.get_text():
                budgetBool = True
                budgetText = i.get_text()[6:]

                # print(budgetText + " (OG)")
                budgetText = laundry_machine(budgetText, i)

            if "Gross worldwide" in i.get_text():
                grossBool = True
                grossText = i.get_text()[15:]
                grossText = laundry_machine(grossText, i)

        if budgetBool:
            print(budgetText)
            BudgetList.append(budgetText)
        else:
            print("no budget")
            BudgetList.append(None)

        if grossBool:
            print(grossText)
            GrossList.append(grossText)
        else:
            print("no gross")
            GrossList.append(None)

        if budgetBool and grossBool:
            netText = grossText - budgetText
            print(netText)
            NetList.append(netText)
        else:
            print("no net")
            NetList.append(None)

        for i in date:
            dateText = i.get_text()[12:].replace(',', '')
            # this is to catch any pages where there isn't a full date
            if dateText.split()[0] in MonthList and int(dateText.split()[1]) < 32:
                dateText = dparser.parse(dateText, fuzzy=True)
                monthText = str(dateText)[5:7]
                print(dateText)
                print(monthText)
                DateList.append(dateText)
                MonthDataList.append(monthText)
            else:
                print("no date")
                DateList.append(None)
                MonthDataList.append(None)
        # do i have to adjust for inflation?
        print("\n")

    data = {
        "Budget": BudgetList,
        "Gross": GrossList,
        "Net": NetList,
        "Date": DateList,
        "Month": MonthDataList
    }
    df2 = pd.DataFrame(data)
    return df2


# this is convert and clean up currency to make it all USD
def laundry_machine(temp, i):
    temp = temp.replace(' ', "")
    temp = temp.replace(',', "")
    if "(estimated)" in temp:
        temp = temp.replace('(estimated)', '')
    if "€" in temp:
        temp = ("$" + str(float(temp[1:]) * 1.04))
    if "£" in temp:
        temp = ("$" + str(float(temp[1:]) * 1.21))
    if "NOK" in temp:
        temp = ("$" + str(float(temp[3:]) * .1))
    if "A$" in temp:
        if "CA$" in temp:
            temp = ("$" + str(float(temp[3:]) * .75))
        else:
            temp = ("$" + str(float(temp[2:]) * .68))
    if "HK$" in temp:
        temp = ("$" + str(float(temp[3:]) * .128))
    if "NZ$" in temp:
        temp = ("$" + str(float(temp[3:]) * .63))
    if "MX$" in temp:
        temp = ("$" + str(float(temp[3:]) * .0516))
    if "NT$" in temp:
        temp = ("$" + str(float(temp[3:]) * .0325))
    if "THB" in temp:
        temp = ("$" + str(float(temp[3:]) * .0279))
    if "₩" in temp:
        temp = ("$" + str(float(temp[1:]) * .00075))
    if "HUF" in temp:
        temp = ("$" + str(float(temp[3:]) * .002515))
    if "IDR" in temp:
        temp = ("$" + str(float(temp[3:]) * .000063889806))
    if "RUR" in temp:
        temp = ("$" + str(float(temp[3:]) * .016550135))
    if "₹" in temp:
        temp = ("$" + str(float(temp[1:]) * .0122))
    if "¥" in temp:
        if "Japan" in i.get_text():
            temp = ("$" + str(float(temp[1:]) * .0072))
        else:
            print("?")
            return 0
            temp = ("$" + str(float(temp[1:]) * .14))
    if "$" in temp:
        temp = float(temp[1:])
    else:
        print("catch")
    return temp


def main():
    df1 = pd.DataFrame
    df2 = pd.DataFrame
    df1 = first_scrape(df1)
    df2 = second_scrape(df2)
    df = pd.concat([df1, df2], axis=1)

    df.to_csv('imdbhorrordata5kratingsv4.csv')


if __name__ == "__main__":
    main()

# print(YearList)
# print(RatingList)
# print(LinkList)
# print(TitleList)


# for i in range(len(LinkList)):
#     print(i)
#     print(LinkList[i])

# https://www.imdb.com/search/title/?title_type=feature&num_votes=1000,&genres=horror&view=simple&sort=release_date,desc
# https://www.imdb.com/search/title/?title_type=feature&num_votes=1000,&genres=horror&view=simple&sort=release_date,desc&start=1&ref_=adv_nxt
