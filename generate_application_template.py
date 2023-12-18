import os
from bs4 import BeautifulSoup

def generate_application_template(combined, application, snapshot, prev_snapshot_date, added, total, html_template_path, generated_html_path, violations_data, PrInfo):
    table_data = ''
    if not combined.empty:

        if combined.iloc[0]['Change'] == 'N/A':
            Transferability_style= "text-align: center; "
            print(combined.iloc[0])
        else:
            Transferability_style = "text-align: center; color: red" if combined.iloc[0]['Change'] < 0 else "text-align: center; color:green"
            print(combined.iloc[0])

        if combined.iloc[1]['Change'] == 'N/A':
            Changeability_style = "text-align: center; "
        else:    
            Changeability_style = "text-align: center; color: red" if combined.iloc[1]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[2]['Change'] == 'N/A':
            Robustness_style = "text-align: center; "
        else:
            Robustness_style = "text-align: center; color: red" if combined.iloc[2]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[3]['Change'] == 'N/A':
            Security_style = "text-align: center; "
        else:
            Security_style = "text-align: center; color: red" if combined.iloc[3]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[4]['Change'] == 'N/A':
            TQI_style = "text-align: center; "
        else:
            TQI_style = "text-align: center; color: red" if combined.iloc[4]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[5]['Change'] == 'N/A':
            Efficiency_style = "text-align: center; "
        else:    
            Efficiency_style = "text-align: center; color: red" if combined.iloc[5]['Change'] < 0 else "text-align: center; color:green"

        # if combined.iloc[6]['Change'] == 'N/A':
        #     Documentation_style = "text-align: center; "
        # else:
        #     Documentation_style = "text-align: center; color: red" if combined.iloc[6]['Change'] < 0 else "text-align: center; color:green"
        
        td_style = "padding-left: 15px; padding-right: 5px; padding-top: 3px; padding-bottom: 3px; border-bottom: 1px solid #DDDDDD;"


        if combined.iloc[0]['Previous'] == 'N/A':
            Transferability_prev = combined.iloc[0]['Previous']
        else:
            Transferability_prev = "%.2f" % round(combined.iloc[0]['Previous'], 2)

        if combined.iloc[1]['Previous'] == 'N/A':
            Changeability_prev = combined.iloc[1]['Previous']
        else:
            Changeability_prev = "%.2f" % round(combined.iloc[1]['Previous'], 2)

        if combined.iloc[2]['Previous'] == 'N/A':
            Robustness_prev = combined.iloc[2]['Previous']
        else:
            Robustness_prev = "%.2f" % round(combined.iloc[2]['Previous'], 2)

        if combined.iloc[3]['Previous'] == 'N/A':
            Security_prev = combined.iloc[3]['Previous']
        else:
            Security_prev = "%.2f" % round(combined.iloc[3]['Previous'], 2)

        if combined.iloc[4]['Previous'] == 'N/A':
            TQI_prev = combined.iloc[4]['Previous']
        else:
            TQI_prev = "%.2f" % round(combined.iloc[4]['Previous'], 2)
        
        if combined.iloc[5]['Previous'] == 'N/A':
            Efficiency_prev = combined.iloc[5]['Previous']
        else:
            Efficiency_prev = "%.2f" % round(combined.iloc[5]['Previous'], 2)

        # if combined.iloc[6]['Previous'] == 'N/A':
        #     Documentation_prev = combined.iloc[6]['Previous']
        # else:
        #     Documentation_prev = "%.2f" % round(combined.iloc[6]['Previous'], 2)


        if combined.iloc[0]['Change'] == 'N/A':
            Transferability_change = combined.iloc[0]['Change']
        else:
            Transferability_change = "%.2f" % round(combined.iloc[0]['Change'], 2)

        if combined.iloc[1]['Change'] == 'N/A':
            Changeability_change = combined.iloc[1]['Change']
        else:
            Changeability_change = "%.2f" % round(combined.iloc[1]['Change'], 2)

        if combined.iloc[2]['Change'] == 'N/A':
            Robustness_change = combined.iloc[2]['Change']
        else:
            Robustness_change = "%.2f" % round(combined.iloc[2]['Change'], 2)

        if combined.iloc[3]['Change'] == 'N/A':
            Security_change = combined.iloc[3]['Change']
        else:
            Security_change = "%.2f" % round(combined.iloc[3]['Change'], 2)

        if combined.iloc[4]['Change'] == 'N/A':
            TQI_change = combined.iloc[4]['Change']
        else:
            TQI_change = "%.2f" % round(combined.iloc[4]['Change'], 2)
        
        if combined.iloc[5]['Change'] == 'N/A':
            Efficiency_change = combined.iloc[5]['Change']
        else:
            Efficiency_change = "%.2f" % round(combined.iloc[5]['Change'], 2)

        # if combined.iloc[6]['Change'] == 'N/A':
        #     Documentation_change = combined.iloc[6]['Change']
        # else:
        #     Documentation_change = "%.2f" % round(combined.iloc[6]['Change'], 2)

        table_data =f"""
            <tr>
                <td style="{td_style}">Transferability</td>
                <td style="text-align: center; {td_style}">{Transferability_prev}</td>
                <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[0]['Latest'], 2)}</td>
                <td style="{Transferability_style}; {td_style}">{Transferability_change}%</td>
            </tr>
            <tr>
                <td style="{td_style}">Changeability</td>
                <td style="text-align: center; {td_style}">{Changeability_prev}</td>
                <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[1]['Latest'], 2)}</td>
                <td style="{Changeability_style}; {td_style}">{Changeability_change}%</td>
            </tr>
            <tr>
                <td style="{td_style}">Robustness</td>
                <td style="text-align: center; {td_style}">{Robustness_prev}</td>
                <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[2]['Latest'], 2)}</td>
                <td style="{Robustness_style}; {td_style}">{Robustness_change}%</td>
            </tr>
            <tr>
                <td style="{td_style}">Security</td>
                <td style="text-align: center; {td_style}">{Security_prev}</td>
                <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[3]['Latest'], 2)}</td>
                <td style="{Security_style}; {td_style}">{Security_change}%</td>
            </tr>
            <tr>
                <td style="{td_style}">TQI</td>
                <td style="text-align: center; {td_style}">{TQI_prev}</td>
                <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[4]['Latest'], 2)}</td>
                <td style="{TQI_style}; {td_style}">{TQI_change}%</td>
            </tr>
            <tr>
                <td style="{td_style}">Efficiency</td>
                <td style="text-align: center; {td_style}">{Efficiency_prev}</td>
                <td style="text-align: center; {td_style}">{"%.2f" % round(combined.iloc[5]['Latest'], 2)}</td>
                <td style="{Efficiency_style}; {td_style}">{Efficiency_change}%</td>
            </tr>
            """

    added_critical_violations = """<p> Added Critical Violations Insight </p>
			<table id="dataframe-table" style="width: 100%;border-top: 1px solid black;border-bottom: 1px solid black;">
				<tr>
					<th style="text-align: left;border-bottom: 1px solid black;">Violation(s)</th>
				</tr>
                <tbody>
                    <!-- Data will be added here -->
                </tbody>
			</table> """
    
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(added_critical_violations, 'html.parser')

    # Find the table element where you want to add the data
    table = soup.find('table', {'id': 'dataframe-table'})
    
    # Iterate through the DataFrame rows and add them to the table
    for index,row in enumerate(violations_data):
        if index + 1 < len(violations_data):
            table.tbody.append(BeautifulSoup(f"<tr><td>{row['Rule ID']} - {row['Rule Name']} <br> <b>Object: </b> {row['Object Name']} <br> <b>Filename: </b> {row['File Path']} <br> <b>Line #: </b> {row['Start Line']} <br> <hr style='border-top: 1px dashed navy' /> </td></tr>", 'html.parser'))
        else:
            table.tbody.append(BeautifulSoup(f"<tr><td>{row['Rule ID']} - {row['Rule Name']} <br> <b>Object: </b> {row['Object Name']} <br> <b>Filename: </b> {row['File Path']} <br> <b>Line #: </b> {row['Start Line']} </td></tr>", 'html.parser'))

    complete_PRs = """<p> Completed PRs </p>
			<table id="dataframe-table" style="width: 100%;border-top: 1px solid black;border-bottom: 1px solid black;">
				<tr>
					<th style="text-align: left;border-bottom: 1px solid black;">PR Details</th>
				</tr>
                <tbody>
                    <!-- Data will be added here -->
                </tbody>
			</table> """
    
    # Create a BeautifulSoup object to parse the HTML
    soup_2 = BeautifulSoup(complete_PRs, 'html.parser')

    # Find the table element where you want to add the data
    table_2 = soup_2.find('table', {'id': 'dataframe-table'})
    
    # Iterate through the DataFrame rows and add them to the table
    count = 0
    for item in PrInfo:
        if count + 1 < len(PrInfo):
            count += 1
            table_2.tbody.append(BeautifulSoup(f"<tr><td> <b>PR ID: </b> {item['PullRequestId']} <br> <b>PR Status: </b> {item['Status']} <br> <b>PR Source Branch: </b> {item['SourceBranch']} <br> <b>PR Created By: </b> {item['CreatedBy']} <br> <b>Reviewers that Approved: </b> {item['Reviewers']}<br> <b>Created Date: </b> {item['CreatedDate']['DateTime']}<br><b>Closed Date: </b> {item['ClosedDate']['DateTime']}<br><b>PR URL: </b> {item['PrURL']}<br> <hr style='border-top: 1px dashed navy' /> </td></tr>", 'html.parser'))
        else:
            table_2.tbody.append(BeautifulSoup(f"<tr><td> <b>PR ID: </b> {item['PullRequestId']} <br> <b>PR Status: </b> {item['Status']} <br> <b>PR Source Branch: </b> {item['SourceBranch']} <br> <b>PR Created By: </b> {item['CreatedBy']} <br> <b>Reviewers that Approved: </b> {item['Reviewers']}<br> <b>Created Date: </b> {item['CreatedDate']['DateTime']}<br><b>Closed Date: </b> {item['ClosedDate']['DateTime']}<br><b>PR URL: </b> {item['PrURL']} </td></tr>", 'html.parser'))

    context = {
        "application": application,
        "snapshot_date": snapshot,
        "prev_snapshot_date": prev_snapshot_date,
        "new_critical_viol": added,
        "total_critical_viol": total,
        "table_health_score": table_data
    }    

    if added > 0:
        # it contains data of various fields
        context["added_critical_violations_insight"] = str(soup)
    else:
        # it contains data of various fields
        context["added_critical_violations_insight"] = ''

    if len(PrInfo) > 0:
        context["complete_PRs"] = str(soup_2)
    else:
        context["complete_PRs"] = ''
        

    # passing context dictionary data to html file 
    with open(html_template_path+"\ApplicationHealthTemplate.htm", "r") as file:
        html = file.read().format(**context)
        with open(generated_html_path+f"\ApplicationHealth_{application}.htm", "w") as file2:
            file2.write(html)
