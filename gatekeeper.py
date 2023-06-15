from cast_common.aipRestCall import AipRestCall
from cast_common.logger import Logger,INFO
from cast_common.util import format_table
from pandas import ExcelWriter,merge,options, DataFrame
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

            
        internal_css="""<style>
                            .healthTable { width: 50%; border-top: 1px solid black; border-bottom: 1px solid black; }
                            th { text-align: left; padding-left: 15px; border-bottom: 1px solid black; }
                            td { padding-left: 15px; padding-right: 5px; padding-top: 3px; padding-bottom: 3px; border-bottom: 1px solid #DDDDDD;}
                            .number { text-align: center; }
                            .negNumber { text-align: center; color: red }
                            .posNumber { text-align: center; color:green }
                        </style>"""

        #if application does not contains previous snapshot then prev_snapshot['date'] = 0
        if  len(prev_snapshot) == 0:
            prev_snapshot['date'] = 0
        prev_snapshot_date = prev_snapshot['date']

        table_data = ''
        if not combined.empty:

            TQI_no_type = "negNumber" if combined.iloc[0]['Change'] < 0 else "posNumber"
            Robustness_no_type = "negNumber" if combined.iloc[1]['Change'] < 0 else "posNumber"
            Efficiency_no_type = "negNumber" if combined.iloc[2]['Change'] < 0 else "posNumber"
            Security_no_type = "negNumber" if combined.iloc[3]['Change'] < 0 else "posNumber"
            Transferability_no_type = "negNumber" if combined.iloc[4]['Change'] < 0 else "posNumber"
            Changeability_no_type = "negNumber" if combined.iloc[5]['Change'] < 0 else "posNumber"
            Documentation_no_type = "negNumber" if combined.iloc[6]['Change'] < 0 else "posNumber"

            table_data =f"""
                <tr>
                    <td>TQI</td>
                    <td class="number">{"%.2f" % round(combined.iloc[0]['Previous'], 2)}</td>
                    <td class="number">{"%.2f" % round(combined.iloc[0]['Latest'], 2)}</td>
                    <td class="{TQI_no_type}">{"%.2f" % round(combined.iloc[0]['Change'], 2)}</td>
                </tr>
                <tr>
                    <td>Robustness</td>
                    <td class="number">{"%.2f" % round(combined.iloc[1]['Previous'], 2)}</td>
                    <td class="number">{"%.2f" % round(combined.iloc[1]['Latest'], 2)}</td>
                    <td class="{Robustness_no_type}">{"%.2f" % round(combined.iloc[1]['Change'], 2)}</td>
                </tr>
                <tr>
                    <td>Efficiency</td>
                    <td class="number">{"%.2f" % round(combined.iloc[2]['Previous'], 2)}</td>
                    <td class="number">{"%.2f" % round(combined.iloc[2]['Latest'], 2)}</td>
                    <td class="{Efficiency_no_type}">{"%.2f" % round(combined.iloc[2]['Change'], 2)}</td>
                </tr>
                <tr>
                    <td>Security</td>
                    <td class="number">{"%.2f" % round(combined.iloc[3]['Previous'], 2)}</td>
                    <td class="number">{"%.2f" % round(combined.iloc[3]['Latest'], 2)}</td>
                    <td class="{Security_no_type}">{"%.2f" % round(combined.iloc[3]['Change'], 2)}</td>
                </tr>
                <tr>
                    <td>Transferability</td>
                    <td class="number">{"%.2f" % round(combined.iloc[4]['Previous'], 2)}</td>
                    <td class="number">{"%.2f" % round(combined.iloc[4]['Latest'], 2)}</td>
                    <td class="{Transferability_no_type}">{"%.2f" % round(combined.iloc[4]['Change'], 2)}</td>
                </tr>
                <tr>
                    <td>Changeability</td>
                    <td class="number">{"%.2f" % round(combined.iloc[5]['Previous'], 2)}</td>
                    <td class="number">{"%.2f" % round(combined.iloc[5]['Latest'], 2)}</td>
                    <td class="{Changeability_no_type}">{"%.2f" % round(combined.iloc[5]['Change'], 2)}</td>
                </tr>
                <tr>
                    <td>Documentation</td>
                    <td class="number">{"%.2f" % round(combined.iloc[6]['Previous'], 2)}</td>
                    <td class="number">{"%.2f" % round(combined.iloc[6]['Latest'], 2)}</td>
                    <td class="{Documentation_no_type}">{"%.2f" % round(combined.iloc[6]['Change'], 2)}</td>
                </tr>
                """

        # it contains data of various fields
        context = {
            "internal_css": internal_css,
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
