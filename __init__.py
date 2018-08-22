import os
import cuda_addonman
from cudatext import *

USER_JSON = os.path.join(app_path(APP_DIR_SETTINGS), 'user.json')

def str_to_bool(s):
    return s == '1'

T_LEXER='lexer'
T_LINTER='linter'
T_TREE='treehelper'
T_INTEL='intel'
T_SNIP='snippets'
T_OTHER='other'
CLASSES=(
    T_LEXER,
    T_LINTER,
    T_TREE,
    T_INTEL,
    T_SNIP,
    T_OTHER,
    )
    
PLUGINS_CLASSES={T_OTHER,T_INTEL,'plugin'}

CLASSES_MSGS={
    T_LEXER: 'Lexers:',
    T_LINTER: 'Linters:',
    T_TREE: 'Code Tree helpers:',
    T_INTEL: 'Code intelligence plugins:',
    T_SNIP: 'Snippets:',
    T_OTHER: 'Others:',
    }

PLUGINS={
    'Python':{
        T_LINTER:(
            'Python_using_pylint',
            'Python_using_pep8',
            ),
        T_INTEL:(
            'Python_Intel',
            ),
        T_SNIP:(
            'Python',
            ),
        T_OTHER:(
            'Python_Fix_Imports',
            ),
        },
    'Lua':{
        T_LINTER:( 
            'Lua_using_luac', 
            ),
        T_SNIP:( 
            'Lua',
            ),
        T_OTHER:(
            'Lua_Format',
            ),
        },
    'Pascal':{
        T_SNIP:(
            'Pascal',
            ),
        T_TREE:(
            'Pascal',
            ),
        },
    'HTML/CSS':{
        T_LINTER:(
            'CSS_using_csslint',
            'CSS_using_csstree',
            'HTML_using_htmltidy',
            ),
        T_INTEL:(
            'HTML_Tidy',
            'HTML_Completion',
            ),
        T_OTHER:(
            'HTML_Beautify',
            'HTML_Ops',
            'HTML_Tooltips',
            'CSS_AutoPrefixer',
            'CSS_CanIUse',
            'CSS_Comb',
            'CSS_Format',
            'CSS_Minifier',
            'CSS_Prefixer',
            'CSS_Table_of_Contents',
            ),
        T_SNIP:(
            'CSS_Grid',
            'CSS_Reset',
            'Atom-Sass',
            'FakeImg',
            'HTML_Handlebars',
            'Sublime-SCSS',
            ),
        T_LEXER:(
            'LESS',
            'Sass',
            'SCSS',
            'Stylus',
            'HTML_Diafan',
            'HTML_Django_DTL',
            'HTML_Embedded_JS',
            'HTML_Handlebars',
            'HTML_Laravel_Blade',
            'HTML_Liquid',
            'HTML_Mustache',
            'HTML_Smarty',
            ),
        },
    'JavaScript':{
        T_SNIP:(
            'Atom-JavaScript',
            'Atom-JavaScript-ES6',
            ),
        T_LINTER:(
            'JavaScript_using_eslint',
            'JavaScript_using_jshint',
            'JavaScript_using_jsl',
            ),
        T_LEXER:(
            'JavaScript_Babel',
            'TypeScript',
            'CoffeeScript',
            ),
        T_OTHER:(
            'JS_Format',
            'JS_Minifier',
            'JS_Multiline_Array',
            'JS_Sort_Imports',        
            ),
        T_INTEL:(
            'Tern',
            ),
        },
    'PHP':{
        T_LINTER:(
            'PHP_using_phpcs',
            'PHP_using_phpl',
            'PHP_using_phplint',
            'PHP_using_phpmd',            
            ),
        T_SNIP:(
            'PHP',
            ),
        },
    'XML':{
        T_LINTER:(
            'XML_using_xmllint-libxml2',
            ),
        T_OTHER:(
            'XML_Format',
            'XML_Tidy',        
            ),
        T_LEXER:(
            'XSLT',
            ),
        }
    }
COLUMN_LEN=20


class Command:
    
    def __init__(self):
        pass
                
    def load_repo(self):
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
        #print('  '+kind+' '+name)
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
        #print('  '+kind+' '+name+' - Not found')
        
    def open_menu(self):
        self.load_repo()
        langs = list(PLUGINS.keys())
        langs.sort()
        to_install = []
        res = dlg_custom('Multi Installer', 300, 300, '\n'.join([
            '\1'.join(['type=label','pos=5,5,200,0','cap=Select languages:']),
            '\1'.join(['type=button','pos=235,265,295,295','cap=Next']),
            '\1'.join(['type=checklistbox','pos=5,25,295,260','items='+
                '\t'.join(langs)
                ]),
            '\1'.join(['type=button','pos=5,265,65,295','cap=Skip'])
            ]))
        to_install = {}
        for i in CLASSES:
            to_install[i] = []
        h=app_proc(PROC_GET_GUI_HEIGHT,'check')
        if res!=None:
            if res[0]==1:
                for i,f in enumerate(map(str_to_bool,res[1].split('\n')[2].split(';')[1].split(','))):
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
                                    UI.append('\1'.join(['type=label','pos='+str(5+300*cl)+','+str(line*h+5)+','+str(295+300*cl)+','+str(line*20+25),'cap='+CLASSES_MSGS[curr_class]]))
                                    UI_reg.append(())
                                    line+=1
                                    for pl in pls:
                                        if line==COLUMN_LEN:
                                            cl+=1
                                            line = 0
                                        if not self.is_installed(curr_class,pl):
                                            UI.append('\1'.join(['type=check','pos='+str(5+300*cl)+','+str(line*h)+','+str(295+300*cl)+','+str(line*20+25),'cap='+pl.replace('_',' '),'en=1']))
                                        else:
                                            UI.append('\1'.join(['type=check','pos='+str(5+300*cl)+','+str(line*h)+','+str(295+300*cl)+','+str(line*20+25),'cap='+pl.replace('_',' '),'en=0']))                                            
                                        UI_reg.append((curr_class,pl))
                                        line+=1
                        if cl!=0:
                            line=COLUMN_LEN
                        UI = ['\1'.join(['type=button','pos='+str(235+300*cl)+','+str(line*h+5)+','+str(295+300*cl)+','+str(line*20+25),'cap=Next'])] + UI
                        line+=1
                        cl+=1
                        res2 = dlg_custom('Select add-ons - '+langs[i], 300*cl, line*h+15, '\n'.join(UI))
                        if res2:
                            if res2[0]==0:
                                res2=res2[1].split('\n')
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
        if not os.path.exists(USER_JSON):
            self.open_menu()
