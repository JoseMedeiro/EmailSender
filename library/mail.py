import  smtplib, ssl
import  datetime
from    pathlib import Path
from    email.mime.text         import MIMEText
from    email.mime.multipart    import MIMEMultipart
import  imaplib
import  time
from    library.basic_utils     import force_list
KNOWN_SERVERS = ['aerotec.tecnico.ulisboa.pt'
                 'tecnico.ulisboa.pt',
                 'gmail.com',
                 'outlook.com']
SHAPE            = {
    'metadata': ['To','From','Subject','Date','Cc','Bcc','Reply-To'],
    'body':     None,
    'fields':   None
}
### CLASSES ###
class server_session:
    def __init__(self,data) -> None:
        self.user           = data['user']
        self.password       = data['password']
        self.server         = data['server']
        # SMTP
        self.smtp_port      = data['smtp_port']
        # IMAP
        self.imap_port      = data['imap_port']
        # Sessions
        self.smtp = None
        self.imap = None

        return None
    # SMTP
    def smtp_login(self):
        context     = ssl.create_default_context()
        self.smtp   = smtplib.SMTP_SSL(self.server, self.smtp_port, context=context)
        self.smtp.login(self.user, self.password)

        return None
    def smtp_logout(self):
        self.smtp.quit()
        self.smtp = None

        return None
    # IMAP
    def imap_login(self):
        self.imap   = imaplib.IMAP4_SSL(self.server,self.imap_port)
        self.imap.login(self.user, self.password)

        return None
    def imap_logout(self):
        self.imap.logout()
        self.imap = None

        return None
class mail:
    def __init__(self, data, custom_reciever:dict = None, in_cc:bool = True) -> None:
        
        self.emiter     = data["metadata"]["From"]
        self.message    = create_mail(data)
        self.recievers  = define_recievers_email(data,custom_reciever,in_cc)

        return None

    def send(self,smtp_session:smtplib.SMTP_SSL,imap_session:imaplib.IMAP4_SSL)->bool:
        ## SMTP Session and recievers verification
        if smtp_session == None:
            return False
        if self.recievers == None:
            return False
        # Actual sending of the email
        result = smtp_session.sendmail(self.emiter, self.recievers, self.message.as_string())
        print(f"Sent email to {', '.join(self.recievers)}",end="")
        ## Saving the email in the server (IMAP)
        if imap_session == None:
            return len(result.keys()) == 0
        imap_session.append('Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), self.message.as_string().encode('utf8'))

        return len(result.keys()) == 0
### FUNCTIONS ###
def fill_data(d_init:dict,d_in:dict,initial=False):
    if d_in == None:
        return d_init
    if d_init == None:
        return d_in
    for k, v in zip(list(d_in.keys()),list(d_in.values())):
        r = True
        if k == 'body':
            r = False
        for s in list(SHAPE.keys()):
            if isinstance(SHAPE[s],list) and k in SHAPE[s]:
                d_init[s][k] = v
                r            = False
        if r and (k in d_init['fields'] or initial):
            d_init['fields'][k] = v
    return d_init
def merge_template_data(data:dict,template:dict):
    if template == None:
        return None
    # Initialization
    merger = dict()
    for section in SHAPE:
        merger[section] = dict()
    # Fillers
    merger          = fill_data(merger,template,initial=True)
    merger['body']  = template['body']
    merger          = fill_data(merger,data)
    return merger
def validate_address(str:str, verbose:bool=False):
    # Basic check for str
    if not isinstance(str,str):
        if verbose:
            print(f"Email {str} is not a string!")
        return False   
    # Basic check for ASCII
    if not str.isascii():
        if verbose:
            print(f"Email {str} has non ASCII characters!")
        return False
    # Check if there is one and only one 'at'
    if len(str.split('@')) != 2:
        if verbose:
            print(f"Email {str} is not valid, check for 'at' missed.")
        return False
    # Check if there is a basic server
    if len(server.split('.')) < 2:
        if verbose:
            print(f"Email {str} is not valid, check for basic server missed.")
        return False
    server = str.split('@')[1]
    # Check authorized servers
    if not server in KNOWN_SERVERS:
        if verbose:
            print(f"Email {str} is not valid, check for authorized servers missed.")
        return False
    return True

def create_mail(data):
    message = MIMEMultipart("alternative")
    # Metadata
    for key in data['metadata']:
        if data['metadata'][key] != None:
            message[key] = data['metadata'][key]
    ### Body
    # Loading Template
    with open(data['body']+'-HTML.html', 'r', encoding='utf-8') as f:
        corpo_html = f.read()
    # Replacing Fields
    if 'fields' in data:
        # Loading Signature
        if 'signature' in data['fields']:
            with open(data['fields']['signature']+'-HTML.html', 'r', encoding='utf-8') as f:
                data['fields']['signature'] = f.read()
        # Replacing Gender
        if 'gender' in data['fields']:
            if   data['fields']['gender'] == 'M':
                corpo_html = corpo_html.replace("{gender}",'o')
            elif data['fields']['gender'] == 'F':
                corpo_html = corpo_html.replace("{gender}",'a')
            else:
                corpo_html = corpo_html.replace("{gender}",'e')
        # Replacing custom strings
        for r_key, r_str in zip(list(data['fields'].keys()),list(data['fields'].values())):
            corpo_html = corpo_html.replace("{"+r_key+"}",r_str)
        
    part2 = MIMEText(corpo_html, "html")
    message.attach(part2)

    return message

def define_recievers_email(metadata,custom_reciever:dict|list|None = None,in_cc:bool = True,reciever_check:bool=True,**kargs):
    '''
    
    '''
    reciever_pre    = None
    reciever_check  = None
    # Define recievers and if there is validation
    if custom_reciever!=None:
        reciever_pre = {'a':    force_list(custom_reciever['To'].split(", ")),
                        'b':    []}
        if custom_reciever['Cc'] != None:
            reciever_pre['b'].extend(force_list(custom_reciever['Cc'].split(", ")))
        if custom_reciever['Cc'] != None:
            reciever_pre['b'].extend(force_list(custom_reciever['Bcc'].split(", ")))
    else:
        reciever_pre = {'a':    force_list(metadata['To'].split(", ")),
                        'b':    []}
        if metadata['Cc'] != None:
            reciever_pre['b'].extend(force_list(metadata['Cc'].split(", ")))
        if metadata['Cc'] != None:
            reciever_pre['b'].extend(force_list(metadata['Bcc'].split(", ")))
    reciever = reciever_pre['a']
    if in_cc and custom_reciever==None:
        reciever.extend(reciever_pre['b'])
    # Performs validation of the addresses
    if reciever_check:
        for email in reciever:
            if not validate_address(email):
                return None
            
    return reciever
