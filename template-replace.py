#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pywikibot import Page

class TemplateReplacer():
    def __init__(self, site, names, target):
        """
        Initiates a TemplateReplacer object.
        
        The purpose of this task is to recurse over all pages
        that use a particular template and substitute it for another.
        This is a pretty common request on Wikipedia, therefore
        I created a blanket software to use as necessary. However,
        this is FOSS, so you may use it as you would.
        
        @param site: a Pywikibot Site object.
        @type site: Site
        @param names: an array of templates to be changed.
        @type names: list
        @param target: name of template that templates in `name` will
            be replaced by.
        @type target: string
        """
        # Turn the values passed to the template into global vars
        self.site = site
        self.names = names
        self.target = target
        
    def deploy_task(self):
        # Deploys the task to replace each occurence of the templates
        # in self.names with self.target.
        if type(self.names) == list or not len(self.names) == 1:
            pass
