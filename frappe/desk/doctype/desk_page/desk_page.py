# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.modules.export_file import export_to_files
from frappe.model.document import Document

class DeskPage(Document):
	def on_update(self):
		export_to_files(record_list=[['Desk Page', self.name]], record_module=self.module)
