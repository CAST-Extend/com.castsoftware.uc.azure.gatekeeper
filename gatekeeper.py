from cast_common.aipRestCall import AipRestCall
from cast_common.logger import Logger,INFO
from cast_common.util import format_table
from pandas import ExcelWriter, Series,merge,options, DataFrame
from argparse import ArgumentParser
from os.path import abspath,exists
from datetime import datetime
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
    parser.add_argument('-r','--restURL',required=True,help='CAST REST API URL')
    parser.add_argument('-u','--user',required=True,help='CAST REST API User Name')
    parser.add_argument('-p','--password',required=True,help='CAST REST API Password')
    parser.add_argument('-a','--application',required=True,help='Application Name')
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

    aip = AipRestCall(args.restURL, args.user, args.password,log_level=INFO)
    domain_id = aip.get_domain(f'{args.application}_central')
    if domain_id==None:
        log.error(f'Domain not found: {args.application}')
    else:
        total = 0
        added = 0
        snapshot = aip.get_latest_snapshot(domain_id)
        if not bool(snapshot):
            log.error(f'No snapshots found: {args.application}')
            exit (-1)
        snapshot_id = snapshot['id']

        base='./'
        if not args.output is None:
            base = args.output

        s = datetime.now().strftime("%Y%m%d-%H%M%S")
        file_name = abspath(f'{base}/violations-{args.application}-{s}.xlsx')
        writer = ExcelWriter(file_name, engine='xlsxwriter')

        first=True
        for code in measures:
            name = measures[code]
            df=aip.get_rules(domain_id,snapshot_id,code,critical=True,non_critical=False,start_row=1,max_rows=999999)
            if not df.empty:
                if first:
                    total=len(df)
                    
                df=df.loc[df['diagnosis.status'] == 'added']

                if first:
                    added=len(df)

                detail_df = df[['component.name','component.shortName','rulePattern.name','rulePattern.critical']]
                detail_df = detail_df.rename(columns={'component.name':'Component Name','component.shortName':'Component Short Name','rulePattern.name':'Rule','rulePattern.critical':'Critical'})
                first=False

                if not detail_df.empty:
                    format_table(writer,detail_df,name,[120,50,75,10])

        combined = DataFrame()
        prev_snapshot = aip.get_prev_snapshot(domain_id)
        if bool(prev_snapshot):
            new_grades = aip.get_grades_by_technology(domain_id,snapshot)
            unwanted=new_grades.columns[new_grades.columns.str.startswith('ISO')]
            new_grades=new_grades.drop(unwanted,axis=1).transpose()[['All']].rename(columns={'All':'Latest'})
            
            old_grades = aip.get_grades_by_technology(domain_id,prev_snapshot).drop(unwanted,axis=1).transpose()[['All']].rename(columns={'All':'Previous'})

            combined = merge(old_grades,new_grades,left_index=True,right_index=True).reset_index()
            combined['Change'] = combined[['Previous', 'Latest']].pct_change(axis=1)['Latest']
            format_table(writer,combined,'Grades',[50,10,10,10])
        else:
            new_grades = aip.get_grades_by_technology(domain_id,snapshot)
            unwanted=new_grades.columns[new_grades.columns.str.startswith('ISO')]
            new_grades=new_grades.drop(unwanted,axis=1).transpose()[['All']].rename(columns={'All':'Latest'})

            data = {
            "Previous": ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
            }

            old_grades = DataFrame(data, index =  ['TQI', 'Robustness', 'Efficiency', 'Security', 'Transferability', 'Changeability', 'Documentation'])

            #load data into a DataFrame object:
            combined = merge(old_grades,new_grades,left_index=True,right_index=True).reset_index()

            combined['Change'] = ['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']
            format_table(writer,combined,'Grades',[50,10,10,10])

        writer.close()

        #if application does not contains previous snapshot then prev_snapshot['date'] = 0
        if len(prev_snapshot) == 0:
            prev_snapshot['date'] = 0
        prev_snapshot_date = prev_snapshot['date']

        generate_application_template(combined, args.application, snapshot, prev_snapshot_date, added, total)

        log.info(f'{added} new violations added')

        # send_email(args.application, args.sender, args.reciever, args.smtp_host, args.smtp_port, args.smtp_user, args.smtp_pass)
            
        exit(added)
