#! /usr/bin/env python
# -*- coding: utf-8  -*-
import re
import datetime
import sys
import time
import codecs
from cerabot.wiki.tasks import Task
import mwparserfromhell
from cerabot import exceptions
from cerabot.wiki.api import Site
from dateutil.parser import parse

class DateTemplates(Task):
    """Bot to add dates to maintenance templates that have none."""
    name = "template_dater"
    task = 1

    @property
    def pages(self):
        if not hasattr(self, "pages"):
            self._pages = None
        return self._pages

    @pages.setter
    def pages(self, value):
        self._pages = value

    @property
    def to_date(self):
        if not hasattr(self, "_to_date"):
            self._to_date = []
        return self._to_date

    @property
    def redirects(self):
        if not hasattr(self, "_redirects"):
            self._redirects = {}
        return self._redirects

    @property
    def year(self):
        year = datetime.datetime.today().strftime('%Y')
        return year

    @property
    def month(self):
        month = datetime.datetime.today().strftime('%B')
        return month

    @property
    def correct_dates(self):
        correct_dates = {
            'january':'January',
            'jan':'January',
            'february':'February',
            'feb':'February',
            'march':'March',
            'mar':'March',
            'april':'April',
            'apr':'April',
            'may':'May',
            'june':'June',
            'jun':'June',
            'july':'July',
            'jul':'July',
            'august':'August',
            'aug':'August',
            'september':'September',
            'sep':'September',
            'sept':'September',
            'october':'October',
            'oct':'October',
            'november':'November',
            'nov':'November',
            'december':'December',
            'dec':'December'
        }
        return correct_dates

    def _load_templates(self):
        """Load the templates we have to date."""
        templates_page = self._site.page("Wikipedia:AutoWikiBrowser/"+ \
                "Dated templates")
        templates_page.load()
        text = template_page.content
        code = mwparserfromhell.parse(text)
        for template in code.filter_templates():
            if template.name.lower() == "tl":
                self.to_date.append(template.get(1).value.lower())
        
        """Load the redirects to the templates we must date."""
        redirects_page = self._site.page("Wikipedia:AutoWikiBrowser/"+ \
            "Template redirects")
        redirects_page.load()
        text_ = redirects_page.content
        try:
            section = text_[text.find(
                    "===Maintenance templates===")
                    +len("===Maintenance templates==="):
                    text_.find("===Navbox templates===")
                    +len("===Navbox templates===")]
        except Exception:
            pass
        delimeter = unicode('→')
        for line in section.splitlines():
            if not delimeter in line:
                continue
            split = line.split(delimeter)
            if len(split) != 2:
                continue
            code_1 = mwparserfromhell.parse(split[0])
            code_2 = mwparserfromhell.parse(split[1])
            destination = code_2.filter_templates()[0].get(1).value
            for template in code_1.filter_templates():
                if template.name.lower() == "tl":
                    name = template.get(1).value
                    self.redirects[name.lower()] = destination
                    self.redirects[destination.lower()] = destination

    def _in_use(self, page):
        """Checks if the page is in use."""
        code = mwparserfromhell.parse(page.content)
        templates = code.filter_templates()
        for template in templates:
            if 'in use' in template.lower():
                return True
        return False

    def _generate_pages(self):
        """Generates a list of all pages to date."""
        i = "Category:Wikipedia maintenance categories sorted by month"
        categoryobj = self._site.category(i)
        categoryobj.load_attributes(get_all_members=True)
        for item in members:
            itemobj = self._site.category(item.title)
            for page in itemobj.load_attributes(get_all_members=True):
                yield page
        return

    def setup(self):
        self.pages = self._generate_pages()
        self._load_templates()

    def is_dormant(self, page):
        timestamp = page.last_edited
        delta = datetime.datetime.now() - timestamp
        result = delta > datetime.timedelta(seconds=600)
        return result

    def run_bot(self, page=None):
        summary = {}
        if page:
            text = page.content
            code = mwparserfromhell.parse(text)
            templates = code.filter_templates(recursive=True)
            for template in templates:
                name = template.name.lower().strip()
                if name in self._redirects.keys():
                    new_name = self._redirects[name]
                    if new_name.lower() != name:
                        template.name = new_name
                if template.name.lower() in self._to_date:
                    if not template.has_param("date"):
                        template.add('date', datetime.datetime.today()
                                .strftime('%B %Y'))
                        if template.name.lower() in summary.keys():
                            summary[template.name.lower()] += 1
                        else:
                            summary[template.name.lower()] = 1
        msg = ', '.join('{{%s}} (%s)' % (item, summary[item]) 
                for item in summary.keys())
        return unicode(code), msg

    def run(self):
        for page in self.pages:
            print "[["+page.title+"]]"
            if page.is_redirect:
                continue
            if self._in_use(page):
                print "Page "+page.title+" is in use."
                continue
            if not self.is_dormant(page):
                continue
            if not page.is_excluded:
                continue
            newtext, msg = self.run_bot(page)
            if not msg:
                continue
            try:
                self.run_page_enabled()
                newtext = newtext.encode('utf-8')
                res = page.edit(text=newtext, summary=self.build_summary(
                        'Dating templates: '+msg))
                if res['edit']['result'] == "Success":
                    out = "Edit was successful. New revision id is: {revid}."
                    print out.format(revid=res['edit']['newrevid'])
                    print res
                else:
                    out = "Edit failed for some reason\n "+ \
                            "Here is the data the API sent us: {api_data}"
                    print out.format(api_data=res)
            except exceptions.CerabotError as e:
                msg = "Exception was raised: {1}"
                self._logger.warn(msg.format(e.message))
                continue
        return
