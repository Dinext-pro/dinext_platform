# Dinext source upgrade

Selected upstream release: [v15.123.0](https://github.com/frappe/frappe/releases/tag/v15.123.0).
Immutable upstream commit: `62fa5cc844a463a75e97962f03d6eafd536a5749`.
Dinext integration line: `dinext/main/v15`.

The merge has two parents: the previous Dinext tip `25ce06e456f6952d5e13822da983f8a336bae6e1` and the upstream tag. The reconciliation base is the current vendor snapshot `e56f5bcecd5de37f18a8fcdf27983ede60c35fe7`. That vendor ref is a rewritten snapshot and is not moved.

## Preserved company changes

Keep the existing Dinext CI profile (`.github/dinext-ci.json` mode `platform-smoke`), policy workflow, validation workflow and the README note that names `dinext/main/v15`. Upstream product workflows stay under `.github/imported-workflows-disabled/`. There is no product patch on top of the selected tag.

## Verification and activation

`dinext/vendor/v15` stays at the previous snapshot. This pull request does not change a running site, a Support or Prod manifest, or an existing tag.

The paired ERPNext line is `dinext/upgrade/v15.123.0` in `Dinext-pro/dinext_erp`. The Dinext acceptance workflow installs this revision together with that branch on a fresh bench, migrates, builds and pings. Cypress acceptance then completes setup on that same disposable site and runs the upstream `cypress/integration/awesome_bar.js` spec. Those jobs are the isolated pair check. They are not a substitute for the repository validation workflow, and a skipped job is not acceptance.

Node 18 is sufficient for this Frappe release (`engines.node` is `>=18`). A runtime cutover still requires a backup, the merged integration commit and a separate site migrate.

## Verification record

The result of this revision is the GitHub check runs on this pull request: `Validation / Repository checks`, `Validation / App unit tests`, `Compatibility acceptance` and `Cypress acceptance`. This file does not claim those runs passed before they complete.
