from core import *


def test():
    settings = openJsonFile("tester_default.json")
    cmd_handler(settings)


def cmd_handler(settings):
    cmd_help = """
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

def findProviousSave(settings) -> Tester:
    tester_obj = None
    save_name_buf = ""
    saves = os.listdir('./records')
    now_method_name = '&'.join(settings['methods'])
    now_tags = settings['tags']
    for old_save in saves:
        date,methods,tags = parse.parse('{}[{}][{}]',old_save).fixed
        if now_method_name == methods and now_tags == tags:
            if tester_obj != None:
                os.remove(save_name_buf)
            print('loading save:',old_save)
            tester_obj = Tester()
            tester_obj.load(os.path.join('./records', old_save))
            save_name_buf = old_save
    return tester_obj

def starttest(settings):
    try:
        finish = False
        data = findProviousSave(settings)
        if data == None:
            data = Tester()
            data.setupNew(settings)
        while not finish:
            try:
                print("{} questions left".format(len(data.data_left)))
                method_name,time = data.random_one_question()
                finish = MethodReflection_dict[method_name].test_forFinish(time,settings)
            except Tester.Err_Zero_Data:
                print('gather zero data')
                finish = True
    finally:
        print('saving')
        data.save("./records",autoName=True)

def changeSettings(settings,cmd_default=[]):
    finish = False
    flag_names = """
    m -> test methods name
    dp -> datebase_path
    tg -> tags
    """
    flag_names_dict = {
        "m":"methods",
        "dp":"db_path",
        "tg":"tags"
    }

    method_set_dict = {
        'en_all':'en_voc_def|en_voc_spe|en_prep_def|en_prep_ans|en_prep_spe'
    }

    def getCMD(hint=""):
        if len(cmd_default) > 0:
            cmd = cmd_default.pop(0)
            print(hint + cmd)
            return cmd
        return input(hint)
    
    if len(cmd_default) > 0:
        cmd_default.append("ex")
    while not finish:
        print(flag_names)
        flag = getCMD("input flag (ex -> exit): ")
        if flag == "ex":
            finish = True
        elif flag == "m":
            obj_str = getCMD("input object (to split, use '|'): ")
            if obj_str in method_set_dict:
                obj_str = method_set_dict[obj_str]
            settings['methods'] = decodeList(obj_str)
        elif flag in flag_names_dict:
            settings[flag_names_dict[flag]] = getCMD("input object: ")
        else:
            print("cannot recognize flag: " + flag)
    saveJsonFile("tester_default.json",settings)
    return settings

def print_test_settings(settings):
    print("{:=^40s}".format("Test Settings"))
    print("test method:\t " + str(settings["methods"]))
    print("tags: \t{}".format(settings["tags"]))
    print("{:*^40s}".format(""))


if __name__ =="__main__":
    test()