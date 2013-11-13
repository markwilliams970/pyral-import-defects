pyral-import-defects
====================

Description:

- An example of using Pyral (Python Rally API) to import defects from a Jira CSV export, into Rally
- Assumes RallyStoryID is a Rally Formatted ID assigned to the Jira bug and exported to the CSV
- Associates Jira bug to Rally Story, if found, during import

Requires:

- [Requests 2.0.0](http://github.com/kennethreitz/requests)
- [Pyral 0.9.4](https://pypi.python.org/pypi/pyral)

Pyral source code on Github:

- https://github.com/RallyTools/RallyRestToolkitForPython#installation