from pyforms.Controls import ControlTreeView
from pyforms.Controls import ControlTree
from PyQt4 import QtGui
from PyQt4.QtCore import QSize
import os, glob
from core.utils.tools import make_lambda_func


class AvailablePluginsTree(ControlTree):

	def __init__(self, parent):
		super(AvailablePluginsTree, self).__init__('List of plugins')
		self.mainwindow = parent
		self.setHeaderHidden(True)
		self.setIconSize( QSize(16, 16) )
		self.__add2Node( self.invisibleRootItem(), 'plugins' )

		self.item_double_clicked_event = self.__item_double_clicked_event

	def __readPluginTXT(self, filename):
		f = open(filename, 'r')
		str2eval = "".join(f.readlines()).strip()
		config = eval(str2eval)
		f.close()
		return config

	def __add2Node(self, node, searchpath):
		searchstr 	= os.path.join(searchpath,'*','folder.txt')
		files 		= glob.glob(searchstr)

		for filename in files:
			path,_ = os.path.split(filename)
			config = self.__readPluginTXT(filename)

			treeItem = self.create_child(
				config.get('name', ''),
				parent=node,
				icon=os.path.join(path,config.get('icon', ''))
			)
			
			if 'class' in config:
				treeItem.pluginfile  = path
				treeItem.pluginclass = config['class']

				self.add_popup_menu_option(
					'Add to project', 
					make_lambda_func(self.__add_2_project, treeItem=treeItem),
					item=treeItem
				)
			
			self.__add2Node(treeItem, path)

	def __add_2_project(self, treeItem):
		self.mainwindow.addModule2Project(treeItem)

	def __item_double_clicked_event(self, item):
		if hasattr(item, 'pluginfile') and hasattr(item, 'pluginclass'):
			self.mainwindow.addModule2Project(treeItem)
		