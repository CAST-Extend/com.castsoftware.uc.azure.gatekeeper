from cast_common.aipRestCall import AipRestCall
from cast_common.logger import Logger,INFO
from cast_common.util import format_table
from pandas import ExcelWriter, Series,merge,options, DataFrame
from argparse import ArgumentParser
from os.path import abspath,exists
from datetime import datetime

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

        #if application does not contains previous snapshot then prev_snapshot['date'] = 0
        if len(prev_snapshot) == 0:
            prev_snapshot['date'] = 0
        prev_snapshot_date = prev_snapshot['date']

        table_data = ''
        if not combined.empty:

            if combined.iloc[0]['Change'] == 'N/A':
                TQI_style= "text-align: center; {td_style}"
            else:
                TQI_style = "text-align: center; color: red" if combined.iloc[0]['Change'] < 0 else "text-align: center; color:green"

            if combined.iloc[1]['Change'] == 'N/A':
                Robustness_style = "text-align: center; {td_style}"
            else:    
                Robustness_style = "text-align: center; color: red" if combined.iloc[1]['Change'] < 0 else "text-align: center; color:green"

            if combined.iloc[2]['Change'] == 'N/A':
                Efficiency_style = "text-align: center; {td_style}"
            else:
                Efficiency_style = "text-align: center; color: red" if combined.iloc[2]['Change'] < 0 else "text-align: center; color:green"

            if combined.iloc[3]['Change'] == 'N/A':
                Security_style = "text-align: center; {td_style}"
            else:
                Security_style = "text-align: center; color: red" if combined.iloc[3]['Change'] < 0 else "text-align: center; color:green"

            if combined.iloc[4]['Change'] == 'N/A':
                Transferability_style = "text-align: center; {td_style}"
            else:
                Transferability_style = "text-align: center; color: red" if combined.iloc[4]['Change'] < 0 else "text-align: center; color:green"

            if combined.iloc[5]['Change'] == 'N/A':
                Changeability_style = "text-align: center; {td_style}"
            else:    
                Changeability_style = "text-align: center; color: red" if combined.iloc[5]['Change'] < 0 else "text-align: center; color:green"

            if combined.iloc[6]['Change'] == 'N/A':
                Documentation_style = "text-align: center; {td_style}"
            else:
                Documentation_style = "text-align: center; color: red" if combined.iloc[6]['Change'] < 0 else "text-align: center; color:green"
            td_style = "padding-left: 15px; padding-right: 5px; padding-top: 3px; padding-bottom: 3px; border-bottom: 1px solid #DDDDDD;"


            if combined.iloc[0]['Previous'] == 'N/A':
                TQI_prev = combined.iloc[0]['Previous']
            else:
                TQI_prev = "%.2f" % round(combined.iloc[0]['Previous'], 2)

            if combined.iloc[1]['Previous'] == 'N/A':
                Robustness_prev = combined.iloc[1]['Previous']
            else:
                Robustness_prev = "%.2f" % round(combined.iloc[1]['Previous'], 2)

            if combined.iloc[2]['Previous'] == 'N/A':
                Efficiency_prev = combined.iloc[2]['Previous']
            else:
                Efficiency_prev = "%.2f" % round(combined.iloc[2]['Previous'], 2)

            if combined.iloc[3]['Previous'] == 'N/A':
                Security_prev = combined.iloc[3]['Previous']
            else:
                Security_prev = "%.2f" % round(combined.iloc[3]['Previous'], 2)

            if combined.iloc[4]['Previous'] == 'N/A':
                Transferability_prev = combined.iloc[4]['Previous']
            else:
                Transferability_prev = "%.2f" % round(combined.iloc[4]['Previous'], 2)
            
            if combined.iloc[5]['Previous'] == 'N/A':
                Changeability_prev = combined.iloc[5]['Previous']
            else:
                Changeability_prev = "%.2f" % round(combined.iloc[5]['Previous'], 2)

            if combined.iloc[6]['Previous'] == 'N/A':
                Documentation_prev = combined.iloc[6]['Previous']
            else:
                Documentation_prev = "%.2f" % round(combined.iloc[6]['Previous'], 2)


            if combined.iloc[0]['Change'] == 'N/A':
                TQI_change = combined.iloc[0]['Change']
            else:
                TQI_change = "%.2f" % round(combined.iloc[0]['Change'], 2)

            if combined.iloc[1]['Change'] == 'N/A':
                Robustness_change = combined.iloc[1]['Change']
            else:
                Robustness_change = "%.2f" % round(combined.iloc[1]['Change'], 2)

            if combined.iloc[2]['Change'] == 'N/A':
                Efficiency_change = combined.iloc[2]['Change']
            else:
                Efficiency_change = "%.2f" % round(combined.iloc[2]['Change'], 2)

            if combined.iloc[3]['Change'] == 'N/A':
                Security_change = combined.iloc[3]['Change']
            else:
                Security_change = "%.2f" % round(combined.iloc[3]['Change'], 2)

            if combined.iloc[4]['Change'] == 'N/A':
                Transferability_change = combined.iloc[4]['Change']
            else:
                Transferability_change = "%.2f" % round(combined.iloc[4]['Change'], 2)
            
            if combined.iloc[5]['Change'] == 'N/A':
                Changeability_change = combined.iloc[5]['Change']
            else:
                Changeability_prev = "%.2f" % round(combined.iloc[5]['Change'], 2)

            if combined.iloc[6]['Change'] == 'N/A':
                Documentation_change = combined.iloc[6]['Change']
            else:
                Documentation_change = "%.2f" % round(combined.iloc[6]['Change'], 2)

            table_data =f"""
                <tr>
                    <td style="{td_style}">TQI</td>
                    <td style="text-align: center; {td_style}">{TQI_prev}</td>
                    <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[0]['Latest'], 2)}</td>
                    <td style="{TQI_style}; {td_style}">{TQI_change}</td>
                </tr>
                <tr>
                    <td style="padding-left: 15px; {td_style}">Robustness</td>
                    <td style="text-align: center; {td_style}">{Robustness_prev}</td>
                    <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[1]['Latest'], 2)}</td>
                    <td style="{Robustness_style}; {td_style}">{Robustness_change}</td>
                </tr>
                <tr>
                    <td style="{td_style}">Efficiency</td>
                    <td style="text-align: center; {td_style}">{Efficiency_prev}</td>
                    <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[2]['Latest'], 2)}</td>
                    <td style="{Efficiency_style}; {td_style}">{Efficiency_change}</td>
                </tr>
                <tr>
                    <td style="{td_style}">Security</td>
                    <td style="text-align: center; {td_style}">{Security_prev}</td>
                    <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[3]['Latest'], 2)}</td>
                    <td style="{Security_style}; {td_style}">{Security_change}</td>
                </tr>
                <tr>
                    <td style="{td_style}">Transferability</td>
                    <td style="text-align: center; {td_style}">{Transferability_prev}</td>
                    <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[4]['Latest'], 2)}</td>
                    <td style="{Transferability_style}; {td_style}">{Transferability_change}</td>
                </tr>
                <tr>
                    <td style="{td_style}">Changeability</td>
                    <td style="text-align: center; {td_style}">{Changeability_prev}</td>
                    <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[5]['Latest'], 2)}</td>
                    <td style="{Changeability_style}; {td_style}">{Changeability_change}</td>
                </tr>
                <tr> 
                    <td style="{td_style}">Documentation</td>
                    <td style="text-align: center; {td_style}">{Documentation_prev}</td>
                    <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[6]['Latest'], 2)}</td>
                    <td style="{Documentation_style}; {td_style}">{Documentation_change}</td>
                </tr>
                """

        # it contains data of various fields
        context = {
            "application": args.application,
            "snapshot_date": snapshot['date'],
            "prev_snapshot_date": prev_snapshot_date,
            "new_critical_viol": added,
            "total_critical_viol":total,
            "table_health_score":table_data
        }

        # passing context dictionary data to html file 
        with open("ApplicationHealthTemplate.htm", "r") as file:
            html = file.read().format(**context)
            with open("ApplicationHealth.htm", "w") as file2:
                file2.write(html)

        writer.close()
        log.info(f'{added} new violations added')
            
        exit(added)
