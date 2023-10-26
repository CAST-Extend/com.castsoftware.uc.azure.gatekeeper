from cast_common.aipRestCall import AipRestCall
from cast_common.logger import Logger,INFO
from cast_common.util import format_table
from pandas import ExcelWriter, Series,merge,options, DataFrame
from argparse import ArgumentParser
from os.path import abspath,exists
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
import psycopg2

from generate_application_template import generate_application_template
from sendmail import send_email

if __name__ == "__main__":

    measures = {
        '60017':'TQI',
        '60013':'Robustness',
        '60014':'Efficiency',
        '60016':'Security',
        '60011':'Transferability',
        '60012':'Changeability'
    }

    parser = ArgumentParser()
    # parser.add_argument('-r','--restURL',required=True,help='CAST REST API URL')
    # parser.add_argument('-u','--user',required=True,help='CAST REST API User Name')
    # parser.add_argument('-p','--password',required=True,help='CAST REST API Password')
    parser.add_argument('-app_name','---app_name',required=True,help='Application Name')
    parser.add_argument('-css_host','--css_host',required=True,help='CSS Host')
    parser.add_argument('-css_database','--css_database',required=True,help='CSS Database')
    parser.add_argument('-css_port','--css_port',required=True,help='CSS Port')
    parser.add_argument('-css_user','--css_user',required=True,help='CSS User')
    parser.add_argument('-css_password','--css_password',required=True,help='CSS Pasword')
    parser.add_argument('-html_template_path','--html_template_path',required=True,help='ApplicationHealthTemplate.htm Path')
    parser.add_argument('-generated_html_path','--generated_html_path',required=True,help='Output Path to store generated HTML file')
    # parser.add_argument('-sender','--sender',required=True,help='Sender Email ID')
    # parser.add_argument('-reciever','--reciever',required=True,help='Reciever Email ID List')
    # parser.add_argument('-smtp_host','--smtp_host',required=True,help='SMTP Host URL')
    # parser.add_argument('-smtp_port','--smtp_port',required=True,help='SMTP PORT NUMBER')
    # parser.add_argument('-smtp_user','--smtp_user',required=True,help='SMTP USERNAME')
    # parser.add_argument('-smtp_pass','--smtp_pass',required=True,help='SMTP PASSWORD')
#    parser.add_argument('-f','--healthFactor',required=False,default='60017',help='Health Factor Code')
    parser.add_argument('-o','--output',required=False,help='Output Folder')

    args=parser.parse_args()
    log = Logger()

    # aip = AipRestCall(args.restURL, args.user, args.password,log_level=INFO)
    # domain_id = aip.get_domain(f'{args.application}_central')
    # if domain_id==None:
    #     log.info(f'Application not found: {args.application}.')
    #     log.info(f'Please validate application - {args.application} in the Engineering Health Dashboard.')
    # else:
    #     total = 0
    #     added = 0
    #     snapshot = aip.get_latest_snapshot(domain_id)
    #     if not bool(snapshot):
    #         log.error(f'No snapshots found: {args.application}')
    #         exit (-1)
    #     snapshot_id = snapshot['id']

    #     base='./'
    #     if not args.output is None:
    #         base = args.output

    #     s = datetime.now().strftime("%Y%m%d-%H%M%S")
    #     file_name = abspath(f'{base}/violations-{args.application}-{s}.xlsx')
    #     writer = ExcelWriter(file_name, engine='xlsxwriter')

    #     first=True
    #     for code in measures:
    #         name = measures[code]
    #         df=aip.get_rules(domain_id,snapshot_id,code,critical=True,non_critical=False,start_row=1,max_rows=999999)
    #         if not df.empty:
    #             if first:
    #                 total=len(df)
                    
    #             df=df.loc[df['diagnosis.status'] == 'added']

    #             if first:
    #                 added=len(df)

    #             detail_df = df[['component.name','component.shortName','rulePattern.name','rulePattern.critical']]
    #             detail_df = detail_df.rename(columns={'component.name':'Component Name','component.shortName':'Component Short Name','rulePattern.name':'Rule','rulePattern.critical':'Critical'})
    #             first=False

    #             if not detail_df.empty:
    #                 format_table(writer,detail_df,name,[120,50,75,10])

    #     combined = DataFrame()
    #     prev_snapshot = aip.get_prev_snapshot(domain_id)
    #     if bool(prev_snapshot):
    #         new_grades = aip.get_grades_by_technology(domain_id,snapshot)
    #         unwanted=new_grades.columns[new_grades.columns.str.startswith('ISO')]
    #         new_grades=new_grades.drop(unwanted,axis=1).transpose()[['All']].rename(columns={'All':'Latest'})
            
    #         old_grades = aip.get_grades_by_technology(domain_id,prev_snapshot).drop(unwanted,axis=1).transpose()[['All']].rename(columns={'All':'Previous'})

    #         combined = merge(old_grades,new_grades,left_index=True,right_index=True).reset_index()
    #         combined['Change'] = combined[['Previous', 'Latest']].pct_change(axis=1)['Latest']
    #         format_table(writer,combined,'Grades',[50,10,10,10])
    #     else:
    #         new_grades = aip.get_grades_by_technology(domain_id,snapshot)
    #         unwanted=new_grades.columns[new_grades.columns.str.startswith('ISO')]
    #         new_grades=new_grades.drop(unwanted,axis=1).transpose()[['All']].rename(columns={'All':'Latest'})

    #         data = {
    #         "Previous": ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
    #         }

    #         old_grades = DataFrame(data, index =  ['TQI', 'Robustness', 'Efficiency', 'Security', 'Transferability', 'Changeability', 'Documentation'])

    #         #load data into a DataFrame object:
    #         combined = merge(old_grades,new_grades,left_index=True,right_index=True).reset_index()

    #         combined['Change'] = ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
    #         format_table(writer,combined,'Grades',[50,10,10,10])

    #     writer.close()

    #     #if application does not contains previous snapshot then prev_snapshot['date'] = 0
    #     if len(prev_snapshot) == 0:
    #         prev_snapshot['date'] = 0
    #     prev_snapshot_date = prev_snapshot['date']

    #     print(combined)

    db_uri = f"postgresql://{args.css_user}:{args.css_password}@{args.css_host}:{args.css_port}/{args.css_database}"

    # Create an SQLAlchemy engine
    engine  = create_engine(db_uri)

    # Create a connection and a cursor
    connection = engine.connect()
    cursor = connection.connection.cursor()

    app_name = args.app_name

    if '.' in args.app_name:
        app_name = args.app_name.replace('.','_')

    if '-' in args.app_name:
        app_name = app_name.replace('-','_')

    query = f"""set search_path={app_name}_central;"""
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
        log.info(f'There is no previous snapshot for the application -> {args.app_name}.')
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

    generate_application_template(combined, args.app_name, latest_snapshot_date, previous_snapshot_date, added, total, args.html_template_path, args.generated_html_path)

    log.info(f'{added} new violations added')

    name = 'status'

    # set value of the variable
    if added == 0: 
        value = 'pass'
    else:
        value = 'fail'

    # set variable
    print(f'##vso[task.setvariable variable={name};]{value}')

    print(added) 

    # send_email(args.application, args.sender, args.reciever, args.smtp_host, args.smtp_port, args.smtp_user, args.smtp_pass)
        
    exit(added)
