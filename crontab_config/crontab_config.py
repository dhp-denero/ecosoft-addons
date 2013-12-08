import netsvc
import time
from openerp.osv import osv, fields
from tools.translate import _
import subprocess
import os

class crontab_config(osv.osv):
    _loging = os.path.realpath(os.getcwd()+'/..') + "/crontab_oe.log"
    _root = os.path.realpath(os.getcwd()+'/..')
        
    _name = "crontab.config"
    _columns = {
        'name': fields.char('Crontab Name', size=128, required=True,),
        'note': fields.text('Description'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done','Confirmed'),
            ('cancel', 'Cancelled'),
            ], 'Status', readonly=True,
             select=True),
        'minute':fields.char('Minute', required=True),
        'hour':fields.char('Hour', required=True),
        'day':fields.char('Day of Month', required=True),
        'month':fields.char('Month', required=True),
        'week':fields.char('Day of Week', required=True),
        'command':fields.char('Command', required=True),
        'working_path':fields.char('Execute Directory'),
        'active':fields.boolean('Active'),
        'last_exec':fields.datetime('Last Manually Execute',readonly=True),
    }
    
    _defaults = {
        'minute': '*',
        'hour': '*',
        'day': '*',
        'month': '*',
        'week': '*',
        'active':True,
        'state':"draft",
        'working_path':os.path.realpath(os.getcwd()+'/..'),
        }
    
    def get_command(self,cr, user, ids, context=None):
        commands = dict.fromkeys(ids, {})
        cron_recs = self.read(cr, user, ids, ['id','name','command','working_path','active','minute','hour','day','month','week','state'], context=context)
        for cron_rec in cron_recs:
            commands[cron_rec['id']].update({'command':"echo '#Start:OE-->"+ (cron_rec.get('name',False) or "")+"';" + 
                                            (cron_rec.get('command',False) or ""),
                                            'name':(cron_rec.get('name',False) or ""),
                                            'active':(cron_rec.get('active',False)) and (cron_rec.get('state',False)=='done'),
                                            'schedule':(cron_rec.get('minute',False) or "") + " " + (cron_rec.get('hour',False) or "")  + " " +
                                                        (cron_rec.get('day',False) or "")  + " " + (cron_rec.get('month',False) or "")  + " " +
                                                        (cron_rec.get('week',False) or "") ,
                                    })  
        return commands
    
    def write(self, cr, uid, ids, vals, context=None):           
        res = super(crontab_config, self).write(cr, uid, ids, vals, context=context)            
        self.generate_crontab(cr, uid, ids, context)
         
        return res
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('working_path',False) :
            if len(vals.get('working_path',""))>0:
                working_path = vals.get('working_path',"")
                working_path_len = len(working_path)
                if not working_path.endswith("/",working_path_len,working_path_len):
                    vals['working_path']=vals.get('working_path',"")+"/"
        res_id = super(crontab_config, self).create(cr, uid, vals, context=context)
        
        self.generate_crontab(cr, uid, [res_id], context)
        
        return res_id 
    
    def generate_crontab(self,cr, user, ids, context=None):        
        #Create temporary. 
        #Note,make sure you have permission to access directory and directory exists.
        tmpfn1 = os.tempnam(self._root,'oe1')
        tmpfn2 = os.tempnam(self._root,'oe2')
        tmpfn3 = ""
        
        #Extract Crontab to temporary file
        p = subprocess.call(["crontab -l > "+ tmpfn1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #Get Command from database                        
        commands = self.get_command(cr, user, ids, context)
        for id in ids:
            #Search with "#Start:OE-->" + name crontrab  and delete it.
            subprocess.call(["sed '/#Start:OE-->"+ (commands[id].get('name',False) or "") +"/d' "+  tmpfn1 +" > "+ tmpfn2], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            
            if  commands[id].get('active',False):#Active and state is done
                #Append new command into temporary file
                fo = open(tmpfn2, "a")
                fo.write( commands[id].get('schedule',"") + " " + commands[id].get('command',"")+">>"+self._loging +"\n");
                fo.close()
                
            tmpfn3 = tmpfn1    
            tmpfn1 = tmpfn2
            tmpfn2 = tmpfn3
        
        #Generate the Crontab from file.
        p = subprocess.call(["crontab "+ tmpfn1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #Delete temporary file
        p = subprocess.call(["rm "+ tmpfn1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p = subprocess.call(["rm "+ tmpfn2], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
           
        return True
    
    def action_button_confirm(self,cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context)
        return True
    
    def action_button_execute(self,cr, uid, ids, context=None):
        commands = self.get_command(cr, uid, ids, context)
         
        for id in ids:
            p = subprocess.call([commands[id].get('command',"")+">>"+self._loging], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.write(cr, uid, ids, {'last_exec':time.strftime('%Y-%m-%d %H:%M:%S')}, context)
#         
#         p = subprocess.call(["echo '#Start:OE# Scheduling' $( date +\%d-\%m-\%Y_\%H:\%M ) >> /tmp/dbbackup.log"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#         p = subprocess.call(["sed '/#Start:OE#/d' /tmp/dbbackup.log > /tmp/dbbackup1.log"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
# #         output, err = p.communicate()
        return True
    
    
    
    def db_backup(self,cr, uid, ids=None, context=None):
        return self._root
crontab_config()