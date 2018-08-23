import os
import urllib.request
from cudatext import *

TEST_CFG = os.path.join(app_path(APP_DIR_SETTINGS), 'history.json')
URL_DB = 'https://raw.githubusercontent.com/Alexey-T/CudaText-registry/master/multi_inst/db.py'
COLUMN_LEN = 20

def str_to_bool(s):
    return s == '1'
def bool_to_str(v):
    return '1' if v else '0'


class Command:

    def load_repo(self):

        global cuda_addonman
        import cuda_addonman # do it here for faster Cud start

        exec("global T_LEXER,T_LINTER,T_TREE,T_INTEL,T_SNIP,T_OTHER,CLASSES,PLUGINS_CLASSES,CLASSES_MSGS,PLUGINS\n"+urllib.request.urlopen(URL_DB).read().decode("utf-8"))

        self.packets = cuda_addonman.work_remote.get_remote_addons_list(cuda_addonman.opt.ch_def+cuda_addonman.opt.ch_user)
        self.installed_list = cuda_addonman.work_local.get_installed_list()
        
    def is_installed(self,kind,name):

        if kind in PLUGINS_CLASSES:
            return name in list(map(cuda_addonman.work_local.get_name_of_module,self.installed_list))
        elif kind == T_TREE:
            return 'cuda_tree_'+name.lower() in self.installed_list
        elif kind == T_LINTER:
            return 'cuda_lint_'+name.lower() in self.installed_list
        return False
        
    def install(self,kind,name):

        print('Installing: '+kind+' '+name)
        for i in self.packets:
            if i['kind']==kind and i['name']==name:
                state='Installing: %s %s'%(kind,name)
                msg_status(state, True)                    
                #download
                fn = cuda_addonman.work_remote.get_plugin_zip(i['url'])
                if not os.path.isfile(fn):
                    msg_status(state+' - Cannot download', True)
                    return
                    
                ok = file_open(fn, options='/silent')
                msg_status(state+(' - Installed' if ok else ' - Cancelled'), True)

                #save version
                if kind in cuda_addonman.KINDS_WITH_VERSION:
                    dir_addon = app_path(APP_DIR_INSTALLED_ADDON)
                    if dir_addon:
                        filename_ver = os.path.join(dir_addon, 'v.inf')
                        with open(filename_ver, 'w') as f:
                            f.write(i['v'])
                return
        print('Not found: '+kind+' '+name)
        
    def open_menu(self):

        self.load_repo()

        langs = list(PLUGINS.keys())
        langs.sort()
        h=app_proc(PROC_GET_GUI_HEIGHT,'check')

        to_install = {}
        for i in CLASSES:
            to_install[i] = []

        RES_LIST = 1
        RES_NEXT = 3
        res = dlg_custom('Multi Installer', 300, 300, '\n'.join([
            '\1'.join(['type=label','pos=5,5,200,0','cap=Select languages:']),
            '\1'.join(['type=checklistbox','pos=5,25,295,260','items='+
                '\t'.join(langs)
                ]),
            '\1'.join(['type=button','pos=5,265,85,295','cap=Cancel']),
            '\1'.join(['type=button','pos=215,265,295,295','cap=Next']),
            ]),
            get_dict=True
            )
        if res is None:
            return
        if res['clicked']!=RES_NEXT:
            return
            
        res_list = res[RES_LIST].split(';')[1].split(',')
        res_list = map(str_to_bool,res_list) 
        for i,f in enumerate(res_list):
            if f:
                cl = 0
                line = 0
                UI = []
                UI_reg = [()]
                for curr_class in CLASSES:
                        pls = PLUGINS[langs[i]].setdefault(curr_class)
                        if pls:
                            if line in (COLUMN_LEN,COLUMN_LEN-1):
                                cl+=1
                                line = 0
                            UI.append('\1'.join([
                                            'type=label',
                                            'pos=%d,%d,%d,%d'%(5+300*cl, line*h+5, 295+300*cl, line*20+25),
                                            'cap='+CLASSES_MSGS[curr_class]
                                            ]))
                            UI_reg.append(())
                            line+=1
                            for pl in pls:
                                if line==COLUMN_LEN:
                                    cl+=1
                                    line = 0
                                flag_en = not self.is_installed(curr_class,pl)
                                UI.append('\1'.join([
                                                'type=check',
                                                'pos=%d,%d,%d,%d'%(5+300*cl, line*h, 295+300*cl, line*20+25),
                                                'cap='+pl.replace('_',' '),
                                                'en='+bool_to_str(flag_en)
                                                ]))
                                UI_reg.append((curr_class,pl))
                                line+=1
                if cl!=0:
                    line=COLUMN_LEN
                UI = ['\1'.join([
                            'type=button',
                            'pos=%d,%d,%d,%d'%(215+300*cl, line*h+5, 295+300*cl, line*20+25),
                            'cap=Next'
                            ])] + UI
                line+=1
                cl+=1
                res2 = dlg_custom(
                        'Select add-ons - '+langs[i], 
                        300*cl, 
                        line*h+15, 
                        '\n'.join(UI),
                        get_dict=True
                        )
                if res2:
                    if res2['clicked']==0:
                        for ii in range(len(UI_reg)):
                            if UI_reg[ii] and res2[ii]=='1':
                                to_install[UI_reg[ii][0]].append(UI_reg[ii][1])
        f = False
        for i in to_install.items():
            if i:
                f = True
                break
        if f:            
            for i in to_install[T_LEXER]:
                self.install(T_LEXER,i)
            if to_install[T_LINTER]:
                if not self.is_installed('plugin','CudaLint'):
                    self.install('plugin','CudaLint')
                for i in to_install[T_LINTER]:
                    self.install(T_LINTER,i)
            if to_install[T_TREE]:
                if not self.is_installed('plugin','CudaTree'):
                    self.install('plugin','CudaTree')
                for i in to_install[T_TREE]:
                    self.install(T_TREE,i)
            if to_install[T_SNIP]:
                if not self.is_installed('plugin','Snippets'):
                    self.install('plugin','Snippets')
                for i in to_install[T_SNIP]:
                    self.install(T_SNIP,i)
            for i in to_install[T_INTEL]:
                self.install('plugin',i)
            for i in to_install[T_OTHER]:
                self.install('plugin',i)
            msg_status('Multi Installer: done', True)

    def on_start(self, ed_self):

        if not os.path.exists(TEST_CFG):
            self.open_menu()
