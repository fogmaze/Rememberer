from operator import itemgetter
import parse
import os
import random
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

def openSettings():
    db_operator = DataBaseOperator()
    db_operator.cur.execute("select * from settings;")
    recv_data = db_operator.cur.fetchall()
    if not len(recv_data) == 1:
        raise
    wr_method,wr_tags,te_methods,te_tags,te_lp = recv_data[0]
    return {
        'wr':{
            "method":wr_method,
            "tags":wr_tags
        },
        "te":{
            "methods":decodeList(te_methods),
            "tags":te_tags,
            "load_provious":False if te_lp == 0 else True
        }
    }

def saveSettings(settings):
    db_operator = DataBaseOperator()
    data = (settings['wr']["method"], settings['wr']['tags'],encodeList(settings['te']['methods']), settings['te']['tags'], settings['te']['load_provious'],)
    db_operator.cur.execute("update settings set wr_method=?, wr_tags=?, te_methods=?, te_tags=?, te_lp=?",data)
    db_operator.con.commit()
    db_operator.close()

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
    TESTING_CMD_PROMPT = "input cmd (ex -> exit; n -> notes; d -> blacklist)"
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
            elif cmd == 'd':
                #add to blacklist
                db_operator = DataBaseOperator()
                db_operator.cur.execute('select testing_blacklist from {} where time={}'.format(self.TABLE_NAME,time))
                blacklist = decodeList(db_operator.cur.fetchone()[0])
                if self.METHOD_NAME not in blacklist:
                    blacklist.append(self.METHOD_NAME)
                db_operator.cur.execute('update {} set testing_blacklist="{}" where time={}'.format(
                    self.TABLE_NAME,
                    encodeList(blacklist),
                    time
                ))
                db_operator.close()
            else:
                break
            cmd = input(self.TESTING_CMD_PROMPT)
        return False

    def dataTestable(self,time):
        try:
            db_operator = DataBaseOperator()
            db_operator.cur.execute("select que,ans,testing_blacklist from {} where time={}".format(self.TABLE_NAME,time))
            recv = db_operator.cur.fetchall()
            if len(recv) != 1:
                raise Exception('{} datas found'.format(len(recv)))
            blacklist = decodeList(recv[0][2])
            if self.METHOD_NAME in blacklist:
                return False
            else:
                return self.queANDansIsTestable(recv[0][0], recv[0][1])
        finally:
            db_operator.close()
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
                sql_str = 'INSERT INTO {table} (que,ans,tags,time) VALUES("{que}","{ans}", "{tags}",strftime("%s","now"))'.format(
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
            sql_str = 'INSERT INTO {table} (que,ans,tags,time) VALUES("{que}","{ans}", "{tags}", strftime("%s","now"))'.format(
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
        db_operator.cur.execute('select method_name from {} where method_time={};'.format(NoteClass.TABLE_NAME,time))
        old_data = db_operator.cur.fetchall()

        is_added = False
        while len(old_data) > 0:
            data_buf = old_data.pop()
            if data_buf[0] == method_name:
                print('already added')
                is_added = True

        if not is_added:
            sql_str = 'insert into {tn} (que,ans,method_name,tags,time,method_time) values("{que}","{ans}","{method_name}","{tags}", strftime("%s","now"), {method_time})'.format(
                tn=NoteClass.TABLE_NAME,
                que=que,
                ans=ans,
                method_name=method_name,
                tags=tags,
                method_time=time
            )
            print('added to note')
            db_operator.cur.execute(sql_str)
        db_operator.close()
    def handle_operate_result(self, que, old_ans, ans, old_tags: str, tags: str) -> str:
        raise Exception('test only')
    def test_forFinish(self, time, settings) -> bool:
        db_operator = DataBaseOperator()
        db_operator.cur.execute("select method_name,tags,method_time from notes where time == {}".format(time))
        recv = db_operator.cur.fetchall()
        if len(recv) == 0:
            print("length of zero")
            finish = True
            return finish
        method_name, tags ,method_time = recv[0]

        db_operator.cur.execute('select que,ans from {} where time = {}'.format(MethodReflection_dict[method_name].TABLE_NAME,method_time))
        recv = db_operator.cur.fetchall()
        if len(recv) != 1:
            raise Exception('length error')
        que,ans = recv[0]

        method = MethodReflection_dict[method_name]

        tmp = method.TESTING_CMD_PROMPT 
        method.TESTING_CMD_PROMPT="input cmd(ex -> exit u -> remove from note):"
        print('#'*30)

        cmd = method.handle_testing_forResult(que,ans,method_time,tags,settings)

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

class EnGrammerClass(Method):
    TABLE_NAME = "en_gra"
    METHOD_NAME = "en_gra"

class EnVocabClass(Method):
    TABLE_NAME="en_voc"
    METHOD_NAME="en_voc"
    QUE_NAME = 'vocab'
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
        if ans == '*':
            return super().handle_operate_result(que,old_ans,ans,old_tags,tags)
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
        g -> grammer
        ex -> exit
        """
        all_method_dict = {
            "v":EnVocab,
            "p":EnPrep,
            "g":EnGrammer
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
            if len(definitions_and_kinds) > 1:
                print(kind)
            input('enter to see definition')
            if len(definitions_and_kinds) == 1:
                print(kind,end="")
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

def tg2list(tag_str:str):
    ret = []
    for e in tag_str.split("|"):
        ret.append(e.split("&"))
    return ret
def list2ttg(tag_list:List[list]):
    ret = []
    for e in tag_list:
        ret.append ("&".join(e))
    return "|".join(ret)

class Tester:
    settings=None
    data_left:List[Tuple[str,int]]=[]
    id=-1

    class Err_Zero_Data(Exception):
        pass
    
    def __init__(self,settings) -> None:
        self.settings = settings

        load = False
        if settings['load_provious']:
            ret = self.get_id()
            if not ret == -2:
                self.load_by_id(ret)
                load = True
                print('find provious id =',ret)
            else:
                print('cannot find provious record')
        if not load:
            self.setupNew()

        pass
    def save(self) -> bool:
        if len(self.data_left) == 0:
            return False
        db_operator = DataBaseOperator()
        db_operator.cur.executemany('insert into record_data(method_name,time,id) values(?,?,{})'.format(self.id),self.data_left)
        db_operator.close()
    def get_id(self):
        tg_list = tg2list(self.settings['tags'])
        tg_list.sort(key=itemgetter(0))
        for i in range(len(tg_list)):
            tg_list[i].sort()
        tg_str = list2ttg(tg_list)
        method_list = self.settings['methods']
        method_str = "|".join(sorted(self.settings['methods']))

        sql_str = 'select id from record_list where method_names="{}" and tags="{}"'.format(method_str,tg_str)
        db_operator = DataBaseOperator()
        db_operator.cur.execute(sql_str)
        recv = db_operator.cur.fetchall()
        if len(recv) == 1:
            return recv[0][0]
        if len(recv) == 0:
            return -2
        if len(recv) > 1:
            raise Exception('len error of {}'.format(len(recv)))

    def load_by_id(self,id):
        try:
            db_operator = DataBaseOperator()
            db_operator.cur.execute("select method_name,time from record_data where id={}".format(id))
            self.data_left = db_operator.cur.fetchall()
            self.id = id
            if len(self.data_left) == 0:
                print('zero data loaded')
            db_operator.cur.execute('delete from record_data where id=?',(id,))
            db_operator.con.commit()

        finally:
            db_operator.close()

    def setupNew(self):
        self.data_left = []
        self.reget()
        
        tg_list = tg2list(self.settings['tags'])
        tg_list.sort(key=itemgetter(0))
        for i in range(len(tg_list)):
            tg_list[i].sort()
        tg_str = list2ttg(tg_list)
        method_str = "|".join( sorted(self.settings['methods']))
        
        db_operator = DataBaseOperator()

        sql_str = 'select id from record_list where method_names="{}" and tags="{}"'.format(method_str,tg_str)
        db_operator.cur.execute(sql_str)
        recv = db_operator.cur.fetchall()
        if len(recv) == 0:
            sql_str = 'insert into record_list (method_names,tags) values("{}","{}")'.format(method_str,tg_str)
            db_operator.cur.execute(sql_str)
            db_operator.con.commit()
            sql_str = 'select id from record_list where method_names="{}" and tags="{}"'.format(method_str,tg_str)
            db_operator.cur.execute(sql_str)
            self.id = db_operator.cur.fetchall()
            print('create new record in id [{}]'.format(self.id))

        else:
            self.id = recv[0][0]
            sql_str = "delete from record_data where id={}".format(recv[0][0])
            db_operator.cur.execute(sql_str)
            db_operator.con.commit()
            print("using id [{}]".format(self.id))
        
        db_operator.close()

        

    def reget(self):
        try:
            db_operator = DataBaseOperator()
            

            for method_name in self.settings['methods']:

                sql_str = 'select time from {tn} where {all_limits}'.format(
                    tn = MethodReflection_dict[method_name].TABLE_NAME,
                    all_limits = getAllLimits(self.settings)
                )
                db_operator.cur.execute(sql_str)
                data_recieved = db_operator.cur.fetchall()
                if len(data_recieved) == 0:
                    print("no data match in cmd: " + sql_str)
                for eachData in data_recieved:
                    time = eachData[0]
                    if MethodReflection_dict[method_name].dataTestable(time):
                        self.data_left.append((method_name,time))

            if len(self.data_left) == 0:
                raise self.Err_Zero_Data()
        finally:
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
EnGrammer = EnGrammerClass()


MethodReflection_dict:Dict[str,Method] = {
    EnVocab.METHOD_NAME:EnVocab,
    EnPrep.METHOD_NAME:EnPrep,
    English.METHOD_NAME:English,
    EnVocab_def.METHOD_NAME:EnVocab_def,
    EnVocab_spe.METHOD_NAME:EnVocab_spe,
    Notes.METHOD_NAME:Notes,
    EnPrep_def.METHOD_NAME:EnPrep_def,
    EnPrep_ans.METHOD_NAME:EnPrep_ans,
    EnPerp_spe.METHOD_NAME:EnPerp_spe,
    EnGrammer.METHOD_NAME:EnGrammer
}

import os 
os.chdir(os.path.dirname(os.path.abspath(__file__)))