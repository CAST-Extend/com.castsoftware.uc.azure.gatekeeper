from cast_common.aipRestCall import AipRestCall
from cast_common.logger import Logger,INFO
from cast_common.util import format_table
from pandas import ExcelWriter
from argparse import ArgumentParser
from os.path import abspath

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-r','--restURL',required=True,help='CAST REST API URL')
    parser.add_argument('-u','--user',required=True,help='CAST REST API User Name')
    parser.add_argument('-p','--password',required=True,help='CAST REST API Password')
    parser.add_argument('-a','--application',required=True,help='Application Name')
    parser.add_argument('-f','--healthFactor',required=False,default='60017',help='Health Factor Code')
    parser.add_argument('-o','--output',required=False,help='Output Folder')

    args=parser.parse_args()

    log = Logger()

#    aip = AipRestCall(args.restURL, args.user, args.password,log_level=INFO,accept_json=True)
    aip = AipRestCall(args.restURL, args.user, args.password,log_level=INFO)
    domain_id = aip.get_domain(f'{args.application}_central')
    if domain_id==None:
        log.error(f'Domain not found: {args.application}')
    else:
        total = 0
        added = 0
        snapshot_id = aip.get_latest_snapshot(domain_id)['id']
        df=aip.get_rules(domain_id,snapshot_id,args.healthFactor,critical=True,non_critical=False,start_row=1,max_rows=999999)
        if df.empty:
            log.info(f'No violations found.')
        else:
            total=len(df)
            df=df.loc[df['component.status'] == 'added']
            added=len(df)
            detail_df = df[['component.name','component.shortName','rulePattern.name','rulePattern.critical']]
            detail_df = detail_df.rename(columns={'component.name':'Component Name','component.shortName':'Component Short Name','rulePattern.name':'Rule','rulePattern.critical':'Critical'})

            base='./'
            if not args.output is None:
                base = args.output

            file_name = abspath(f'{base}/violations.xlsx')
            writer = ExcelWriter(file_name, engine='xlsxwriter')
            cloud_tab = format_table(writer,detail_df,'Violations',[120,50,75,10])
            writer.close()

            log.info(f'{added} new violations added')
        exit(added)
