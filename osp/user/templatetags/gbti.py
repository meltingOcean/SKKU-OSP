def get_type_test(type1, type2, type3, type4):
    code = ""
    code += "E" if type4 > 0 else "I"
    code += "N" if type3 > 0 else "S"
    code += "T" if type2 > 0 else "F"
    code += "P" if type1 > 0 else "J"
    desc4 = ["Steady", "Fluid"]
    desc3 = ["Cool-head", "Warm-heart"]
    desc2 = ["Efficient", "Creative"]
    desc1 = ["Multiplayer", "Singleplayer"]
    descKR4 = ["꾸준하며", "유연하며"]
    descKR3 = ["냉철한 이성의", "따뜻한 마음씨의"]
    descKR2 = ["효율적인", "창의적인"]
    descKR1 = ["협동가", "자립가"]
    
    gbti_dict = {
        "ENFJ":{"code":"ENFJ", "nickname":"Twilight", "nicknameKR":"해 질 녘", "desc":" ".join([desc4[0], desc3[1], desc2[1], desc1[0]]), "descKR":" ".join([descKR4[0], descKR3[1], descKR2[1], descKR1[0]])},
        "INTJ":{"code":"INTJ", "nickname":"Deep Ocean", "nicknameKR":"심해", "desc":" ".join([desc4[0], desc3[0], desc2[1], desc1[1]]), "descKR":" ".join([descKR4[0], descKR3[0], descKR2[1], descKR1[1]])},
        "ESFJ":{"code":"ESFJ", "nickname":"Morning Dew", "nicknameKR":"아침 이슬", "desc":" ".join([desc4[0], desc3[1], desc2[0], desc1[0]]), "descKR":" ".join([descKR4[0], descKR3[1], descKR2[0], descKR1[0]])},
        "ISTJ":{"code":"ISTJ", "nickname":"Fog City", "nicknameKR":"안개 도시", "desc":" ".join([desc4[0], desc3[0], desc2[0], desc1[1]]), "descKR":" ".join([descKR4[0], descKR3[0], descKR2[0], descKR1[1]])},
        "ISTP":{"code":"ISTP", "nickname":"Summer Shower", "nicknameKR":"소나기", "desc":" ".join([desc4[1], desc3[0], desc2[0], desc1[1]]), "descKR":" ".join([descKR4[1], descKR3[0], descKR2[0], descKR1[1]])},
        "INFP":{"code":"INFP", "nickname":"Snowflake", "nicknameKR":"눈송이", "desc":" ".join([desc4[1], desc3[1], desc2[1], desc1[1]]), "descKR":" ".join([descKR4[1], descKR3[1], descKR2[1], descKR1[1]])},
        "ENFP":{"code":"ENFP", "nickname":"Rainbow Cloud", "nicknameKR":"무지개 구름", "desc":" ".join([desc4[1], desc3[1], desc2[1], desc1[0]]), "descKR":" ".join([descKR4[1], descKR3[1], descKR2[1], descKR1[0]])},
        "ISFJ":{"code":"ISFJ", "nickname":"Salt Lake", "nicknameKR":"염수호", "desc":" ".join([desc4[0], desc3[1], desc2[0], desc1[1]]), "descKR":" ".join([descKR4[0], descKR3[1], descKR2[0], descKR1[1]])},
        "INFJ":{"code":"INFJ", "nickname":"Moonlight", "nicknameKR":"달빛", "desc":" ".join([desc4[0], desc3[1], desc2[1], desc1[1]]), "descKR":" ".join([descKR4[0], descKR3[1], descKR2[1], descKR1[1]])},
        "ESFP":{"code":"ESFP", "nickname":"Spring Breeze", "nicknameKR":"봄바람", "desc":" ".join([desc4[1], desc3[1], desc2[0], desc1[0]]), "descKR":" ".join([descKR4[1], descKR3[1], descKR2[0], descKR1[0]])},
        "ISFP":{"code":"ISFP", "nickname":"Cherry Blossom", "nicknameKR":"벚꽃", "desc":" ".join([desc4[1], desc3[1], desc2[0], desc1[1]]), "descKR":" ".join([descKR4[1], descKR3[1], descKR2[0], descKR1[1]])},
        "ENTJ":{"code":"ENTJ", "nickname":"Dawn Breathe", "nicknameKR":"새벽 숨", "desc":" ".join([desc4[0], desc3[0], desc2[1], desc1[0]]), "descKR":" ".join([descKR4[0], descKR3[0], descKR2[1], descKR1[0]])},
        "INTP":{"code":"INTP", "nickname":"Blue Hour", "nicknameKR":"여명 빛", "desc":" ".join([desc4[1], desc3[0], desc2[1], desc1[1]]), "descKR":" ".join([descKR4[1], descKR3[0], descKR2[1], descKR1[1]])},
        "ESTJ":{"code":"ESTJ", "nickname":"Dune Line", "nicknameKR":"사구선", "desc":" ".join([desc4[0], desc3[0], desc2[0], desc1[0]]), "descKR":" ".join([descKR4[0], descKR3[0], descKR2[0], descKR1[0]])},
        "ESTP":{"code":"ESTP", "nickname":"Lightning Flash", "nicknameKR":"번개 섬광", "desc":" ".join([desc4[1], desc3[0], desc2[0], desc1[0]]), "descKR":" ".join([descKR4[1], descKR3[0], descKR2[0], descKR1[0]])},
        "ENTP":{"code":"ENTP", "nickname":"Blinking Star", "nicknameKR":"깜박이별", "desc":" ".join([desc4[1], desc3[0], desc2[1], desc1[0]]), "descKR":" ".join([descKR4[1], descKR3[0], descKR2[1], descKR1[0]])},
    }
    gbti_combi_dict = {
        "ENFJ":{"pos":["INFP"], "neg":["ISTJ"]},
        "INTJ":{"pos":["ENTP"], "neg":["ESFJ"]},
        "ESFJ":{"pos":["ISFP"], "neg":["INTJ"]},
        "ISTJ":{"pos":["ESTP"], "neg":["ENFJ"]},
        "ISTP":{"pos":["ESTJ"], "neg":["ENFP"]},
        "INFP":{"pos":["ENFJ"], "neg":["ESTP"]},
        "ENFP":{"pos":["INFJ"], "neg":["ISTP"]},
        "ISFJ":{"pos":["ESFP"], "neg":["ENTJ"]},
        "INFJ":{"pos":["ENFP"], "neg":["ESTJ"]},
        "ESFP":{"pos":["ISFJ"], "neg":["INTP"]},
        "ISFP":{"pos":["ESFJ"], "neg":["ENTP"]},
        "ENTJ":{"pos":["INTP"], "neg":["ISFJ"]},
        "INTP":{"pos":["ENTJ"], "neg":["ESFP"]},
        "ESTJ":{"pos":["ISTP"], "neg":["INFJ"]},
        "ESTP":{"pos":["ISTJ"], "neg":["INFP"]},
        "ENTP":{"pos":["INTJ"], "neg":["ISFP"]},
    }
    gbti_dict[code]["pos"] = [gbti_dict[pos_code] for pos_code in gbti_combi_dict[code]["pos"]]
    gbti_dict[code]["neg"] = [gbti_dict[neg_code] for neg_code in gbti_combi_dict[code]["neg"]]
    return gbti_dict[code]

def get_type_analysis(type_list):
    icon = {
        "icon0":["bi-sun-fill", "bi-moon-fill"],
        "icon1":["bi-lightning-fill", "bi-tree-fill", "bi-fire"],
        "icon2":["bi-people-fill", "bi-person-fill"]
    }
    msg = {
        "msg0":["Sunflower", "Night Owl"],
        "msg1":["Initiator", "Evergreen", "Burning"],
        "msg2":["Together", "Independent"]
    }
    msgKR = {
        "msgKR0":["주로 낮에 활동합니다.", "주로 밤에 활동합니다."],
        "msgKR1":["프로젝트 초반에 주로 활약합니다.", "프로젝트에 전반적으로 활약합니다.", "프로젝트 후반에 주로 활약합니다."],
        "msgKR2":["함께 작업하는 편입니다.", "혼자서 작업하는 편입니다."]
    }
    
    result, resultKR, result_icon = [], [], []
    def split_type(k, n, crtr=[0]):
        if n == 2:
            if type_list[int(k)] < crtr[0]:
                result.append(msg["msg"+k][0])
                resultKR.append(msgKR["msgKR"+k][0])
                result_icon.append(icon["icon"+k][0])
            else:
                result.append(msg["msg"+k][1])
                resultKR.append(msgKR["msgKR"+k][1])
                result_icon.append(icon["icon"+k][1])
        elif n == 3:
            if type_list[int(k)] < crtr[0]:
                result.append(msg["msg"+k][0])
                resultKR.append(msgKR["msgKR"+k][0])
                result_icon.append(icon["icon"+k][0])
            elif type_list[int(k)] < crtr[1]:
                result.append(msg["msg"+k][1])
                resultKR.append(msgKR["msgKR"+k][1])
                result_icon.append(icon["icon"+k][1])
            else:
                result.append(msg["msg"+k][2])
                resultKR.append(msgKR["msgKR"+k][2])
                result_icon.append(icon["icon"+k][2])
    
    split_type("0", 2, [0])
    split_type("1", 3, [-0.4, 0.4])
    split_type("2", 2, [0])
    
    return result, resultKR, result_icon
