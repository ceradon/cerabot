#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Copyright (C) 2012 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
import pywikibot
import awb_gen_fixes

class DateBot():
    def __init__(self):
        self.site = pywikibot.Site()
        self.AWB = awb_gen_fixes.AWBGenFixes(self.site)
        self.stop_page = pywikibot.Page(self.site, 'User:Cerabot/Run/Task 1')
        self.summary_end = '. ([[User:Cerabot/Run/Task 1|bot]])'
    def run(self):
        self.AWB.load()
        self.do_page(pywikibot.Page(self.site, 'User:Cerabot/Sandbox'))
        for page in self.gen():
            self.do_page(page)

    def check_run_page(self):
        text = self.stop_page.get(force=True)
        if text.lower() != 'yes':
            raise Exception("Stop page disabled")

    def gen(self):
        cat = pywikibot.Category(self.site, 'Category:Wikipedia maintenance categories sorted by month')
        for subcat in cat.subcategories():
            for page in subcat.articles(content=True, namespaces=[0]):
                yield page

    def is_dormant(self, page):
        """
        Checks if a page hasn't been
        edited for the past 20 minutes
        """
        last = page.editTime()
        dt = pywikibot.Timestamp.fromISOformat(last)
        return datetime.datetime.now() - dt > datetime.timedelta(minutes=20)

    def do_page(self, page):
        print page
        text = page.get()
        if self.AWB.in_use(text):
            return
        elif not self.is_dormant(page):
            return
        newtext, msg = self.AWB.do_page(text)
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
