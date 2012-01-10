#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Jim Miller'
__docformat__ = 'restructuredtext en'

from PyQt4.Qt import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                      QTextEdit, QComboBox, QCheckBox, QPushButton)

from calibre.gui2 import dynamic, info_dialog
from calibre.utils.config import JSONConfig

from calibre_plugins.fanfictiondownloader_plugin.dialogs \
    import (SKIP, ADDNEW, UPDATE, UPDATEALWAYS, OVERWRITE, OVERWRITEALWAYS,
             CALIBREONLY,collision_order)

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/fanfictiondownloader_plugin) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/fanfictiondownloader_plugin')

# Set defaults
prefs.defaults['personal.ini'] = get_resources('example.ini')
prefs.defaults['updatemeta'] = True
#prefs.defaults['onlyoverwriteifnewer'] = False
prefs.defaults['urlsfromclip'] = True
prefs.defaults['updatedefault'] = True
prefs.defaults['fileform'] = 'epub'
prefs.defaults['collision'] = OVERWRITE
prefs.defaults['deleteotherforms'] = False

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        horz = QHBoxLayout()
        label = QLabel('Default Output &Format:')
        horz.addWidget(label)
        self.fileform = QComboBox(self)
        self.fileform.addItem('epub')
        self.fileform.addItem('mobi')
        self.fileform.addItem('html')
        self.fileform.addItem('txt')
        self.fileform.setCurrentIndex(self.fileform.findText(prefs['fileform']))
        self.fileform.setToolTip('Choose output format to create.  May set default from plugin configuration.')
        self.fileform.activated.connect(self.set_collisions)
        label.setBuddy(self.fileform)
        horz.addWidget(self.fileform)
        self.l.addLayout(horz)

        horz = QHBoxLayout()
        label = QLabel('Default If Story Already Exists?')
        label.setToolTip("What to do if there's already an existing story with the same title and author.")
        horz.addWidget(label)
        self.collision = QComboBox(self)
        # add collision options
        self.set_collisions()
        i = self.collision.findText(prefs['collision'])
        if i > -1:
            self.collision.setCurrentIndex(i)
        # self.collision.setToolTip('Overwrite will replace the existing story.  Add New will create a new story with the same title and author.')
        label.setBuddy(self.collision)
        horz.addWidget(self.collision)
        self.l.addLayout(horz)

        self.updatemeta = QCheckBox('Default Update Calibre &Metadata?',self)
        self.updatemeta.setToolTip('Update metadata for story in Calibre from web site?')
        self.updatemeta.setChecked(prefs['updatemeta'])
        self.l.addWidget(self.updatemeta)

        # self.onlyoverwriteifnewer = QCheckBox('Default Only Overwrite Story if Newer',self)
        # self.onlyoverwriteifnewer.setToolTip("Don't overwrite existing book unless the story on the web site is newer or from the same day.")
        # self.onlyoverwriteifnewer.setChecked(prefs['onlyoverwriteifnewer'])
        # self.l.addWidget(self.onlyoverwriteifnewer)
        
        self.urlsfromclip = QCheckBox('Take URLs from Clipboard?',self)
        self.urlsfromclip.setToolTip('Prefill URLs from valid URLs in Clipboard when Adding New?')
        self.urlsfromclip.setChecked(prefs['urlsfromclip'])
        self.l.addWidget(self.urlsfromclip)

        self.updatedefault = QCheckBox('Default to Update when books selected?',self)
        self.updatedefault.setToolTip('The top FanFictionDownLoader plugin button will start Update if\n'+
                                      'books are selected.  If unchecked, it will always bring up \'Add New\'.')
        self.updatedefault.setChecked(prefs['updatedefault'])
        self.l.addWidget(self.updatedefault)

        self.deleteotherforms = QCheckBox('Delete other existing formats?',self)
        self.deleteotherforms.setToolTip('Check this to automatically delete all other ebook formats when updating an existing book.\nHandy if you have both a Nook(epub) and Kindle(mobi), for example.')
        self.deleteotherforms.setChecked(prefs['deleteotherforms'])
        self.l.addWidget(self.deleteotherforms)
        
        self.label = QLabel('personal.ini:')
        self.l.addWidget(self.label)

        self.ini = QTextEdit(self)
        self.ini.setLineWrapMode(QTextEdit.NoWrap)
        self.ini.setText(prefs['personal.ini'])
        self.l.addWidget(self.ini)

        self.defaults = QPushButton('View Defaults', self)
        self.defaults.setToolTip("View all of the plugin's configurable settings\nand their default settings.")
        self.defaults.clicked.connect(self.show_defaults)
        self.l.addWidget(self.defaults)
        
        reset_confirmation_button = QPushButton(_('Reset disabled &confirmation dialogs'), self)
        reset_confirmation_button.setToolTip(_(
                    'Reset all show me again dialogs for the FanFictionDownLoader plugin'))
        reset_confirmation_button.clicked.connect(self.reset_dialogs)
        self.l.addWidget(reset_confirmation_button)
        
    def set_collisions(self):
        prev=self.collision.currentText()
        self.collision.clear()
        for o in collision_order:
            if self.fileform.currentText() == 'epub' or o not in [UPDATE,UPDATEALWAYS]:
                self.collision.addItem(o)
        i = self.collision.findText(prev)
        if i > -1:
            self.collision.setCurrentIndex(i)
        
    def save_settings(self):
        prefs['fileform'] = unicode(self.fileform.currentText())
        prefs['collision'] = unicode(self.collision.currentText())
        prefs['updatemeta'] = self.updatemeta.isChecked()
        prefs['urlsfromclip'] = self.urlsfromclip.isChecked()
        prefs['updatedefault'] = self.updatedefault.isChecked()
#        prefs['onlyoverwriteifnewer'] = self.onlyoverwriteifnewer.isChecked()
        prefs['deleteotherforms'] = self.deleteotherforms.isChecked()
        
        ini = unicode(self.ini.toPlainText())
        if ini:
            prefs['personal.ini'] = ini
        else:
            # if they've removed everything, clear it so they get the
            # default next time.
            del prefs['personal.ini']
        
    def show_defaults(self):
        text = get_resources('defaults.ini')
        ShowDefaultsIniDialog(self.windowIcon(),text,self).exec_()

    def reset_dialogs(self):
        for key in dynamic.keys():
            if key.startswith('fanfictiondownloader_') and key.endswith('_again') \
                                                  and dynamic[key] is False:
                dynamic[key] = True
        info_dialog(self, _('Done'),
                _('Confirmation dialogs have all been reset'), show=True)

        
class ShowDefaultsIniDialog(QDialog):

    def __init__(self, icon, text, parent=None):
        QDialog.__init__(self, parent)
        self.resize(600, 500)
        self.l = QVBoxLayout()
        self.setLayout(self.l)
        self.label = QLabel("Plugin Defaults (Read-Only)")
        self.label.setToolTip("These all of the plugin's configurable settings\nand their default settings.")
        self.setWindowTitle(_('Plugin Defaults'))
        self.setWindowIcon(icon)
        self.l.addWidget(self.label)
        
        self.ini = QTextEdit(self)
        self.ini.setToolTip("These all of the plugin's configurable settings\nand their default settings.")
        self.ini.setLineWrapMode(QTextEdit.NoWrap)
        self.ini.setText(text)
        self.ini.setReadOnly(True)
        self.l.addWidget(self.ini)
        
        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.hide)
        self.l.addWidget(self.ok_button)
        