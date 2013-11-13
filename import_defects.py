import sys
import os
import csv
from pyral import Rally, rallySettings

def main(args):

    # Settings
    rally_server = 'rally1.rallydev.com'
    user_id = 'user@company.com'
    rally_password = 'topsecret'
    my_workspace = 'My Workspace'
    my_project = 'My Project'
    jira_bugs_csv = 'jirabugs.csv'

    csvfile  = open(jira_bugs_csv, "rb")
    bugsreader = csv.reader(csvfile)

    # Rally Connection info
    rally = Rally(rally_server, user_id, rally_password, workspace=my_workspace, project=my_project)

    # Set logging
    rally.enableLogging('import_defects.log')

    # Get a handle to Rally Project
    proj = rally.getProject()

    # Jira Severity to Rally Severity Lookup
    jira2rally_sev_lookup = { 
                             "Critical" : "Crash/Data Loss",
                             "Severe" : "Crash/Data Loss",
                             "Major" : "Major Problem",
                             "Minor" : "Minor Problem","Cosmetic":"Cosmetic",
                             "Trivial" : "Cosmetic",
                             "None" : "Minor Problem" 
                             }

    # Column name to index mapping
    column_name_index_lookup = {0 : 'Summary',
                                1 : 'Priority',
                                2 : 'Severity',
                                3 : 'State',
                                4 : 'Description',
                                5 : 'Assignee',
                                6 : 'Submitter',
                                7 : 'RallyStoryID',
                                8 : 'JiraID'}

    # get the first user whose DisplayName is 'Mark Williams'
    user = rally.getUserInfo(name='Mark Williams').pop(0)

    rownum = 0
    for row in bugsreader:
        # Save header row.
        if rownum == 0:
            header = row
        else:
            print "Importing Defect count %d" % (rownum)
            colnum = 0
            for col in row:
                column_name = column_name_index_lookup[colnum]
                if column_name == "Summary":
                    summary = col
                elif column_name == "Priority":
                    priority = col
                elif column_name == "Severity":
                    severity = jira2rally_sev_lookup[col]
                elif column_name == "State":
                    state = col
                elif column_name == "Description":
                    desc = col
                elif column_name == "Assignee":
                    owner = rally.getUserInfo(name=col).pop(0)
                elif column_name == "Submitter":
                    submitted_by = rally.getUserInfo(name=col).pop(0)
                elif column_name == "RallyStoryID":
                    story_formatted_id = col
                elif column_name == "JiraID":
                    jira_id = col
                colnum += 1

            # Find the story to parent to in Rally
            query_criteria = 'FormattedID = "%s"' % story_formatted_id
            response = rally.get('Story', fetch=True, query=query_criteria)
            if response.errors:
                sys.stdout.write("\n".join(errors))
                sys.exit(1)
                
            defect_data = { 
                "Project"       : proj.ref,
                "Name"          : summary,
                "Priority"      : priority,
                "Severity"      : severity,
                "State"         : state,
                "Description"   : desc,
                "ScheduleState" : "Defined",
                "Owner"         : owner.ref,
                "SubmittedBy"   : submitted_by.ref,
                "JiraID"        : jira_id }

            if response.resultCount == 0:
                print "No Story %s found in Rally - No Parent will be assigned." % (story_formatted_id)
            else:
                print "Story %s found in Rally - Defect will be associated." % (story_formatted_id)
                story_in_rally = response.next()
                defect_data = { 
                    "Project"       : proj.ref,
                    "Name"          : summary,
                    "Priority"      : priority,
                    "Severity"      : severity,
                    "State"         : state,
                    "Description"   : desc,
                    "ScheduleState" : "Defined",
                    "Owner"         : owner.ref,
                    "SubmittedBy"   : submitted_by.ref,
                    "Requirement"   : story_in_rally.ref,
                    "JiraID"        : jira_id }
            try:
                defect = rally.create('Defect', defect_data)
            except Exception, details:
                sys.stderr.write('ERROR: %s \n' % details)
                sys.exit(1)
            print "Defect created, ObjectID: %s  FormattedID: %s" % (defect.oid, defect.FormattedID)
        rownum += 1

if __name__ == '__main__':
    main(sys.argv[1:])