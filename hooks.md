### List of Hooks

#### Application Name and Details

1. `app_name` - slugified name e.g. "frappe"
1. `app_title` - full title name e.g. "Frappe"
1. `app_publisher`
1. `app_description`
1. `app_version`

#### Install

1. `before_install` - method
1. `after_install` - method


#### Javascript / CSS Builds

1. `app_include_js` - include in "app"
1. `app_include_css` - assets/frappe/css/splash.css

1. `web_include_js` - assets/js/frappe-web.min.js
1. `web_include_css` - assets/css/frappe-web.css

#### Desktop

1. `get_desktop_icons` - method to get list of desktop icons
1. `awesomebar_search` - method(txt) returning extra Awesome Bar results (`label`, `description`, `route`, `index`). `route` may be a desk route list, an in-app path (`/desk/...`), or an `http(s)://` URL.

#### Notifications

1. `notification_config` - method to get notification configuration

#### Permissions

1. `permission_query_conditions:[doctype]` - method to return additional query conditions at time of report / list etc.
1. `has_permission:[doctype]` - method to call permissions to check at individual level
1. `final_permission_query_conditions:[doctype]` - opt-in conditions ANDed after ordinary role/user/share conditions; see below.


#### Final permission query conditions (Dinext v15)

Use `final_permission_query_conditions = {"Protected DocType": "app.permissions.final_conditions"}`
when a document share must not override an app's row policy. The callable receives
`user` and `doctype` and returns a trusted, escaped SQL condition or an empty string.
Conditions are ANDed after the complete role/User Permission/owner/DocShare expression,
including the only-shared path. Linked-document JOIN policies apply the same hook
using their table alias. Unconfigured DocTypes keep their existing behavior.
`ignore_permissions=True` bypasses this hook for explicitly trusted queries.

This small platform patch is required for Dinext approval audit isolation:
`permission_query_conditions` is evaluated before an outer DocShare OR, so an app
cannot express this policy through the existing hook alone. Endpoint overrides do
not cover server-side `frappe.get_list`. The patch avoids global monkeypatching and
keeps ordinary constraints in place. Apps can require
`DatabaseQuery.final_permission_query_conditions_version >= 1` and fail closed on
older platforms; this attribute describes the hook contract, not the Frappe version.

For v15 updates, retain the final AND after sharing and run
`frappe.tests.test_final_permission_query_conditions` plus the consuming app's endpoint
tests. For v16, first check whether upstream supplies an equivalent final-policy hook;
port this extension only if needed. Remove the local patch and capability guard after
migrating consumers to a verified upstream equivalent. No schema migration is needed.
