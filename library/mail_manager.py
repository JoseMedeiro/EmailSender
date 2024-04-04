from   library.mail import mail, server_session
import datetime
import time
LIMIT_PER_MINUTE = 50
def create_and_send_emails(l:list,session:dict,
                           custom_reciever=None,
                           in_cc=True, N:int=None):
    session = server_session(session)
    session.smtp_login()
    session.imap_login()

    t_0 = datetime.datetime.now()
    n   = 0
    if N == None:
        N = len(l)+1
    sent_list = list()
    for e in l[:N]:
        # Construct email
        mail_2_send = mail(e,custom_reciever=custom_reciever,in_cc=in_cc)
        ## Controller
        n += len(mail_2_send.recievers)
        if n >= LIMIT_PER_MINUTE:
            print("Limit per minute reached. Awaiting next time slot")
            # Logging out to not raise AFK flags
            session.smtp_logout()
            session.imap_logout()
            # Waiting for time slot
            t_0 = datetime.datetime.now()
            while datetime.datetime.now() - datetime.timedelta(minutes=1) < t_0:
                time.sleep(10)
            n   = 0
            # Logging in again
            session.smtp_login()
            session.imap_login()
        # Sender
        r = False
        try:
            r = mail_2_send.send(session.smtp,session.imap)
        except:
            print('Some error occured during the sending stage. Saving sent emails')
            return sent_list
        if r:
            sent_list.append(e)
    # Final Logout
    session.smtp_logout()
    session.imap_logout()

    return sent_list