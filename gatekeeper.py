from cast_common.aipRestCall import AipRestCall
from cast_common.logger import Logger,INFO
from pandas import json_normalize
from argparse import ArgumentParser

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-r','--restURL',required=True,help='CAST REST API URL')
    parser.add_argument('-u','--user',required=True,help='CAST REST API User Name')
    parser.add_argument('-p','--password',required=True,help='CAST REST API Password')
    parser.add_argument('-a','--application',required=True,help='Application Name')

    args=parser.parse_args()

    log = Logger()

    aip = AipRestCall(args.restURL, args.user, args.password,log_level=INFO,accept_json=True)
    domain_id = aip.get_domain(args.application)
    if domain_id==None:
        log.error(f'Domain not found: {args.application}')
    else:
        snapshot_id = aip.get_latest_snapshot(domain_id)['id']
        df=aip.get_rules(domain_id,snapshot_id,60017,critical=True,non_critical=False,start_row=1,max_rows=999999)
        if df.empty:
            log.info(f'No violations found.')
        else:
            df=json_normalize(df['component'])
            added=len(df[df['status'] == 'added'])
            log.info(f'This snapshot added {added} new violations.')
        exit(0)
