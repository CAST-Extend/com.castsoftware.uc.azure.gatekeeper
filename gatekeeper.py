import json
from argparse import ArgumentParser
import pandas as pd
import requests
from sqlalchemy import create_engine
from generate_application_template import generate_application_template
import psycopg2

def get_application_guid(console_url, console_api_key, app_name):
    url=f"{console_url}/api/applications"
    headers = {
        "x-api-key": console_api_key
    }

    try:
        #fetching the Application list and details.
        rsp = requests.get(url, headers=headers)
        # print(rsp.status_code)
        if rsp.status_code == 200:
            apps = json.loads(rsp.text) 
            for app in apps['applications']:
                if app["name"] == app_name:
                    return app["guid"] 
            print(f'{app_name} application not present in AIP Console')

        else:
            print("Some error has occured! ")
            print(rsp.text)

    except Exception as e:
        print('some exception has occured! \n Please resolve them or contact developers')
        print(e)

def get_central_schema(console_url, console_api_key, guid):
    url=f"{console_url}/api/aic/applications/{guid}"
    headers = {
        "x-api-key": console_api_key
    }

    try:
        #fetching the app schemas.
        rsp = requests.get(url, headers=headers)
        # print(rsp.status_code)
        if rsp.status_code == 200:
            data = json.loads(rsp.text) 

            for i in range(len(data["schemas"])):
                if data["schemas"][i]["type"] == 'central':
                    return data["schemas"][i]["name"]

        else:
            print("Some error has occured! ")
            print(rsp.text)

    except Exception as e:
        print('some exception has occured! \n Please resolve them or contact developers')
        print(e)


if __name__ == "__main__":

    parser = ArgumentParser()
 
    parser.add_argument('-app_name','--app_name',required=True,help='Application Name')
    parser.add_argument('-console_url', '--console_url', required=True, help='AIP Console URL')
    parser.add_argument('-console_api_key', '--console_api_key', required=True, help='AIP Console API KEY')
    parser.add_argument('-css_host','--css_host',required=True,help='CSS Host')
    parser.add_argument('-css_database','--css_database',required=True,help='CSS Database')
    parser.add_argument('-css_port','--css_port',required=True,help='CSS Port')
    parser.add_argument('-css_user','--css_user',required=True,help='CSS User')
    parser.add_argument('-css_password','--css_password',required=True,help='CSS Pasword')
    parser.add_argument('-html_template_path','--html_template_path',required=True,help='ApplicationHealthTemplate.htm Path')
    parser.add_argument('-generated_html_path','--generated_html_path',required=True,help='Output Path to store generated HTML file')
    parser.add_argument('-o','--output',required=False,help='Output Folder')
    parser.add_argument('-PrInfo', '--PrInfo', required=True, help='PR Information')
    parser.add_argument('-PrURL', '--PrURL', required=True, help='PR URL')

    args=parser.parse_args()

    # args.PrInfo = [
    # {
    #     "RepositoryName": "FSL.MyProjectHQ.CrewHQ.API.Sandbox",
    #     "Status": "completed",
    #     "PullRequestId": 22826,
    #     "SourceBranch": "refs/heads/feature/SLA-develop-2",
    #     "TargetBranch": "refs/heads/develop",
    #     "CreatedBy": "Sagar Shenvi",
    #     "Reviewers": "William Gardella Alice Gabrylski",
    #     "CreatedDate": {
    #     "value": "/Date 1700602964088 /",
    #     "DisplayHint": 2,
    #     "DateTime": "Tuesday November 21 2023 4:42:44 PM"
    #     },
    #     "ClosedDate": {
    #     "value": "/Date 1700603058870 /",
    #     "DisplayHint": 2,
    #     "DateTime": "Tuesday November 21 2023 4:44:18 PM"
    #     }
    # },
    # {
    #     "RepositoryName": "FSL.MyProjectHQ.CrewHQ.API.Sandbox",
    #     "Status": "completed",
    #     "PullRequestId": 22806,
    #     "SourceBranch": "refs/heads/feature/SLA-develop",
    #     "TargetBranch": "refs/heads/develop",
    #     "CreatedBy": "Sagar Shenvi",
    #     "Reviewers": "William Gardella Matt Spiewacki",
    #     "CreatedDate": {
    #     "value": "/Date 1700583673682 /",
    #     "DisplayHint": 2,
    #     "DateTime": "Tuesday November 21 2023 11:21:13 AM"
    #     },
    #     "ClosedDate": {
    #     "value": "/Date 1700590873904 /",
    #     "DisplayHint": 2,
    #     "DateTime": "Tuesday November 21 2023 1:21:13 PM"
    #     }
    # }
    # ]

    # print(args.PrInfo)

    # args.PrURL = "https://dev.azure.com/fsllc/Portfolio/_git/FSL.MyProjectHQ.CrewHQ.API.Sandbox/pullrequest/22826,https://dev.azure.com/fsllc/Portfolio/_git/FSL.MyProjectHQ.CrewHQ.API.Sandbox/pullrequest/22806"

    args.PrURL = args.PrURL.split(',')

    print(type(args.PrInfo))
    print(args.PrInfo)

    # Convert the string to a Python object
    args.PrInfo = json.loads(args.PrInfo)

    for item in args.PrInfo:
        for url in args.PrURL:
            if str(item["PullRequestId"]) in url:
                item["PrURL"]=url

    # print(args.PrInfo)

    print('Checking if there are new critical violations added in this version.............')

    guid = get_application_guid(args.console_url, args.console_api_key, args.app_name)
    central_schema = get_central_schema(args.console_url, args.console_api_key, guid)


    db_uri = f"postgresql://{args.css_user}:{args.css_password}@{args.css_host}:{args.css_port}/{args.css_database}"

    # Create an SQLAlchemy engine
    engine  = create_engine(db_uri)

    # Create a connection and a cursor
    connection = engine.connect()
    cursor = connection.connection.cursor()

    query = f"""set search_path={central_schema};"""
    cursor.execute(query)

    snapshot_date_query = """select functional_date from dss_snapshots"""

    # Execute the query
    cursor.execute(snapshot_date_query)

    # Fetch all the rows (column values) from the result
    snapshot_date_list = cursor.fetchall()

    # Assuming you have a datetime object like this
    latest_snapshot_date = snapshot_date_list[-1]

    # Convert it to the "YYYY-MM-DD" format
    latest_snapshot_date = latest_snapshot_date[0].strftime("%Y-%m-%d")

    if len(snapshot_date_list) == 1:
        print(f'There is no previous snapshot for the application -> {args.app_name}.')
        exit(0)
    else:
        # Assuming you have a datetime object like this
        previous_snapshot_date = snapshot_date_list[-2]

        # Convert it to the "YYYY-MM-DD" format
        previous_snapshot_date = previous_snapshot_date[0].strftime("%Y-%m-%d")

    total_violation_query = """SELECT count(distinct(concat(cvs.diag_id,cvs.object_id)))
    FROM csv_violation_statuses cvs , csv_quality_tree cqt
    WHERE cqt.metric_id = diag_id and m_crit =1
    AND cvs.snaphot_id IN (SELECT max (snapshot_id ) FROM dss_snapshots);"""

    # Execute the query
    cursor.execute(total_violation_query)

    # Fetch all the rows (column values) from the result
    total = cursor.fetchall()


    total = total[0][0]

    added_violation_query = """SELECT count(distinct(concat(cvs.diag_id,cvs.object_id)))
    FROM csv_violation_statuses cvs , csv_quality_tree cqt
    WHERE cqt.metric_id = diag_id and m_crit =1
    AND cvs.snaphot_id IN (SELECT max (snapshot_id ) 
    FROM dss_snapshots) AND cvs.violation_status='Added'"""

    # Execute the query
    cursor.execute(added_violation_query)

    # Fetch all the rows (column values) from the result
    added = cursor.fetchall()

    added = added[0][0]


    # Define your SQL query
    # violations_query = """SELECT distinct cvs.diag_name,cvs.object_name,cvs.violation_status
    # FROM csv_violation_statuses cvs , csv_quality_tree cqt
    # WHERE cqt.metric_id = diag_id and m_crit =1
    # AND cvs.snaphot_id IN (SELECT max (snapshot_id ) FROM dss_snapshots) AND cvs.violation_status='Added'"""

    violations_query = """SELECT
           cvs.diag_id "Rule_ID", 
           cvs.diag_name "Rule_Name",
           --cvs.object_id,
           cvs.object_name,
           dst.source_path "File_Path",
           dcb.start_line,
           dcb.end_line, 
           cvs.violation_status
    FROM 
     	csv_violation_statuses cvs , 
     	csv_quality_tree cqt,
    	dss_metric_results dmr
    	left join dss_code_bookmarks dcb on dcb.position_id = dmr.position_id 
    			and dcb.object_id = dmr.object_id 
    	join dss_source_texts dst on dcb.local_source_id = dst.local_source_id 
    WHERE 
        cqt.metric_id = diag_id and m_crit =1 and cqt.b_criterion_id = 60017
    and cvs.snaphot_id IN (SELECT max (snapshot_id ) FROM dss_snapshots)
    and cqt.metric_id = dmr.metric_id -1 
    and cvs.snaphot_id = dmr.snapshot_id 
    and cvs.object_id = dmr.object_id 
    AND cvs.violation_status='Added'
    and dcb."rank" = 1"""

    cursor.execute(violations_query)

    # Fetch the result into a DataFrame
    violations_df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    # Drop the specified columns
    #columns_to_drop = ['diag_id', 'object_id']
    #violations_df = violations_df.drop(columns=columns_to_drop)

    new_column = {'Rule_ID':'Rule ID', 'Rule_Name':'Rule Name', 'object_name':'Object Name', 'File_Path':'File Path', 'start_line':'Start Line', 'end_line':'End Line', 'violation_status':'Violation Status'}

    violations_df = violations_df.rename(columns=new_column)

    # Define the output Excel file path
    excel_file_path = args.generated_html_path + f"\ApplicationHealth_{args.app_name}.xlsx"

    # Write the data to an Excel sheet
    violations_df.to_excel(excel_file_path, sheet_name="violations", index=False)

    print(f"Violations data has been exported to {excel_file_path}")

	# Drop the specified columns
    # columns_to_drop = ['Violation Status']
    # violations_df_for_html = violations_df.drop(columns=columns_to_drop)
    # print(violations_df_for_html)

    # data = {'Violation Name': ['Avoid comparing passwords against hard-coded strings Avoid comparing passwords against hard-coded strings Avoid comparing passwords against hard-coded strings'],
    #         'Object Name': ['FSL.MyProjectHQ.CrewHQ.API.Startup.ConfigureServices']}
    # violations_df_for_html = pd.DataFrame(data)


    # Define your SQL query
    sql_query = """/*
    Query to give comparison of latest and previous health factors with % variation
    */
    --select * from dss_snapshots where metric_id in (10151,10152)
    select current_snapshot.metric_name, round(prev_snapshot.metric_num_value,2) Previous, round(current_snapshot.metric_num_value,2) Latest, 
    case when prev_snapshot.metric_num_value <> 0 then round(((current_snapshot.metric_num_value - prev_snapshot.metric_num_value) * 100 / prev_snapshot.metric_num_value),2) else 0 end Change
    from
    (select dmt.metric_id, dmt.metric_name, dmr.metric_num_value, metric_value_index
    from dss_metric_results dmr, dss_metric_types dmt, dss_objects o
    where
    dmr.metric_id = dmt.metric_id
    and dmr.object_id = o.object_id
    and o.object_type_id = -102
    and snapshot_id = (select max(snapshot_id) from dss_snapshots)
    and
    (dmr.metric_value_index = 0 and dmr.metric_id in (60010,60011,60012,60013,60014,60016,60017)
    or
    dmr.metric_value_index = 1 and dmr.metric_id in (10151,10152))
    ) current_snapshot,
    (select dmt.metric_id, dmt.metric_name, metric_num_value, metric_value_index
    from dss_metric_results dmr, dss_metric_types dmt, dss_objects o
    where
    dmr.metric_id = dmt.metric_id
    and dmr.object_id = o.object_id
    and o.object_type_id = -102
    and snapshot_id = (select max(snapshot_id) from dss_snapshots where snapshot_id < (select max(snapshot_id) from dss_snapshots))
    and 
    (dmr.metric_value_index = 0 and dmr.metric_id in (60010,60011,60012,60013,60014,60016,60017)
    or
    dmr.metric_value_index = 1 and dmr.metric_id in (10151,10152))
    ) prev_snapshot
    where
    current_snapshot.metric_id = prev_snapshot.metric_id"""

    cursor.execute(sql_query)

    # Fetch the result into a DataFrame
    df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    new_column_names = {'metric_name':'', 'previous':'Previous', 'latest':'Latest', 'change':'Change'}
    df = df.rename(columns=new_column_names)

    combined = df.drop([0, 1])

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # set value of the variable
    #log.info(f'{added} new violations added')
    if added == 0: 
        value = 'pass'
        print('Info : As no added critical violations found. The build will pass.')
    else:
        value = 'fail'
        print(f"Info : {added} added critical violations found. Please investigate/fix the violation before merge. The build will fail") 

    
    violations_data = violations_df.to_dict(orient='records')

    generate_application_template(combined, args.app_name, latest_snapshot_date, previous_snapshot_date, added, total, args.html_template_path, args.generated_html_path, violations_data, args.PrInfo)

    name = 'violations'    
    # set variable
    print(f'##vso[task.setvariable variable={name};]{value}')

    exit(added)
