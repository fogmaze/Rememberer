from core import *


def test():
    settings = openJsonFile("tester_default.json")
    cmd_handler(settings)


def cmd_handler(settings):
    cmd_help = """commands
    ch   -> change settings
    ex   -> exit
    else -> start operating
    """
    while True:
        print_test_settings(settings)
        print(cmd_help)
        cmd = input("input command: ").split(' ')
        if cmd[0] == "ch":
            settings = changeSettings(settings,cmd[1:])
        elif cmd[0] == "ex":
            break
        else:
            starttest(settings)

def starttest(settings):
    finish = False
    data = Tester(settings)
    try:
        while not finish:
            try:
                print("{} questions left".format(len(data.data_left)))
                method_name,time = data.random_one_question()
                finish = MethodReflection_dict[method_name].test_forFinish(time,settings)
            except Tester.Err_Zero_Data:
                print('gather zero data')
                finish = True
    finally:
        if data:
            print('saving')
            data.save()

def changeSettings(settings,cmd_default=[]):
    finish = False
    flag_names = """flag names
    m -> test methods name
    dp -> datebase_path
    tg -> tags
    l -> load privious
    """

    method_set_dict = {
        'en_all':'en_voc_def|en_voc_spe|en_prep_def|en_prep_ans|en_prep_spe',
        'def':'en_voc_def|en_prep_def',
        'ans':'en_prep_spe|en_voc_spe'
    }

    def getCMD(hint=""):
        if len(cmd_default) > 0:
            cmd = cmd_default.pop(0)
            print(hint + cmd)
            return cmd
        return input(hint)
    def method_translateInput(input_value:str):
        if input_value in method_set_dict:
            return decodeList(method_set_dict[input_value])
        return decodeList(input_value)
    def tf_translateInput(input_value:str):
        trues = ['t','T','true','True']
        falses = ['f','F','false','False']
        while True:
            if input_value in trues:
                return True
            elif input_value in falses:
                return False
            input_value = input('pls input again')
    def tg_translateInput(input_value:str):
        tag_set_dict = {
            'p1':'2209_1|2209_2|2209_3|2209_4|1_1|1_2|1_3|1_review'
        }
        if input_value in tag_set_dict:
            input_value = tag_set_dict[input_value]
        return input_value

    flag_names_dict = {
        "m":("methods",method_translateInput),
        "tg":("tags",tg_translateInput),
        "l":("load_provious",tf_translateInput)
    }
        
    
    if len(cmd_default) > 0:
        cmd_default.append("ex")
    while not finish:
        print(flag_names)
        flag = getCMD("input flag (ex -> exit): ")
        if flag == "ex":
            finish = True
        elif flag in flag_names_dict:
            inp = flag_names_dict[flag][1](getCMD("input object: "))
            settings[flag_names_dict[flag][0]] = inp
        else:
            print("cannot recognize flag: " + flag)
    saveJsonFile("tester_default.json",settings)
    return settings

def print_test_settings(settings):
    print("{:=^40s}".format("Test Settings"))
    print("test method:\t " + str(settings["methods"]))
    print("tags: \t{}".format(settings["tags"]))
    print("load provious:\t " + str(settings["load_provious"]))
    print("{:*^40s}".format(""))


if __name__ =="__main__":
    test()