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
from dateutil.parser import parse

# Compile a bunch of regular expressions for gen fixes
APIPEA = re.compile('\[\[(?P<link>.*?)\|(?P=link)\]\]')
#BRS = re.compile('<(\\|)br(\.|\\)>', re.IGNORECASE)
DOUBLEPIPE = re.compile('\[\[(.*?)\|\|(.*?)\]\]')
BROKENLINKS1 = re.compile(re.escape('http::/'), re.IGNORECASE)
BROKENLINKS2 = re.compile(re.escape('http://http://'), re.IGNORECASE)

class AWBGenFixes():
    def __init__(self, site):
        self.site = site
        self.date_these = []
        self.redirects = {}
        self.skip_list = []
        self.bad_date = re.compile(r"^\W+|\W+$")
        self.year = datetime.datetime.today().strftime('%Y')
        self.month = datetime.datetime.today().strftime('%B')
        self.correct_dates = {
            '1': 'January',
            'january':'January',
            'jan':'January',
            '2':'February',
            'february':'February',
            'feb':'February',
            '3':'March',
            'march':'March',
            'mar':'March',
            '4':'April',
            'april':'April',
            'apr':'April',
            '5':'May',
            'may':'May',
            '6':'June',
            'june':'June',
            'jun':'June',
            '7':'July',
            'july':'July',
            'jul':'July',
            '8':'August',
            'august':'August',
            'aug':'August',
            '9':'September',
            'september':'September',
            'sep':'September',
            'sept':'September',
            '10':'October',
            'october':'October',
            'oct':'October',
            '11':'November',
            'november':'November',
            'nov':'November',
            '12':'December',
            'december':'December',
            'dec':'December'
        }
        self.dates = {}
        for key, value in self.correct_dates.iteritems():
            if key.isdigit():
                self.dates[int(key)] = value
            else: continue
        self.date_regex = re.compile('(' + 
            '|'.join(self.dates.values()) + '|' +
            '|'.join([x for x in self.correct_dates.keys() if len(x) <= 4 and not x.isdigit()]) +
            ')?' + '\s*' +
            '(19|20)?(\d\d)?',
            re.IGNORECASE
            )

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
            code1 = mwparserfromhell.parse(split[0])
            code2 = mwparserfromhell.parse(split[1])
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
        old_code = mwparserfromhell.parse(text)
        summary = {}
        for temp in code.filter_templates(recursive=True):
            name = temp.name.lower().strip()
            if name in self.redirects.keys():
                new_name = self.redirects[name]
                # Prevents from capitalizing the first letter needlessly
                if new_name.lower() != name: 
                    temp.name = new_name
            if (temp.name.lower() in self.date_these) and date:
                done = False
                changed = False
                for param in temp.params:
                    v = self.strip_nonalnum(unicode(param.name).strip())
                    x = self.strip_nonalnum(unicode(param.value).strip())
                    if unicode(param.name).isdigit() and x == "date":
                        param.name = "date"
                        param.value = self.month + " " + self.year
                    if not unicode(param.value) and v == "date":
                        param.name = v
                        param.value = self.month + " " + self.year
                        changed = True
                    if unicode(param.name).isdigit() and unicode(param.value):
                        a = self.date_regex.match(unicode(param.value))
                        if a:
                            xmonth, xyear = a.group(1).lower(), a.group(2) + a.group(3)
                            if xmonth:
                                if xmonth in self.correct_dates.keys():
                                    monthstring = self.correct_dates[xmonth]
                                else:
                                    monthstring = xmonth.capitalize()
                            else:
                                monthstring = self.month
                            if a.group(2) and a.group(3):
                                yearstring = xyear
                            else:
                                yearstring = self.year
                            param.value = monthstring + " " + yearstring
                            param.name = "date"
                            changed = True
                        else: pass
                    if changed:
                        done = True
                        if temp.name.lower() in summary.keys():
                            summary[temp.name.lower()] += 1
                        else:
                            summary[temp.name.lower()] = 1
                if not temp.has_param('date'):
                    temp.add('date', self.month + " " + self.year)
                    if temp.name.lower() in summary.keys():
                        summary[temp.name.lower()] += 1
                    else:
                        summary[temp.name.lower()] = 1
                else:
                    old_date = str(temp.get('date').value).lower()
                    try:
                        date = parse(old_date)
                    except ValueError:
                        continue
                    month = date.month
                    year = date.year
                    day = date.day
                    if month:
                        monthstring = self.correct_dates[str(month)]
                    else:
                        monthstring = self.month
                    if year:
                        yearstring = str(year)
                    else:
                        yearstring = self.year
                    if 'currentmonthname' in old_date:
                        monthstring = self.month
                    if 'currentyear' in old_date:
                        yearstring = self.year
                    new_date = monthstring + " " + yearstring
                    temp.get('date').value = new_date
                    if old_date != new_date.lower() and not done:
                        if temp.name.lower() in summary.keys():
                            summary[temp.name.lower()] += 1
                        else:
                            summary[temp.name.lower()] = 1
                    else:
                        continue
        msg = ', '.join('{{%s}} (%s)' % (item, summary[item]) for item in summary.keys())
        return unicode(code), msg

    def strip_nonalnum(word):
        for start, c in enumerate(word):
            if c.isalnum():
               break
        for end, c in enumerate(word[::-1]):
            if c.isalnum():
                break
        return word[start:len(word) - end]

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
