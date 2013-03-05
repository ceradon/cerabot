import re
import sys
import codecs
from cerabot import bot
from cerabot import exceptions
from datetime import datetime

class DateTemplates(bot.Bot):
    """Bot to date maintenance templates that have none."""
    name = "template_dater"
    task = 1

    def __init__(self):
        """Ensures DateTemplates is the child of the
        `Bot` class.
        """
        self.pages = []
        self._to_date = []
        self._redirects = {}
        self.year = datetime.today().strftime('%Y')
        self.month = datetime.today().strftime('%B')
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
        super(DateTemplates, self).__init__()

    def _load_templates(self):
        """Load the templates we have to date."""
        templates_page = self.access_page.Page(self.site, 
                "Wikipedia:AutoWikiBrowser/Dated templates")
        text = templates_page.getWikiText()
        code = self.parser.parse(text)
        for template in code.filter_templates():
            if template.name.lower() == "tl":
                self._to_date.append(template.get(1)
                        .value.lower())
        
        """Load the redirects to the templates we
        must date.
        """
        redirects_page = self.access_page.Page(self.site, 
                "Wikipedia:AutoWikiBrowser/Template redirects")
        text_ = redirects_page.getWikiText()
        try:
            section = text_[text.find(
                    "===Maintenance templates===")
                    +len("===Maintenance templates==="):
                    text_.find("===Navbox templates===")
                    +len("===Navbox templates===")]
        except Exception:
            pass
        for line in section.splitlines():
            if not '→' in line:
                continue
            split = line.split('→')
            if len(split) != 2:
                continue
            code_1 = self.parser.parse(split[0])
            code_2 = self.parser.parse(split[1])
            destination = code_2.filter_templates()[0].get(1).value
            for template in code_1.filter_templates():
                if template.name.lower() == "tl":
                    name = template.get(1).value
                    self._redirects[name.lower()] = destination
                    self._redirects[destination.lower()] = destination
        return

    def _in_use(self, text):
        """Checks if the page is in use."""
        code = self.parser.parse(text)
        templates = code.filter_templates()
        for template in templates:
            if 'in use' in template.lower():
                return True
        return False

    def _generate_pages(self):
        """Generates a list of all pages to date."""
        category_object = self.access_category.Category(self.site, 
                "Category:Wikipedia maintenance categories sorted by month")
        members = category_object.getAllMembers(titleonly=True, 
                                                namespaces=[14])
        for item in members:
            item_object = self.access_category.Category(self.site, item)
            for page in item_object.getAllMembers(namespaces=[0]):
                yield page
        return

    def setup(self):
        self.pages = self._generate_pages()
        self._load_templates()
    
    def run_bot(self, page=None):
        summary = {}
        if page:
            text = page.getWikiText()
            code = self.parser.parse(text)
            templates = code.filter_templates(recursive=True)
            for template in templates:
                name = template.name.lower().strip()
                if name in self._redirects.keys():
                    new_name = self._redirects[name]
                    if new_name.lower() != name:
                        template.name = new_name
                if template.name.lower() in self._to_date:
                    if not template.has_param("date"):
                        template.add('date', datetime.today()
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
            if page.isRedir():
                continue
            if self._in_use(page.getWikiText()):
                print "Page "+page.title+" is in use."
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
            except self.access_wiki.WikiError as e:
                print "Exception was raised: {1}".format(e)
                continue

if __name__ == '__main__':
    bot = DateTemplates()
    bot.run()
