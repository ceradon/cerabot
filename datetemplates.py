#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Based off Legoktm's code.
"""
import datetime
import pywikibot
import awb_gen_fixes

class DateBot():
    def __init__(self, test=False):
        self.site = pywikibot.Site()
        self.AWB = awb_gen_fixes.AWBGenFixes(self.site)
        self.stop_page = pywikibot.Page(self.site, 'User:Cerabot/Run/Task 1')
        self.summary_end = '. ([[User:Cerabot/Run/Task 1|bot]])'
        self.test = test
        
    def run(self, test=False):
        self.AWB.load()
        if not test:
            for page in list(set(self.gen())):
                self.do_page(page)
        else:
            self.do_page(pywikibot.page.Page(self.site, "User:Cerabot"))

    def check_run_page(self):
        text = self.stop_page.get(force=True)
        if not 'yes' in text.lower():
            raise Exception("Stop page disabled")

    def gen(self):
        cat = pywikibot.Category(self.site, 'Category:Wikipedia maintenance categories sorted by month')
        if not self.test:
            for subcat in cat.subcategories():
                for page in subcat.articles(content=True, namespaces=[0]):
                    yield page
        else:
            yield pywikibot.Page(self.site, "User:Cerabot/Sandbox")

    def is_dormant(self, page):
        """
        Checks if a page hasn't been
        edited for the past 10 minutes
        """
        last = page.editTime()
        dt = pywikibot.Timestamp.fromISOformat(last)
        return datetime.datetime.now() - dt > datetime.timedelta(minutes=10)

    def do_page(self, page):
        print page
        if page.isRedirectPage():
            return
        text = page.get()
        if self.AWB.in_use(text):
            return
        elif not self.is_dormant(page):
            return
        newtext, msg = self.AWB.do_page(text)
        if not msg:
            return
        try:
            self.check_run_page()
            page.put(unicode(newtext), 'Dating templates: '+msg+self.summary_end)
        except pywikibot.exceptions.PageNotSaved:
            pass
        except pywikibot.exceptions.LockedPage:
            pass

if __name__ == "__main__":
    bot = DateBot()
    bot.run()
