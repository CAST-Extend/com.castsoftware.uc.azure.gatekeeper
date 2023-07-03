import os

def generate_application_template(combined, application, snapshot, prev_snapshot_date, added, total):
    table_data = ''
    if not combined.empty:

        if combined.iloc[0]['Change'] == 'N/A':
            TQI_style= "text-align: center; "
        else:
            TQI_style = "text-align: center; color: red" if combined.iloc[0]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[1]['Change'] == 'N/A':
            Robustness_style = "text-align: center; "
        else:    
            Robustness_style = "text-align: center; color: red" if combined.iloc[1]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[2]['Change'] == 'N/A':
            Efficiency_style = "text-align: center; "
        else:
            Efficiency_style = "text-align: center; color: red" if combined.iloc[2]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[3]['Change'] == 'N/A':
            Security_style = "text-align: center; "
        else:
            Security_style = "text-align: center; color: red" if combined.iloc[3]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[4]['Change'] == 'N/A':
            Transferability_style = "text-align: center; "
        else:
            Transferability_style = "text-align: center; color: red" if combined.iloc[4]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[5]['Change'] == 'N/A':
            Changeability_style = "text-align: center; "
        else:    
            Changeability_style = "text-align: center; color: red" if combined.iloc[5]['Change'] < 0 else "text-align: center; color:green"

        if combined.iloc[6]['Change'] == 'N/A':
            Documentation_style = "text-align: center; "
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
            Changeability_change = "%.2f" % round(combined.iloc[5]['Change'], 2)

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
                <td style="{td_style}">Robustness</td>
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
        "application": application,
        "snapshot_date": snapshot['date'],
        "prev_snapshot_date": prev_snapshot_date,
        "new_critical_viol": added,
        "total_critical_viol":total,
        "table_health_score":table_data
    }

    # passing context dictionary data to html file 
    with open(os.getcwd()+"\ApplicationHealthTemplate.htm", "r") as file:
        html = file.read().format(**context)
        with open(os.getcwd()+"\ApplicationHealth.htm", "w") as file2:
            file2.write(html)
