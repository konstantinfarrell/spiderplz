import bs4
import json
import sys, os
import requests

from requests.exceptions import SSLError
from urllib.parse import urlparse


class Crawler(object):
    """
    Konstantin's web crawler.

    """

    PREFIX = "http://"
    DEPTH = 3
    MAX = 200

    def __init__(self, base_url=None):
        super(Crawler, self).__init__()

        # Initialize all the class attributes
        self.base_url = base_url
        self.urls = self.read_urls()
        self.exclusions = list()

    def get_site_info(self, url=None):

        # If there is no url specified,
        # just get the info of the base url
        if url == None:
            url = self.PREFIX + self.base_url
        else:
            if self.PREFIX not in url:
                url = self.PREFIX + url

        # Send a GET request to the url and store the response
        try:
            r = requests.get(url)
        except Exception as e:
            # Something went wrong. lets just return
            self.exclusions.append(url)
            return

        # Store all important data
        site = dict()
        site["status_code"] = r.status_code
        site["headers"] = r.headers
        site["content"] = r.content
        site["urls"] = self.get_links(site["content"])
        site["external"] = self.filter_external_urls(site["urls"])
        site["unique_external"] = self.filter_unique_external_urls(site["urls"])

        # Should be implemented after some sort of
        # Site mapping function is implemented.
        # For now it is not important
        # site["internal"]

        return site

    def get_links(self, content):
        """
        Grabs all the links out of the <body> tag in a content block.
        These are raw links and will need to be cleaned or appended as necessary.
        """

        urls = list()
        # Turn that content into soup
        # (using the BeautifulSoup html parsing library)
        soup = bs4.BeautifulSoup(content, 'html.parser')

        # Start assigning attributes and whatnot
        body = soup.body

        # Grab everything that looks like a link
        # and throw it into a list
        try:
            links = body.findAll(href=True)
        except AttributeError as e:
            # Tried to parse an empty page for a body
            return None

        unfiltered_urls = list(link['href'] for link in links)
        for url in unfiltered_urls:
            if url not in self.exclusions and url not in self.urls:
                urls.append(url)
        return urls

    def filter_external_urls(self, urls):
        """
        Takes a raw list of urls and returns only links to external sites
        """
        to_return = list()
        if urls != None:
            for url in urls:
                parsed_uri = urlparse(url)
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                if domain != None \
                    and 'http' in domain \
                    and url not in to_return \
                    and url not in self.urls:
                    to_return.append(url)
        return to_return

    def filter_unique_external_urls(self, urls):
        """
        Takes a raw list of urls and returns only unique domain names
        """
        to_return = list()
        if urls != None:
            for url in urls:
                parsed_uri = urlparse(url)
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                if domain != None and 'http' in domain:
                    if domain not in to_return and domain not in self.urls:
                        to_return.append(domain)
        return to_return

    def filter_internal_urls(self, urls):
        """
        Takes a raw list of urls and returns only internal links
        """
        to_return = list()
        external = self.filter_external_urls(urls)
        for url in urls:
            if url not in external and url != "" and url not in to_return:
                to_return.append(url)
        return to_return

    def gather_domains(self, base_url, depth=None):
        """
        This recursive function gets all the urls from a page.
        It then checks the counter, and repeats the process on
        all found urls until the counter is 0.
        Then it takes all unique urls and puts them in a list
        """
        if depth == None:
            depth = self.DEPTH

        site = self.get_site_info(base_url)
        if site == None:
            return
        for url in site["unique_external"]:
            # Keep track of how many urls we've found
            count = len(self.urls)
            if depth != 0 and count < self.MAX and url not in self.urls:
                # Display the url so the end user doesn't think this thing is broken
                print(url)

                self.gather_urls(url, depth - 1)
            else:
                # Add this url to the list
                self.urls[url] = url
        return

    def gather_urls(self, base_url, depth=None):
        """
        This recursive function gets all the urls from a page.
        It then checks the counter, and repeats the process on
        all found urls until the counter is 0.
        Then it takes all unique urls and puts them in a list
        """

        if depth == None:
            depth = self.DEPTH

        site = self.get_site_info(base_url)
        if site == None:
            return
        for url in site["external"]:
            # Keep track of how many urls we've found
            count = len(self.urls)
            if depth != 0 and count < self.MAX and url not in self.urls:
                # Display the url so the end user doesn't think this thing is broken
                print(url)
                # Write it out to a file

                # Add this url to the list
                self.urls[url] = url
                self.gather_urls(url, depth - 1)
        self.write_urls()
        return

    def write_urls(self):
        """
        appends urls to file
        """
        first = ""
        count = 0
        with open('urls.json', 'w+') as f:
            # write out some valid json
            f.write('{ "urls":[\n')
            # Write all the urls
            for url in self.urls:
                count = count + 1
                if first == "":
                    first = "{}\n".format(json.dumps(url))
                else:
                    f.write("{},\n".format(json.dumps(url)))
            # Append the first entry without the end comma
            f.write(first)
            f.write('],\n')
            f.write('"count": ' + str(count) + '\n')
            # And close the valid json
            f.write('}')

    def read_urls(self):
        """
        Read urls from a file
        """
        urls = dict()
        try:
            with open('urls.json', 'r') as urls_file:
                data = json.load(urls_file)
                print(data)
        except FileNotFoundError as e:
            pass
        return urls

    def read_exclusions(self):
        """
        Read exclusions from a file
        """
        exclusions = list()
        try:
            with open('exclusions.json') as ex_file:
                data = json.load(ex_file)
        except FileNotFoundError as e:
            pass
        return exclusions

# Test code
crawler = Crawler()

url = "news.ycombinator.com"
site = crawler.gather_urls(url)
