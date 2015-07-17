from BeautifulSoup import BeautifulSoup
import urllib
import pandas as pd
import numpy as np
import scipy.optimize as so
import seaborn as sns
import argparse


def strip_results_from_ad(ad):
    """ Strip out the information from a single advert and add it to the
        results dictionary

    """

    desc = ad.find("div", attrs={"class": "listing-headline"}).find("h3").text
    loc = ad.findAll("p", attrs={"class": "location"})[0].text
    price = ad.find("div", attrs={"class": "price"})
    price = int(price.text.replace(u"&#163;", "").replace(",", ""))

    specs = ad.find("ul", attrs={"class": "specs"}).findAll("li")
    if len(specs) == 4:
        miles = int(specs[0].text.rstrip(" miles").replace(",", ""))
        fuel = specs[1].text
        bhp = int(specs[2].text.rstrip(" bhp"))
        transmission = specs[3].text
    else:
        fuel = "NA"
        bhp = np.nan
        transmission = "NA"
        try:
            miles = int(specs[0].text.rstrip(" miles").replace(",", ""))
        except:
            # Except any error...!
            miles = np.nan

    return desc, loc, price, miles, fuel, bhp, transmission


def create_url(page=1, M=269, rpp=100):
    base = ("http://www.pistonheads.com/classifieds?Category=used-cars"
            "&M={M}&ResultsPerPage={rpp}&Page={page}")
    return base.format(page=page, rpp=rpp, M=M)


def get_results(*args, **kwargs):
    url = create_url(*args, **kwargs)
    f = urllib.urlopen(url).read()
    soup = BeautifulSoup(f)
    ads = soup.findAll("div", attrs={"class": "ad-listing"})

    results = {"desc": [],
               "loc": [],
               "price": [],
               "miles": [],
               "fuel": [],
               "bhp": [],
               "transmission": []}

    for ad in ads:
        try:
            desc, loc, price, miles, fuel, bhp, transmission = strip_results_from_ad(ad)
        except:
            break

        results["desc"].append(desc)
        results["loc"].append(loc)
        results["price"].append(price)
        results["miles"].append(miles)
        results["fuel"].append(fuel)
        results["bhp"].append(bhp)
        results["transmission"].append(transmission)

    return results


def get_result_from_M(M=269, total=10):
    dfs = []
    for page in xrange(1, total):
        print "Getting results for page {} out of {}".format(page, total)
        r = get_results(M=M, rpp=100, page=page)
        dfs.append(pd.DataFrame(r))

    df = pd.concat(dfs)
    df._metadata.append(M)
    return df


def write_test_data():
    df = get_result_from_M()
    pd.to_pickle(df, "test_data.p")


def read_test_data():
    return pd.read_pickle("test_data.p")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-data", help="Generate some test data",
                        dest="TestData", action="store_true")

    args = parser.parse_args()

    if args.TestData:
        write_test_data()

if __name__ == "__main__":
    main()
