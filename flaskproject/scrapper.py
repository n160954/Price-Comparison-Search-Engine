from flask import Flask, render_template, request, flash, jsonify
from requests import get
from bs4 import BeautifulSoup as bs
import re

app = Flask(__name__)
app.debug = 1
app.secret_key = "Some Super Random Generated Key"


class Scraper():

    def __init__(self, search_term=None):

        self.search_term = search_term

        self.request_headers = {

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip',
            'DNT': '1',
            'Connection': 'keep-alive'

        }

    def flipkart_data(self):
        classes = {
            "horizontal": {
                "name": ["div", "_4rR01T"],
                "price": "_1_WHN1",
                "rating": "_3LWZlK",
                "image": "_396cs4 _3exPp9",
                "link": "_1fQZEK"
            },
            "vertical": {
                "name": ["a", "s1Q9rs"],
                "price": "_30jeq3",
                "rating": "_3LWZlK",
                "image": "_396cs4 _3exPp9",
                "link": "_2rpwqI"

            },
            "other": {
                "name": ["div", "_2B099V"],
                "price": "_30jeq3",
                "rating": "_3LWZlK",
                "image": "_2r_T1I",
                "link": "_2UzuFa"

            }
        }

        URL = "https://flipkart.com/search?q="
        f = get(URL + self.search_term, headers=self.request_headers).text

        source = bs(f, 'html.parser')
        products = source.find_all(class_="_2kHMtA")

        _type = "horizontal"
        if (not len(products)):
            products = source.find_all(class_="_4ddWXP")
            _type = "vertical"

        if (not len(products)):
            products = source.find_all(class_="_1xHGtK _373qXS")
            _type = "other"

        product_data = []

        for product in products[:10]:

            product_name = product.find_all(classes[_type]["name"][0], {"class": classes[_type]["name"][1]})[0].get_text()
            product_price = product.find_all("div", {"class": classes[_type]["price"]})[0].get_text()
            product_image = product.find_all("img", {"class": classes[_type]["image"]})[0].get("src")

            try:
                product_rating = product.find_all("div", {"class": classes[_type]["rating"]})[0].get_text()
            except:
                product_rating = None
            product_link = "https://www.flipkart.com" + product.find_all("a", {"class": classes[_type]["link"]})[0].get("href")

            product_data.append([product_link, product_name, product_price, product_image, product_rating])

        product_data = sorted(product_data,key=lambda x: int(re.sub("[^0-9^]","",x[2])))
        return product_data

    def snapdeal_data(self):

        URL = "https://www.snapdeal.com/search?keyword="

        f = get(URL + self.search_term, headers=self.request_headers).text

        source = bs(f, 'html.parser')
        products = source.find_all(class_="product-tuple-listing")

        product_data = []

        for product in products:
            #print(product.find_all("img"))
            product_url = "" + product.find_all("a")[0].get("href")
            product_name = product.find_all("p", {"class": "product-title"})[0].get_text()
            product_price = product.find_all("span", {"class": "lfloat product-price"})[0].get_text()
            product_image = product.find_all("img", {"class": "product-image"})[0].get("src")
            product_data.append([product_url, product_name, product_price, product_image, None])


        return product_data

    def amazon_data(self):

        _type = "horizontal"

        classes = {
            "horizontal": {
                "name": ["span", "a-size-medium a-color-base a-text-normal"],
                "price": "a-price-whole",
                "rating": "a-icon-alt",
                "image": "s-image",
                "link": "a-link-normal s-no-outline"
            },
            "vertical": {
                "name": ["span", "a-size-base-plus a-color-base a-text-normal"],
                "price": "a-price-whole",
                "rating": "a-icon-alt",
                "image": "s-image",
                "link": "a-link-normal s-no-outline"
            }
        }

        URL = "https://www.amazon.in/s?k="

        f = get(URL + self.search_term, headers=self.request_headers).text

        source = bs(f, 'html.parser')
        products = source.find_all("div", {"class": "a-section a-spacing-medium"})

        if (len(products) <= 1):
            products = source.find_all(class_="a-section a-spacing-medium a-text-center")

        product_data = []

        for product in products[:10]:

            try:
                product_name = \
                product.find_all(classes["horizontal"]["name"][0], {"class": classes["horizontal"]["name"][1]})[0].get_text()
            except:

                try:
                    product_name = \
                    product.find_all(classes["vertical"]["name"][0], {"class": classes["vertical"]["name"][1]})[0].get_text()
                except Exception as e:
                    continue

            product_link = "https://www.amazon.in" + product.find_all("a", {"class": classes[_type]["link"]})[0].get("href")
            product_image = product.find_all("img", {"class": classes[_type]["image"]})[0].get("src")

            product_price = product.find_all("span", {"class": classes[_type]["price"]})[0].get_text()
            try:
                product_rating = product.find_all("span", {"class": classes[_type]["rating"]})[0].get_text().split(" ")[0]
            except:
                product_rating = None

            product_data.append([product_link, product_name, product_price, product_image, product_rating])

        product_data = sorted(product_data, key=lambda x: int(re.sub("[^0-9^]", "", x[2])))
        return product_data

    def paytm_data(self):

        URL = "https://paytmmall.com/shop/search?q="

        f = get(URL + self.search_term, self.request_headers).text
        source = bs(f, 'html.parser')

        products = source.find_all(class_="_3WhJ")

        product_data = []

        for product in products:
            product_url = "https://paytmmall.com" + product.find_all("a")[0].get("href")
            product_name = product.find_all("div", {"class": "UGUy"})[0].get_text()
            product_price = product.find_all("div", {"class": "_1kMS"})[0].get_text()
            product_image = list(product.find_all("div", {"class": "_3nWP"})[0].children)[0].get("src")
            product_link = "https://paytmmall.com" + product.find_all("a", {"class": "_8vVO"})[0].get("href")

            product_data.append([product_url, product_name, product_price, product_image, None])

        product_data = sorted(product_data, key=lambda x: int(re.sub("[^0-9^]", "", x[2])))
        return product_data

    def get_data(self):

        flipkart_data = self.flipkart_data()

        amazon_data = self.amazon_data()

        snapdeal_data = self.snapdeal_data()

        paytm_data = self.paytm_data()


        items = {

            "Flipkart": flipkart_data[:4],
            "Amazon": amazon_data[:4],
            "Paytm Mall": paytm_data[:4],
            "Snapdeal": snapdeal_data[:4]
        }

        return items

    def amazon_reviews(self, link):

        f = get(link, allow_redirects=True, headers=self.request_headers).text
        source = bs(f, 'html.parser')

        reviews = source.find_all(class_="review")

        all_reviews = []

        for review in reviews:
            try:
                name = review.find_all("span", {"class": "a-profile-name"})[0].get_text()
                rating = review.find_all("a", {"class": "a-link-normal"})[0].get("title").split(" ")[0]
                title = review.find_all("a", {"class": "review-title"})[0].get_text()
                text = review.find_all("div", {"class": "reviewText"})[0].get_text()

                all_reviews.append([name, rating, title, text])

            except Exception as e:
                continue

        return all_reviews

    def flipkart_reviews(self, link):
        f = get(link, allow_redirects=True, headers=self.request_headers).text
        source = bs(f, 'html.parser')

        reviews = source.find_all(class_="_16PBlm")

        #print(len(reviews))
        all_reviews = []

        for review in reviews:
            try:

                rating = review.find_all("div", {"class": "_3LWZlK _1BLPMq"})[0].get_text()
                title = review.find_all("p", {"class": "_2-N8zT"})[0].get_text()
                text = review.find_all("div", {"class": "t-ZTKy"})[0].get_text()

                all_reviews.append(["Flipkart User", rating, title, text])

            except Exception as e:
                continue
        # print([rating,title,text])

        return all_reviews

    def paytmmall_reviews(self, link):
        return []

    def snapdeal_reviews(self, link):
        return []

    def get_reviews(self, site, link):

        functions = {
            "Amazon": self.amazon_reviews,
            "Flipkart": self.flipkart_reviews,
            "Paytm Mall": self.paytmmall_reviews,
            "Snapdeal": self.snapdeal_reviews
        }

        review_data = functions[site](link)

        return jsonify({"output": review_data})


@app.route('/review', methods=["POST"])
def fetch_review():
    post_data = request.get_json()

    company = post_data["company"]
    url = post_data["url"]
    scrap = Scraper()
    result = scrap.get_reviews(company, url)

    return result


@app.route('/search', methods=["POST"])
def fetch_data():
    product_data=[]
    search_term = request.form.get("q")

    try:
        scrap = Scraper(search_term)
        product_data = scrap.get_data()


    except Exception as e:
        flash("[-] Internal Server Error.Check your Connection before trying.")

    return render_template("page.html",
                           len=len(product_data), product_data=product_data)


@app.route("/")
def home():
    return render_template("page.html")


if __name__ == '__main__':
    app.run(port=14444)