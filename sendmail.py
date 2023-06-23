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
    mailItem.Body = "Hi, Please find attached Application Health File."
    mailItem.To = 's.p@castsoftware.com; m.sharma@castsoftware.com; n.kaplan@castsoftware.com'

    mailItem.Attachments.Add(os.path.join(os.getcwd(), 'ApplicationHealth.htm'))
    mailItem.Attachments.Add(os.path.join(os.getcwd(), 'img/logo.png'))

    mailItem.Display()

    mailItem.Save()
    mailItem.Send()
