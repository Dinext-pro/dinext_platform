"""Final row policies must remain conjunctive after ordinary shares and constraints."""
import sqlite3
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.model.db_query import DatabaseQuery


class TestFinalPermissionQueryConditions(unittest.TestCase):
	def setUp(self):
		self.context = ExitStack()
		self.addCleanup(self.context.close)
		self.permissions = {"read": 1}
		self.shared = ["DENIED"]
		self.hooks = {"Protected": [lambda user, doctype: f"`tab{doctype}`.`policy` = 1"]}
		self.context.enter_context(patch.object(frappe, "db", SimpleNamespace(db_type="mariadb",
			escape=lambda value, **kwargs: "'" + str(value).replace("'", "''") + "'")))
		self.context.enter_context(patch.object(frappe, "flags", frappe._dict()))
		self.context.enter_context(patch.object(frappe, "get_system_settings", return_value=True))
		self.context.enter_context(patch("frappe.model.db_query.get_server_script_map", return_value={}))
		self.context.enter_context(patch.object(frappe.permissions, "get_role_permissions", side_effect=lambda *a, **kw: self.permissions))
		self.context.enter_context(patch.object(frappe.permissions, "get_user_permissions", return_value={
			"Workflow": [{"doc": "Allowed", "applicable_for": "Protected"}]}))
		self.context.enter_context(patch.object(frappe.share, "get_shared", side_effect=lambda *a, **kw: self.shared))
		self.context.enter_context(patch.object(frappe, "get_hooks", side_effect=lambda name, *args: self.hooks if name == "final_permission_query_conditions" else {}))
		self.connection = sqlite3.connect(":memory:")
		self.addCleanup(self.connection.close)
		self.connection.execute("create table tabProtected (name text, workflow text, owner text, policy int)")
		self.connection.executemany("insert into tabProtected values (?, ?, ?, ?)", [
			("ALLOWED", "Allowed", "reader", 1), ("DENIED", "Other", "other", 0),
			("CONSTRAINED", "Other", "other", 1)])

	def query(self, doctype="Protected"):
		query = DatabaseQuery(doctype, user="reader")
		query.tables = [f"`tab{doctype}`"]
		query.flags.ignore_permissions = False
		query._doctype_meta = SimpleNamespace(istable=False, get_link_fields=lambda: [
			{"fieldname": "workflow", "options": "Workflow"}])
		query.get_permission_query_conditions = lambda: "1=1"
		return query

	def names(self, query):
		condition = query.build_match_conditions()
		conditions = [*query.conditions, condition]
		where = " and ".join(f"({item})" for item in conditions if item) or "1=1"
		return [row[0] for row in self.connection.execute(f"select name from tabProtected where {where} order by name")]

	def test_user_permissions_and_outer_share_do_not_bypass_final_policy(self):
		self.assertEqual(self.names(self.query()), ["ALLOWED"])

	def test_owner_constraint_and_share_do_not_bypass_final_policy(self):
		self.permissions = {"read": 1, "has_if_owner_enabled": True, "if_owner": {"read": 1}}
		self.assertEqual(self.names(self.query()), ["ALLOWED"])

	def test_only_shared_path_still_applies_final_policy(self):
		self.permissions = {}
		with patch("frappe.model.db_query.has_any_user_permission_for_doctype", return_value=False):
			self.assertEqual(self.names(self.query()), [])

	def test_standard_user_constraints_remain_when_policy_allows(self):
		self.shared = []
		self.assertEqual(self.names(self.query()), ["ALLOWED"])

	def test_unconfigured_doctype_keeps_ordinary_share_behavior(self):
		self.hooks = {}
		self.assertEqual(self.names(self.query()), ["ALLOWED", "DENIED"])

	def test_trusted_query_skips_final_hooks(self):
		query = self.query()
		query.flags.ignore_permissions = True
		self.hooks = {"Protected": [lambda *a, **kw: self.fail("trusted queries must skip final hooks")]}
		self.assertTrue(hasattr(query, "get_final_permission_query_conditions"), "final query capability is required")
		self.assertEqual(query.get_final_permission_query_conditions(), "")

	def test_linked_join_uses_final_policy_with_its_alias(self):
		query = self.query()
		condition = query._build_linked_join_conditions("Protected", "protected_alias")
		rows = self.connection.execute(f"select name from tabProtected protected_alias where {condition}")
		self.assertEqual({row[0] for row in rows}, {"ALLOWED", "CONSTRAINED"})

	def test_multiple_final_policies_cannot_widen_each_other(self):
		self.hooks = {"Protected": [lambda *args, **kwargs: "policy=1 or name='DENIED'",
			lambda *args, **kwargs: "name!='DENIED'"]}
		self.assertEqual(self.names(self.query()), ["ALLOWED"])
