#!/usr/bin/env python
"""
Test . Print voltages/currents
 -*- coding: UTF-8 -*-
"""

import ConfigParser
import sys, os
import glob


class Config:
    """
    Class handling script parameters
    
    """
    def __init__(self,  config_file=None):
        self.cphandle = ConfigParser.ConfigParser()
        if config_file is None:
            config_file = sys.argv[0][:-3] +'.ini'
            
        self.cphandle.read(config_file)
                    
    def get_option(self, section, option = None):
        """
        Returns requested option or 
        list of options in section if NO option is given
        """
        self.options = {}           # List of options in section
        if option == None:
            for option in self.cphandle.options(section):
                self.options[option] = self.cphandle.get(section, option)
            return self.options
        else:
            return self.cphandle.get(section, option)
	  
    def get_sections(self):
      """
      Returns list of sections
      """
      return self.cphandle.sections()
    
    

