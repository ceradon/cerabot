#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Based off Legoktm's code.
"""
import re
import datetime
import pywikibot
import mwparserfromhell
#compile a bunch of regular expressions for gen fixes
APIPEA=re.compile('\[\[(?P<link>.*?)\|(?P=link)\]\]')
#BRS=re.compile('<(\\|)br(\.|\\)>', re.IGNORECASE)
DOUBLEPIPE=re.compile('\[\[(.*?)\|\|(.*?)\]\]')
BROKENLINKS1=re.compile(re.escape('http::/'), re.IGNORECASE)
BROKENLINKS2=re.compile(re.escape('http://http://'), re.IGNORECASE)

class AWBGenFixes():
    def __init__(self, site):
        self.site = site
        self.date_these = []
        self.redirects = {}
        self.skip_list = []
        self.bad_date = re.compile('[Dd]ate[^=](.*)')
        self.year = datetime.datetime.today().strftime('%Y')
        self.month = datetime.datetime.today().strftime('%B')
        self.correct_dates = {
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

    def load(self, tr=None, dt=None, skip=None):
        self.load_templates(dt=dt)
        self.load_redirects(tr=tr)
        self.load_skip_templates(templates=skip)

    def load_templates(self, dt=None):
        if dt:
            page = dt
        else:
            page = pywikibot.Page(self.site, 'Wikipedia:AutoWikiBrowser/Dated templates')
        text = page.get()
        code = mwparserfromhell.parse(text)
        for temp in code.filter_templates():
            if temp.name.lower() == 'tl':
                self.date_these.append(temp.get(1).value.lower())

    def load_skip_templates(self, templates=None):
        if not templates:
            templates = ['In use']
        for temp in templates:
            t = pywikibot.Page(self.site, 'Template:'+temp)
            for pg in t.getReferences(redirectsOnly=True):
                self.skip_list.append(pg.title(withNamespace=False).lower())


    def load_redirects(self, tr=None):
        if tr:
            page = tr
        else:
            page = pywikibot.Page(self.site, 'Wikipedia:AutoWikiBrowser/Template redirects')
        text = page.get()
        section = re.search('===Maintenance templates===\n?(.*)'+
                        '===Navbox templates===', text, re.DOTALL)
        for line in section.group(0).splitlines():
            if not '→' in line:
                continue
            split = line.split('→')
            if len(split) != 2:
                continue
            code1=mwparserfromhell.parse(split[0])
            code2=mwparserfromhell.parse(split[1])
            destination = code2.filter_templates()[0].get(1).value #ehhhh
            for temp in code1.filter_templates():
                if temp.name.lower() == 'tl':
                    name = temp.get(1).value
                    self.redirects[name.lower()] = destination
                    self.redirects[destination.lower()] = destination

    def in_use(self, text):
        """
        Returns a boolean value
        if the text contains a skip template
        """
        code = mwparserfromhell.parse(text)
        for temp in code.filter_templates(recursive=True):
            if temp.name.lower().strip() in self.skip_list:
                return True
        return False

    def do_page(self, text, fixes=False, date=True):
        if fixes:
            text = self.all_fixes(text)
        code = mwparserfromhell.parse(text)
        summary= {}
        for temp in code.filter_templates(recursive=True):
            name = temp.name.lower().strip()
            if name in self.redirects.keys():
                new_name = self.redirects[name]
                if new_name.lower() != name: #prevents from capitalizing the first letter needlessly
                    temp.name = new_name
            if (temp.name.lower() in self.date_these) and date:
                if not temp.has_param('date'):
                    temp.add('date', datetime.datetime.today().strftime('%B %Y'))
                    if temp.name.lower() in summary.keys():
                        summary[temp.name.lower()] += 1
                    else:
                        summary[temp.name.lower()] = 1
                else:
                    old_date = temp.get('date').value
                    date = temp.get('date').value.lower()
                    month = date.split()[0]
                    year = date.split()[1]
                    if month in self.correct_dates.keys():
                        month = self.correct_dates[month]
                    if 'currentmonthname' in month.lower():
                        month = self.month
                    if 'currentyear' in year.lower():
                        year = self.year
                    months = map(lambda x: x.lower(), self.correct_dates.values())
                    if not month.lower() in months:
                        month = self.month
                    new_date = month+' '+year
                    if old_date != new_date:
                        temp.get('date').value = new_date
                        if temp.name.lower() in summary.keys():
                            summary[temp.name.lower()] += 1
                        else:
                            summary[temp.name.lower()] = 1
                    else:
                        continue
        msg = ', '.join('{{%s}} (%s)' % (item, summary[item]) for item in summary.keys())
        return unicode(code), msg


    def all_fixes(self,text):
        text = self.a_pipe_a(text)
        #text = self.double_pipe(text)
        #text = self.fix_br(text)
        text = self.fix_http(text)
        return text

    def a_pipe_a(self, text):
        """
        [[A|A]] --> [[A]]
        """
        all = APIPEA.finditer(text)
        for match in all:
            text = text.replace(match.group(0), '[[%s]]' % match.group('link'))
        return text

    def fix_br(self, text):
        """
        <br> <br\> <br.> <\br> --> <br />
        """
        all = BRS.finditer(text)
        for match in all:
            text = text.replace(match.group(0), '<br />')
        return text

    def double_pipe(self, text):
        """
        [[foo||bar]] --> [[foo|bar]]
        """
        all = DOUBLEPIPE.finditer(text)
        for match in all:
            text = text.replace(match.group(0), '[[%s|%s]]' %(match.group(1), match.group(2)))
        return text

    def fix_http(self, text):
        """
        http://http://example.com --> http://example.com
        http:://example.com --> http://example.com
        """
        all1 = BROKENLINKS1.finditer(text)
        for match in all1:
            text = text.replace(match.group(0), 'http://')
        all2 = BROKENLINKS2.finditer(text)
        for match in all2:
            text = text.replace(match.group(0), 'http://')
        return text