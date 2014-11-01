        #!/usr/bin/env python
# encoding: utf-8

# Copyright 2014 Steven Maude

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals
from __future__ import print_function

import codecs
import json
import logging
import sys

from collections import OrderedDict

import dshelpers
import lxml.html


def get_page_as_element_tree(url):
    """ Take URL as string; return lxml etree of HTML. """
    html = dshelpers.request_url(url).text
    return lxml.html.fromstring(html)


def is_last_radio_page(etree):
    """ Return True if current page is final index page, otherwise False. """
    next_disabled = etree.xpath('//li[@class="pagination--disabled"]')
    next_present = etree.xpath('//li[@class="pagination__next"]')

    if next_disabled or not next_present:
        return True
    else:
        return False

def extract_radio_programme_data(programme):
    """ Take programme etree; return dict containing programmed data. """
    # TODO: audio described, HD, signed flags
    logging.info("extract_radio_programme_data")
    programme_data = OrderedDict()

    programme_data['title'] = programme.xpath( './/span[@property="name"]')[0].text.strip()
    try:
        programme_data['subtitle'] = "toedeloe"
        # programme.xpath('.//div[@class="subtitle"]')[0].text.strip()
    except IndexError:
        pass
    programme_data['synopsis'] = programme.xpath( './/p[@class="synopsis"]')[0].text.strip()
    programme_data['channel'] = programme.xpath(  './/span[@class="small"]')[0].text.strip()
    try:
        programme_data['release'] = programme.xpath( './/span[@class="release"]')[0].text.strip()
    except IndexError:
        pass
    href, = programme.xpath('./a/@href')
    programme_data['url'] = ('http://www.bbc.co.uk' + href)
    programme_data['pid'] = href.split('/')[3]
    return programme_data

def parse_radio_items_from_page(etree):
    """ Parse programme data from index page; return list of dicts of data. """
    logging.info("parse_radio_items_from_page")

    programmes = etree.xpath('.//div[contains(@class, " programme--radio ")]')
    programmes_data = [extract_radio_programme_data(programme)
                       for programme in programmes]
    return programmes_data


def radio_iterate_through_index(category):
    """ Iterate over Radio index pages; return list of programme data dicts. """
    last_page = False
    page_number = 0
    items = []

    while not last_page:
        page_number += 1
        url = ("http://www.bbc.co.uk/radio/programmes/genres/{}/player/episodes".format(category))
        if page_number > 1 :
            url += ("?page={}".format(page_number))

        logging.info("Downloading page {}".format(page_number))
        etree = get_page_as_element_tree(url)
        items.append(parse_radio_items_from_page(etree))
        last_page = is_last_radio_page(etree)

    return items

def main():
    """ Scrape BBC iPlayer web frontend category; create JSON feed. """
    logging.basicConfig(level=logging.INFO)

    #logging.basicConfig(level=logging.DEBUG,
    #                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #                datefmt='%m-%d %H:%M',
    #                filename='debug.log',
    #                filemode='w')
    dshelpers.install_cache(expire_after=30*60)

    allowed_categories = ['arts', 'cbbc', 'cbeebies', 'comedy',
                          'documentaries', 'drama-and-soaps', 'entertainment',
                          'films', 'food', 'history', 'lifestyle', 'music',
                          'news', 'science-and-nature', 'sport',
                          'audio-described', 'signed', 'northern-ireland',
                          'scotland', 'wales']

    if len(sys.argv) == 2 and sys.argv[1] in allowed_categories:
        # print(json.dumps(iterate_through_index(sys.argv[1]), indent=4))
        print(json.dumps(radio_iterate_through_index(sys.argv[1]), indent=4))
    else:
        print("Usage: nitroradical.py <category name>")
        print("Allowed categories:")
        print(', '.join(allowed_categories))

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    main()
