#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Gabriele Josephs (ceradon)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys
from pywikibot import Page
import mwparserfromhell

class TemplateReplacer():
    """
    An English Wikipedia bot that trawls through looking for any
    pages that transclude a particular template and replacing it 
    with another template.
    """

    def __init__(self, site, names, target, namespaces=[], test=(False), 
            include_redirects=False, runpage=""):
        """
        Initiates a TemplateReplacer object.
        
        The purpose of this task is to recurse over all pages
        that use a particular template and substitute it for another.
        This is a pretty common request on Wikipedia, therefore
        I created a blanket software to use as necessary for any task
        in this scope that may come along. However, this is FOSS, 
        so you may use it as you would.
        
        @param site: a Pywikibot Site object.
        @type site: Site
        @param names: an list of templates to be changed. 
            i.e "Template:Cn"
        @type names: list
        @param target: name of template that templates in `name` will
            be replaced by. i.e "Template:Citation needed"
        @type target: string
        @param namespaces: a list of namespaces for the bot to edit in.
        @type namespaces: list
        @param test: whether the bot is in test mode or not
        @type test: tuple, with bool as first value and test page to 
            edit in the second.
        @param include_redirects: If True, will include redirects when
            generating a list of pages to edit.
        @type incluse_redirects: boolean
        @param runpage: path to an onwiki page where the bot can be 
            shut-off. i.e. "User:ExampleBot/Run/Task 1"
        @type runpage: string
        """
        # turn the values passed to the template into global vars
        self.site = site
        if type(names) == str:
            self.names = [names]
        else:
            self.names = names
        self.target = target
        self.namespaces = namespaces
        self.test = test
        self.include_redirects = include_redirects
        
        # some predefined variables.
        self.summary = " ".join((u"Replacing templates: replaced {{%s}}",
            u"with {{%s}}."))
        if runpage:
            self.runpage = runpage
            self.summary_end = "[[{0}|bot]]".format(self.runpage)
        else:
            self.summary_end = "[[WP:BOT|bot]]"
    
    def _generator(self):
        page_list = []
        for page in self.names:
            try:
                a = Page(self.site, page)
            except Exception as e:
                print "Caught exception: {0}".format(e)
            page_list.append(a)
        for template in page_list:
            print "-[[{0}]]".format(unicode(template.title))
            for page in template.embeddedin(namespaces=self.namespaces,
                    filter_redirects=self.include_redirects, total=5000):
                print u"--[[{0}]]".format(unicode(page.title))
                yield page

    def _do_page(self, page):
        target = self.target.replace("Template:", "")
        n = [a.replace("template:", "") for a in self.names]
        text = page.get()
        code = mwparserfromhell.parse(text)
        for template in code.filter_templates(recursive=True):
            if unicode(template.name).lower() in n:
                template.name = target
        newtext = unicode(code)
        summary = self.summary + " " + self.summary_end
        page.put(newtext=newtext, comment=summary)

    def check_run_page(self):
        page = Page(self.site, self.runpage)
        text = page.get(force=True)
        if not 'yes' in text.lower():
            raise ShutoffPageDisabled("Stop page disabled")

    def deploy_task(self):
        # deploys the task to replace each occurence of the templates
        # in the transclusions of self.names with self.target
        try:
            page = Page(self.site, self.target)
        except Exception as e:
            raise ValueError(e)
        count = 0
        stream_message = "---{0} instances of {1} replaced on this page."
        if self.test[0]:
            page = Page(self.site, self.test[1])
            self._do_page(page)
            return True
        for page in self._generator():
            self._do_page(page)

class ShutoffPageDisabled(Exception):
    """Raised if shutodd page is disabled."""
