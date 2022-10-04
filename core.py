import parse
import os
import pickle
from datetime import datetime
import random
import json
import sqlite3 as sql
from typing import Dict, List, Tuple


def decodeList(str:str) -> List[str]:
    if str == "":
        return []
    return str.split('|')
def encodeList(list:List[str]) -> str:
    return '|'.join(list)
def mergeEncodedList(strs:Tuple[str]):
    all_tags = []
    for str in strs:
        all_tags_in_str = decodeList(str)
        for tag in all_tags_in_str:
            if tag not in all_tags:
                all_tags.append(tag)
    return encodeList(all_tags)

def decodeTags(tagss:str) -> List[List[str]]:
    res = []
    tags = tagss.split('|')
    for tag in tags:
        res.append(tag.split('&'))
    return res
def encodeTags(list:List[List[str]]) -> str:
    tags_strs = []
    for tag in list:
        tags_strs.append('&'.join(tag))
    return '|'.join(tags_strs)
def mergeEncodedTags(strs:Tuple[str]):
    all_tags = []
    for str in strs:
        all_tags_in_str = decodeTags(str)
        for tag in all_tags_in_str:
            if tag not in all_tags:
                all_tags.append(tag)
    return encodeTags(all_tags)
    

def openJsonFile(path:str):
    with open(path,'r') as f:
        return json.load(f)
    
def saveJsonFile(path:str,obj,indent=4):
    with open(path,'w') as f:
        return json.dump(obj,f,indent=indent)

def getFilterFromSettings(settings)->str:
    tagLimit_d = decodeTags(settings['tags'])
    if len(tagLimit_d) == 0:
        return ""

    tag_limits = []
    for lim in tagLimit_d:
        condition = []
        for tag in lim:
            condition.append('tags like "%{}%"'.format(tag))
        tag_limits.append('(' + " AND ".join(condition) + ")")
    tag_limits = '(' + ' OR '.join(tag_limits) + ')'
    result = ""
    result += tag_limits
    return result

    raise Exception("developing")
    return result

def getAllLimits(settings) -> str:
    all_limit = ""
    all_limit += getFilterFromSettings(settings)
    return all_limit

class DataBaseOperator():
    def __init__(self):
        self.con = sql.connect(db_path)
        self.cur = self.con.cursor()
    def close(self):
        self.con.commit()
        self.cur.close()
        self.con.close()

class Method:
    TABLE_NAME = "default"
    METHOD_NAME = "default"
    PROMPT_AFTER_ASKING_QUESTION_IN_TEST = "enter for answer"
    TESTING_CMD_PROMPT = "input cmd (ex -> exit; n -> add to notes)"
    QUE_NAME = 'que'
    ANS_NAME = 'ans'
    length:None
    def calculateLength(self,settings=None) -> int:
        db_operator = DataBaseOperator()
        db_operator.cur.execute("SELECT count(*) FROM {}".format(self.TABLE_NAME))
        length = db_operator.cur.fetchone()
        db_operator.close()
        self.length = length
        return length
    def __len__(self):
        if self.length != None:
            return self.length
        return self.calculateLength()
    def operate(self,settings):
        finish = False
        while not finish:
            finish = self.operate_one(settings)
    def operate_one(self,settings) -> bool:
        db_operator = DataBaseOperator()
        que = input("input {} (ex -> exit): ".format(self.QUE_NAME))
        ans = ""
        old_tags = ""
        old_ans = ""
        #exit
        if que == "ex":
            return True

        #que that already been there
        sql_str = 'SELECT ans,tags FROM {} WHERE que == "{}"'.format(self.TABLE_NAME,que)
        db_operator.cur.execute(sql_str)
        old_data = db_operator.cur.fetchall()
        if len(old_data) == 1:
            old_ans,old_tags= old_data[0]
            print("It is already added in tag {}".format(old_tags))
            print("By answer: {}".format(old_ans))
            
            print('to add more answers pls put "|" in the front')
            print('to create new data  pls put ";" in the front')
            print('to only flag it use "*" ')
        if len(old_data) > 1:
            print("error more than one ansinition found")
            return

        ans = input("input {}: ".format(self.ANS_NAME))
        tags = settings["tags"]
        sql_str = self.handle_operate_result(que,old_ans,ans,old_tags,tags)

        if ans == "nope":
            sql_str = ""

        db_operator.cur.execute(sql_str)
        db_operator.close()
        return False
    
    def getAnsAndQueFromSql(self,settings,sql_str:str) -> List[tuple]:
        db_operator = DataBaseOperator()
        db_operator.cur.execute(sql_str)
        recv = db_operator.cur.fetchall()
        db_operator.close()
        return recv
        
    def test_forFinish(self,time,settings) -> bool:
        recv = self.getAnsAndQueFromSql(settings,'select que,ans,tags from {tn} where time=={time}'.format(tn=self.TABLE_NAME,time=time))

        if len(recv) != 1:
            raise Exception('length error' + str(len(recv)))
        recv_que = recv[0][0]
        recv_ans = recv[0][1]
        recv_tags = recv[0][2]
        print("")
        print("#"*30)
        print(self.METHOD_NAME + ":")
        cmd = self.handle_testing_forResult(recv_que,recv_ans,time,recv_tags,settings)
        return self.handle_testing_cmd_forFinish(cmd,recv_que,recv_ans,time,recv_tags,settings)


    def handle_testing_forResult(self,que,ans,time,tags,settings)->str:
        print(que)
        inp = input()
        print(ans)
        inp = input(self.TESTING_CMD_PROMPT)
        return inp
    
    def handle_testing_cmd_forFinish(self, cmd, que, ans, time, tags, settings):
        while True:
            if cmd == 'ex':
                return True
            elif cmd == 'n': 
                NoteClass.takeNote(que, ans, self.METHOD_NAME, tags, time,settings)
                cmd = input(self.TESTING_CMD_PROMPT)
            else:
                break
        return False

    def queANDansIsTestable(self,que,ans) -> bool:
        return True
        

    def handle_operate_result(self,que,old_ans,ans,old_tags:str,tags:str) -> str:
        if ans == "":
            print("answer cannot be blank")
            return ""

        #question already exists
        if old_ans != "":
            if ans[0] == '*':
                sql_str = 'UPDATE {table} SET tags="{tags}",time=strftime("%s","now") WHERE que == "{que}"'.format(
                    table=self.TABLE_NAME,
                    tags=mergeEncodedList((old_tags,tags)),
                    que=que
                )
                return sql_str

            if ans[0] == ';':
                sql_str = 'INSERT INTO {table} VALUES("{que}","{ans}", 0, 0,"{tags}",strftime("%s","now"))'.format(
                    table=self.TABLE_NAME,
                    que=que,
                    ans=ans[1:],
                    tags=tags
                )
                return sql_str

            ans_all = ans

            if ans[0] == '|':
                ans_all = old_ans + ans
            
            sql_str = 'UPDATE {table} SET ans="{ans}",tags="{tags}",time=strftime("%s","now") WHERE que == "{que}"'.format(
                table=self.TABLE_NAME,
                ans=ans_all,
                tags=mergeEncodedList((old_tags,tags)),
                que=que
            )
            return sql_str
        else: 
            #new question
            sql_str = 'INSERT INTO {table} VALUES("{que}","{ans}", 0, 0,"{tags}",strftime("%s","now"))'.format(
                table=self.TABLE_NAME,
                que=que,
                ans=ans,
                tags=tags
            )
            return sql_str

class NoteClass(Method):
    TABLE_NAME="notes"
    METHOD_NAME="notes"
    @staticmethod
    def takeNote(que,ans,method_name,tags,time,settings):
        db_operator = DataBaseOperator()
        db_operator.cur.execute('select que,method_name from {} where time={};'.format(NoteClass.TABLE_NAME,time))
        old_data = db_operator.cur.fetchall()

        is_added = False
        while len(old_data) > 0:
            data_buf = old_data.pop()
            if data_buf[0] == que and data_buf[1] == method_name:
                print('already added')
                is_added = True

        if not is_added:
            sql_str = 'insert into {tn} values("{que}","{ans}","{method_name}","{tags}",{time})'.format(
                tn=NoteClass.TABLE_NAME,
                que=que,
                ans=ans,
                method_name=method_name,
                tags=tags,
                time=time
            )
            print('added to note')
            db_operator.cur.execute(sql_str)
        db_operator.close()
    def handle_operate_result(self, que, old_ans, ans, old_tags: str, tags: str) -> str:
        raise Exception('test only')
    def test_forFinish(self, time, settings) -> bool:
        db_operator = DataBaseOperator()
        db_operator.cur.execute("select method_name,que,ans,tags from notes where time == {}".format(time))
        recv = db_operator.cur.fetchall()
        if len(recv) == 0:
            print("length of zero")
            finish = True
            return finish
        method_name, que, ans, tags = recv[0]
        

        method = MethodReflection_dict[method_name]

        tmp = method.TESTING_CMD_PROMPT 
        method.TESTING_CMD_PROMPT="input cmd(ex -> exit u -> remove from note):"
        print('#'*30)
        cmd = method.handle_testing_forResult(que,ans,time,tags,settings)
        method.TESTING_CMD_PROMPT = tmp
        
        finish = False 
        if "u" in cmd:
            sql_str = 'delete from {} where time=={} and method_name=="{}"'.format(NoteClass.TABLE_NAME,time,method_name)
            db_operator.cur.execute(sql_str)
            print('removed [{}] from notes'.format(que))
        if "ex" in cmd:
            finish = True
        db_operator.close()
        return finish


class EnVocabClass(Method):
    TABLE_NAME="en_voc"
    METHOD_NAME="en_voc"
    QUE_NAME = 'covab'
    ANS_NAME = 'definition'
    @staticmethod
    def splitDifinitionAndKind(definition:str):
        defi=definition
        kind = ""
        try:
            defi,kind = parse.parse("{} {}",definition).fixed
        except:
            pass
        return defi,kind

class EnPrepClass(Method):
    TABLE_NAME = "en_prep"
    METHOD_NAME= "en_prep"
    QUE_NAME = '[words(use ? to replace )]'
    ANS_NAME = '[hard words (use _ to split each)]:[definition]'
    def handle_operate_result(self, que:str, old_ans, ans:str, old_tags: str, tags: str) -> str:
        que_len = len(que.split('?'))
        ans_len = len(ans.split('_'))
        if not que_len == ans_len + 1:
            print("question length and answer length do not match")
            return ""
        if ":" not in ans:
            print("pls enter ans with definition")
            return ""
        return super().handle_operate_result(que, old_ans, ans, old_tags, tags)

class EnglishClass(Method):
    METHOD_NAME="en"
    def operate(self,settings):
        all_method = """\tAll Method:
        v -> vocab,
        p -> prep,
        ex -> exit
        """
        all_method_dict = {
            "v":EnVocab,
            "p":EnPrep
        }
        finish = False
        while not finish:
            print(all_method)
            method = input()
            if method == 'ex':
                finish = True
                break
            if method not in all_method_dict:
                print("cannot recognize method: " + method)
                continue
            method_one = all_method_dict[method].operate_one
            finish = method_one(settings)
    

class EnVocabClass_def(EnVocabClass):
    METHOD_NAME="en_voc_def"
    def handle_testing_forResult(self, que, ans, time, tags, settings) -> str:
        definitions_and_kinds = decodeList(ans)
        
        print(que)
        print("Q: What's the definition? [{}])".format(len(definitions_and_kinds)))
        cmd = ""
        for dk in definitions_and_kinds:
            kind,definition= self.splitDifinitionAndKind(dk)
            print(kind)
            input('enter to see definition')
            print(definition)
        cmd = input(self.TESTING_CMD_PROMPT)
        return cmd
    #-w for writting only
    def queANDansIsTestable(self, que, ans) -> bool:
        if '-w' in que:
            return False
        return True
class EnVocabClass_spe(EnVocabClass):
    METHOD_NAME="en_voc_spe"
    def handle_testing_forResult(self, que, ans, time, tags, settings) -> str:
        cmd = ""
        print(ans)
        print("Q: How to spell? ")
        hint_len = 0
        while True:
            print(self.maskStr(que,hint_len))
            cmd = input("enter to see the word or 'h' for a letter: ")
            if cmd == 'h':
                hint_len += 1
            else:
                print(que)
                print("")
                break
        cmd = input(self.TESTING_CMD_PROMPT)
        return cmd
    @staticmethod
    def maskStr(ans:str,hint_len):
        result = ""
        for i in range(len(ans)):
            if i < hint_len:
                result += ans[i]
            elif ans[i] == ' ':
                result += ' '
            else:
                result += '.'
        return result

class EnPrepClass_def(EnPrepClass):
    METHOD_NAME="en_prep_def"
    @staticmethod
    def merge_que_ans(que:str,ans:str):
        que_frag = que.split("?")
        ans_frag = ans.split("_")
        final_result = ""
        while len(ans_frag) > 0:
            final_result += que_frag.pop(0)
            final_result += ans_frag.pop(0)
        final_result += que_frag.pop(0)
        return final_result
    def handle_testing_forResult(self, que, ans, time, tags, settings) -> str:
        cmd = ""
        ans_ans,ans_def = ans.split(":")
        print(EnPrep_def.merge_que_ans(que,ans_ans))
        print("Q: What's the word mean? ")
        input('enter to see the answer')
        print(ans_def)
        cmd = input(self.TESTING_CMD_PROMPT)
        return cmd

    #-w for writting only
    def queANDansIsTestable(self, que, ans) -> bool:
        if '-w' in que:
            return False
        return True

class EnPrepClass_ans(EnPrepClass):
    METHOD_NAME="en_prep_ans"
    def handle_testing_forResult(self, que, ans, time, tags, settings) -> str:
        cmd = ""
        ans_ans,ans_def = ans.split(":")
        print('{}:{}'.format(que,ans_def))
        print("Q: What's in the blank? ")
        input('enter to see the answer')
        print(ans_ans)
        cmd = input(self.TESTING_CMD_PROMPT)
        return cmd
    
class EnPrepClass_spe(EnPrepClass):
    METHOD_NAME="en_prep_spe"
    def handle_testing_forResult(self, que, ans, time, tags, settings) -> str:
        cmd = ""
        ans_ans,ans_def = ans.split(":")
        hole_words = EnPrep_def.merge_que_ans(que,ans_ans).split(' ')
        print(ans_def)
        print("Q: What's the missing words?")
        prompt_len = 0
        while True:
            print(' '.join(hole_words[0: prompt_len]), "__ " * (len(hole_words) - prompt_len) )
            cmd = input("enter to see the word or 'h' for a word")
            if cmd == 'h':
                prompt_len += 1
            else:
                break
        print(' '.join(hole_words))
        cmd = input(self.TESTING_CMD_PROMPT)
        return cmd

    #-w for writting only
    def queANDansIsTestable(self, que, ans) -> bool:
        if '-w' in que:
            return False
        return True

class Tester:
    @staticmethod
    def getName_AUTO(settings):
        nowT = datetime.now()
        
        return "{date}_[{methods}][{tags}]".format(
            date=nowT.strftime("%m~%d~%Y"),
            methods='&'.join(settings['methods']),
            tags=settings['tags']
        )

    settings=None
    data_left:List[Tuple[str,int]]=[]
    data_path=None
    
    def save(self,path = None,autoName = True) -> bool:
        if len(self.data_left) == 0:
            return False
        if path != None:
            filename = path
            if autoName:
                filename=os.path.join(filename,self.getName_AUTO(self.settings))
            with open(filename,'w') as f:
                lines = [str(data)+'\n' for data in self.data_left]
                f.writelines(lines)
            return True
        if self.data_path == None:
            print('file path not set')
            return False
        with open(path,'wb') as f:
            raise Exception('e')

    def load(self,path):
        with open(path,'r') as f:
            self.data_left = []
            lines = f.readlines()
            for line in lines:
                method_name, time = parse.parse("('{}', {})\n",line).fixed
                time = int(time)
                self.data_left.append(tuple((method_name,time)))
            _,methods,tags = parse.parse('{}[{}][{}]',path).fixed
            self.settings = {
                'methods':methods.split("&"),
                'tags':tags
            }
            self.data_path = path

    def setupNew(self,settings,path:str=None):
        self.settings = settings
        self.data_path = path
        self.reget()

    class Err_Zero_Data(Exception):
        pass

    def reget(self):
        db_operator = DataBaseOperator()

        for method_name in self.settings['methods']:
            sql_str = 'select time,que,ans from {tn} where {all_limits}'.format(
                tn = MethodReflection_dict[method_name].TABLE_NAME,
                all_limits = getAllLimits(self.settings)
            )
            db_operator.cur.execute(sql_str)
            data_recieved = db_operator.cur.fetchall()
            if len(data_recieved) == 0:
                print("no data match in cmd: " + sql_str)
            for eachData in data_recieved:
                if MethodReflection_dict[method_name].queANDansIsTestable(eachData[1],eachData[2]):
                    self.data_left.append((method_name,eachData[0]))

        if len(self.data_left) == 0:
            raise self.Err_Zero_Data()
        db_operator.close()
    
    def random_one_question(self) -> Tuple[str,int]:
        all_data_len = len(self.data_left)
        if all_data_len == 0:
            print("length of question is 0")
            print("regenerating provious question")
            self.reget()
            return self.random_one_question()
        seed = random.randrange(0,all_data_len)
        return self.data_left.pop(seed)

def testDataGen(settings,data:Tester=None):
    if data == None:
        data = Tester()
        data.setupNew(settings)
    while True:
        yield data.random_one_question()
# constants
db_path = "./highSchool.db"

English = EnglishClass()
EnVocab = EnVocabClass()
EnVocab_def = EnVocabClass_def()
EnVocab_spe = EnVocabClass_spe()
EnPrep = EnPrepClass()
EnPrep_def = EnPrepClass_def()
EnPrep_ans = EnPrepClass_ans()
EnPerp_spe = EnPrepClass_spe()
Notes = NoteClass()

MethodReflection_dict:Dict[str,Method] = {
    EnVocab.METHOD_NAME:EnVocab,
    EnPrep.METHOD_NAME:EnPrep,
    English.METHOD_NAME:English,
    EnVocab_def.METHOD_NAME:EnVocab_def,
    EnVocab_spe.METHOD_NAME:EnVocab_spe,
    Notes.METHOD_NAME:Notes,
    EnPrep_def.METHOD_NAME:EnPrep_def,
    EnPrep_ans.METHOD_NAME:EnPrep_ans,
    EnPerp_spe.METHOD_NAME:EnPerp_spe
}
import os 
os.chdir(os.path.dirname(os.path.abspath(__file__)))