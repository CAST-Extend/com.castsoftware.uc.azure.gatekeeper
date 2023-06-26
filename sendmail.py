import os
import win32com.client as win32

def send_email():

    # construct Outlook application instance
    olApp = win32.Dispatch('Outlook.Application')
    olNS = olApp.GetNameSpace('MAPI')

    # construct the email item object
    mailItem = olApp.CreateItem(0)
    mailItem.Subject = 'Application Health File'
    mailItem.BodyFormat = 1
    mailItem.To = 's.p@castsoftware.com; m.sharma@castsoftware.com; n.kaplan@castsoftware.com'

    attachment = mailItem.Attachments.Add(os.path.join(os.getcwd(), 'img/logo.png'))
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyId1")

    with open('ApplicationHealth.htm', 'r') as myfile:
        data=myfile.read()

    mailItem.HTMLBody = "<html> <body lang=EN-US style='word-wrap:break-word'> <div class=WordSection1> <table border=0 cellspacing=0 cellpadding=0 width='100%'> <tr> <td width='25%' valign=top> " + "<img src=""cid:MyId1"">" + data 

    mailItem.Display()

    mailItem.Save()
    mailItem.Send()

