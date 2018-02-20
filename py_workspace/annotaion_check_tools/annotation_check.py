

from cmd import Cmd
import sys
import os
import test_cmd_color


class CmdTest(Cmd):
    intro = '''
@brief：本exe主要功能为检测c文件和h头文件的注释率，输出不满足30%注释率的文件
@author: brain.liu-刘波
@version:V1.0.1_20180131
@email: brain.liu@spreadtrum.com

@note：
1）本exe只检查满足doxygen 注释规范的注释，不满足规范的注释将被认为是无效注释，不计算在注释率内
2）doxygen注释规范请参考《编码风格精简版与全局头文件V0.3》,输入命令:"help doxygen" 了解详细风格
3）注释率 = 注释行数/(总行数 - 空行数),为提高注释率，请删除无效代码，增加注释
4）默认的注释率门限为30%，低于门限的文件将被输出到“annotation_fail_files.log”
5）若遇到错误和问题，欢迎反馈到brain.liu@spreadtrum.com

            '''
    prompt = "command:"
    def __init__(self):  # 初始基础类方法
        Cmd.__init__(self)
        self.start = 0
        self.rate = 30 #注释率门限，以百分比为单位
        
    
    def precmd(self,line):
        current_dir = os.getcwd()  # 获取check_tool的目录
        result_dir = os.path.join(current_dir, "check_result/")
        config_dir = os.path.join(current_dir, "check_config/")
        # 方式exit命令重新打开文件，刷空文件,在输入如下3种命令和空行命令时，可以处理文件
        if (line.strip() in ["check all", "check c", "check h",""]):
            self.log_f = open(result_dir +"annotation_check_logs.log", "w")
            self.w_f = open(result_dir + "annotation_check_results.log", "w")
            self.fail_f = open(result_dir +"annotation_fail_files.log", "w")
            self.ignore_f =  open(config_dir + "ignore_file_list.log", "r")
            print(" "*15 +"annotation rate threshold:%.2f%%,belowing files are the unqualified files" \
                    %self.rate,file=self.fail_f)
            print("---------------------------------------------unqualified files list-------------------------------------------------- ",file = self.fail_f)
            print("注：若文件头部注释区域无author定义，owner 显示为文件名\n", file=self.fail_f)
            # 格式化输出结果
            print(" " * 12 + "Owner" + " " * 24 +"FileName" + " " * 21 + "TotalLines" + \
                  " " * 10 + "BlankLines" + " " * 9 + "CommentLines" + " " * 9 +"CommentRate", \
                 file=self.fail_f)
        if (line.strip() == ""):
            print("the command is empty, will execute the last nonempty command")
        return Cmd.precmd(self, line)
    
    def postcmd(self,stop,line):
        #在输入如下3种命令和空行命令时，可以处理文件
        if(line.strip() in ["check all","check c","check h",""]):
            self.log_f.close()
            self.w_f.close()
            self.fail_f.close()
            self.ignore_f.close()
        return Cmd.postcmd(self, stop, line)
    
    def help_doxygen(self):
        print('''
    如下风格为本工具可检查的注释风格(不符合风格的注释将视为无效注释)：
                
    文件头注释示范:    /** @file..注释....*/

    函数头注释示范：   /*!......注释......*/
                         
    单行注释  示范:   /*!<.....注释......*/
                   //!<.....注释......
                                         
    多行注释  示范:   /*!......注释......*/\n''')
        
    def help_check(self):
        print('''check ---------检测文件，有三种命令:
                            check all: 检查.c文件和.h文件
                            check c:   只检查.c文件
                            check h:   只检查.h文件\n''')
    def help_version(self):
        print('''@version: 20180220
@cr_0220: add different color setting for character
@bugfix_0203: gbk codec can't decode error
@bugfix_0218: exit command flush the log file because of the precomd command
@bugfi_0218: input empty command ,execute the last nonempty command
@cr_0205: print check result on cmd window
@cr_0218: add ignore_file_list process

''')
        
    def do_check(self, line):
        "do check file"
        if line.lower() == "all":
            self.start = 1
        elif line.lower() == "c":
            self.start = 2
        elif line.lower() == "h":
            self.start = 3
        else:
            self.start = 0
            print("请输入正确指令，或者exit退出\n")

            
        try:
            process_check_file(self.start)
        except Exception as err:
            print("error:",str(err),file = self.log_f)
            print("error:",str(err),file = self.fail_f)
            self.log_f.close()
            self.fail_f.close()
            
            
   
    #def help_changerate(self):
     #   print('''changerate-------修改注释率门限，目前默认为30，表示30%''')
     
    '''
  #  def do_changerate(self,line):
    #    try:
            self.rate = float(line)
            print(self.rate)
        except Exception as e:
            print(e)
            pass
    '''
   
    def help_exit(self):  # 以help_*开头的为帮助
        print("exit--------输入exit退出程序\n")
    
    def do_exit(self, line):  # 以do_*开头为命令
        print("Exit:", line)
        sys.exit()
        


#注释检测类定义
class Annotation():
        total_file_num = 0 #class property
        pass_file_num = 0
        fail_file_num = 0
        ignore_file_num = 0
        ignore_file_list = []
        def __init__(self,file_owner,\
                     file_name,\
                     abspath_file_name,\
                     total_line,blank_line,\
                     single_comment,\
                     multi_comment,\
                     comment_rate,\
                     *logs):
            self.file_name_abspath = abspath_file_name # 带绝对路径的文件名
            self.file_name = file_name #文件名
            self.file_owner = file_owner # add file owner
            self.total_line_num = total_line
            self.blank_line_num = blank_line
            self.single_line_comment = single_comment
            self.multi_line_comment = multi_comment
            self.total_commment = single_comment + multi_comment
            self.annotation_rate = comment_rate
            self.logs = logs

        

    
    
# step1:遍历文件夹和子文件夹，找到所有文件，并形成list
dir_f = open("check_file_dir.log","w")
file_list = []
current_dir = os.getcwd() #获取check_tool的目录
    # #获取上级目录
rootdir = os.path.abspath(os.path.join(current_dir, ".."))
for parent, dirnames, filenames in os.walk(rootdir):
    print(parent,file = dir_f)
    print(dirnames,file = dir_f)
    print(filenames,file = dir_f)
    # case 1:
    for dirname in dirnames:
        print("parent folder is:" + parent,file = dir_f)
        print("dirname is:" + dirname,file = dir_f)
        # case 2
    for filename in filenames:
        print("filename with full path:" + os.path.join(parent, filename),file = dir_f)
        file_list.append(os.path.join(parent, filename))
dir_f.close()

def ignore_file_find(in_file):
    '''find the ignore_files in ignore_file_list.log'''
    ignore_list = []
    with open(in_file, "r", encoding="utf-8", errors="ignore") as ig_f:
        for ignore_line in ig_f.readlines():
            ignore_strip = ignore_line.strip()
            if(ignore_strip.__len__()!= 0):
                ignore_list.append(ignore_strip)
    return ignore_list



# setp2:找到.c 或者.h文件，形成新的list
c_file_list = []
h_file_list = []
ignore_file_list = []

for in_file in file_list:
    if in_file.endswith(".c"):
        c_file_list.append(in_file)
    if in_file.endswith(".h"):
        h_file_list.append(in_file)
	#python中，if判断句中，不为0的任何数都为真，-1也表示真，所以一定要明确指定判断条件
    if (in_file.find("ignore_file_list") != -1):
        ignore_file_list = ignore_file_find(in_file)






# step3: core function ,找到总行数和空行，以及注释行，给出注释率
# 处理文件时，要查找该文件的owner, owner 使用@author 进行赋值:
def file_annotation_cal(file,cmd):
    total_line_num = 0
    space_line_num = 0
    single_line_num = 0
    multi_line_num = 0
    multi_line_start = -1
    multi_line_end = -1
    blank_line_num = 0
    blank_line_record_list = []
    single_line_record_list = []
    multi_line_record_dict = {}
    log_f = cmd.log_f
    fail_f = cmd.fail_f
    file_owner = file.split("\\")[-1] #[-1]表示的是文件名
    file_name_only = file.split("\\")[-1] #[-1]表示的是文件名
    try:
        with open(file, "r",encoding = "utf-8",errors = "ignore") as file_p:
            for line in file_p.readlines():
                line_strip = line.strip()
                total_line_num += 1
                if(len(line_strip) == 0):
                    blank_line_num += 1
                    blank_line_record_list.append(total_line_num)
                if((line_strip.find("//!<") != -1) and (multi_line_start == -1) and (line_strip.find("/*!") == -1)):
                    single_line_num += 1
                    single_line_record_list.append(total_line_num)
                if ((line_strip.find("/*!") != -1)
                    or (line_strip.find("/** @file") != -1)):
                    multi_line_start = total_line_num
                    if (line_strip.endswith("*/")):
                        multi_line_end = total_line_num
                        multi_line_num += 1
                        multi_line_record_dict[multi_line_start] = multi_line_end
                        multi_line_start = -1  #bug fix
                    else:
                        pass
                if ((line_strip.find("*/") != -1) and (multi_line_start > 0)):
                    multi_line_end = total_line_num
                    multi_line_num += multi_line_end - multi_line_start + 1
                    multi_line_record_dict[multi_line_start] = multi_line_end
                    multi_line_start = -1
                # 只在第一个多行注释中查找author，其他地方的author 认为无效
                if ((line_strip.find("@author") != -1) and (len(multi_line_record_dict) == 0)):
                    # 替换这一行中的空格和:, 防止不同写法
                    line_find_owner = line_strip.replace(" ","")
                    line_strip = line_find_owner.replace(":","")
                    file_owner = line_strip.split("@author")[-1]
                
    except Exception as err:
        print(file,str(err),file = log_f)
        pass


    try:    
        valid_line = total_line_num - blank_line_num
        anno_line = multi_line_num + single_line_num
        if(valid_line != 0): #防止空文件
            rate = round(100 * (anno_line / valid_line),3) #保留小数位设置
        else:
            rate = 0
    except Exception as err:
        print(file,str(err),file = log_f)
        print(file,str(err),file = fail_f)
    finally:
        
        return(Annotation(file_owner,file_name_only,file,total_line_num,blank_line_num,single_line_num,multi_line_num,(rate),single_line_record_list,multi_line_record_dict,blank_line_record_list))
        
        
        
def check_file(file_list,ignore_file_list,cmd):
    w_f = cmd.w_f
    log_f = cmd.log_f
    fail_f = cmd.fail_f
    path_list = []
    for file in file_list: #file 是绝对路径
        Annotation.total_file_num += 1
        path_list = file.split("\\") #path_list[-1]表示的是文件名
        if path_list[-1] not in ignore_file_list:
            anno_var = file_annotation_cal(file,cmd)
            
        
            print(anno_var.file_name_abspath, "annotation_rate：%.2f%%" % anno_var.annotation_rate, file=w_f)
            print("total_line_num:%d" % anno_var.total_line_num, file=w_f)
            print("blank_line_num:%d" % anno_var.blank_line_num, file=w_f)
            print("single_line_comment_num:%d" % anno_var.single_line_comment, file=w_f)
            print("multi_line_comment_num:%d" % anno_var.multi_line_comment, file=w_f)
        
            # output log
            print(anno_var.file_name_abspath, file=log_f)
            print(anno_var.logs, file=log_f)
        
            # output fail file 
            if (anno_var.annotation_rate < cmd.rate):
                Annotation.fail_file_num += 1 #失败文件计数
                #这里的15/20 要跟上述的"owner,filename,totallines"的间隔匹配
                space_num0 = int(15 - len(anno_var.file_owner)//2)
                space_num1 = int(30 - (len(anno_var.file_owner) + len(anno_var.file_name))//2)
                space_num2 = int(30 - (len(anno_var.file_name) + len(anno_var.total_line_num.__str__()))//2)
                space_num3 = int(20 - (len(str(anno_var.total_line_num)) + len(str(anno_var.blank_line_num)))//2)
                space_num4 = int(20 -  (len(anno_var.blank_line_num.__str__()) + \
                                len((anno_var.total_commment).__str__()))//2)
                #annotation_rate's length fixed to 4 for simplify
                space_num5 = int(20 - (len((anno_var.total_commment).__str__()) \
                                       + len(str(anno_var.annotation_rate)))//2)
                                 
                print(" "*space_num0 + anno_var.file_owner+" " * space_num1 + anno_var.file_name+\
                      " "* space_num2+ str(anno_var.total_line_num) +" "* space_num3 + \
                      str(anno_var.blank_line_num)+" "*space_num4+
                      str(anno_var.total_commment)+" "* space_num5 + str(anno_var.annotation_rate)+"%",\
                      file = fail_f)
        else: #ignore file
            Annotation.ignore_file_num += 1
            Annotation.ignore_file_list.append(file)
    

# step4: 遍历所有.c和.h文件，输出不合格的文件路径到指定文件中。
def process_check_file(flag = 1):
    w_f = cmd.w_f
    log_f = cmd.log_f
    fail_f = cmd.fail_f
    Annotation.total_file_num = 0
    Annotation.fail_file_num = 0
    Annotation.ignore_file_num = 0
    Annotation.ignore_file_list = [] #每次执行都要清空
    if(flag == 1):
            print("-------------------------------check *.h files-------------------------------------------------\n",file = w_f)
            print("-------------------------------check *.h files-------------------------------------------------\n",file = log_f)
        
            check_file(h_file_list,ignore_file_list,cmd)

            print("-------------------------------\
            check *.c files-------------------------------------------------\n",file = w_f)
            print("-------------------------------\
            check *.c files-------------------------------------------------\n",file = log_f)
            
            
            check_file(c_file_list,ignore_file_list,cmd)

            test_cmd_color.printYellow("check all files successful!\nchecked %d files,%d files failed,%d files ignored\nplease check the result in check_result\\annotation_fail_files.log\n\n"
                  % (Annotation.total_file_num,Annotation.fail_file_num,Annotation.ignore_file_num))
    elif (flag == 2):
            print("-------------------------------"
                  "check *.c files-------------------------------------------------\n",file = w_f)
            print("-------------------------------"
                  "check *.c files-------------------------------------------------\n",file = log_f)

            check_file(c_file_list,ignore_file_list,cmd)

            test_cmd_color.printYellow("check *.c files successful!\nchecked %d files,%d files failed,%d files ignored\nplease check the result in acheck_result\\annotation_fail_files.log\n\n" \
                  % (Annotation.total_file_num,Annotation.fail_file_num,Annotation.ignore_file_num))
    elif (flag == 3):
            print("-------------------------------"
                  "check *.h files-------------------------------------------------\n",file = w_f)
            print("-------------------------------"
                  "check *.h files-------------------------------------------------\n",file = log_f)
            check_file(h_file_list,ignore_file_list,cmd)

            test_cmd_color.printYellow("check *.h files successful!\nchecked %d files,%d files failed,%d files ignored\nplease check the result in check_result\\annotation_fail_files.log\n\n" \
                  % (Annotation.total_file_num,Annotation.fail_file_num,Annotation.ignore_file_num))
    else:
        pass

    # always output the ignore file list
    print("\n" + "-" * 50 + "ignore files list" + "-" * 50, file=fail_f)
    for line in Annotation.ignore_file_list:
        print(line, file=fail_f)
     
    #always 输出统计结果到log文件中
    print("\n\n--check file completed: check %d files  ,%d files failed,%d files ignored------------------\n\n" % (Annotation.total_file_num,Annotation.fail_file_num,Annotation.ignore_file_num),file = w_f)
    print("\n\n--check file completed: check %d files  ,%d files failed,%d files ignored \
    ------------------\n\n" % (Annotation.total_file_num, Annotation.fail_file_num,\
                               Annotation.ignore_file_num), file=log_f)
    print("\n\n--check file completed: check %d files  ,%d files failed,%d files ignored \
    ------------------\n\n" % (Annotation.total_file_num, Annotation.fail_file_num,\
                               Annotation.ignore_file_num), file=fail_f)
    
    
cmd = CmdTest()
cmd.cmdloop()





