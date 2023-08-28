"""
@Auth: Lin yunxiao
@Description: 提取xml中的三元组.
"""
import xml.etree.ElementTree as ET
import pandas as pd
import random
import string
import os
import time


# 每个节点唯一的ID
# 生成指定长度的不重复随机数字ID
def generate_random_id(length):
    # 已生成的ID列表
    generated_ids = []
    while True:
        id = ''.join(random.choices(string.digits, k=length))
        if id not in generated_ids:
            generated_ids.append(id)
            return id


def entity_content1(patent, path, label):
    p_dict = {}
    p_dict[':ID'] = generate_random_id(12)
    p_dict['name'] = patent.findtext(path)
    p_dict[':LABEL'] = label
    return p_dict


def entity_content2(patent, path1, path2, label):
    p_dict = {}
    p_dict[':ID'] = generate_random_id(12)
    p_dict['name'] = patent.findtext(path1) + \
                     patent.findtext(path2)
    p_dict[':LABEL'] = label
    return p_dict


def entity_content3(patent, path1, path2, path3, label):
    p_dict = {}
    p_dict[':ID'] = generate_random_id(12)
    p_dict['name'] = patent.findtext(path1) + \
                     patent.findtext(path2) + \
                     patent.findtext(path3)
    p_dict[':LABEL'] = label
    return p_dict


# sid为title_id
def get_relation(sid, n, eid, typ):
    relation_dict = {}
    relation_dict[':START_ID'] = sid
    relation_dict['name'] = n
    relation_dict[':END_ID'] = eid
    relation_dict[':TYPE'] = typ
    return relation_dict


# 批量读取多级文件，几个for就是几级文件，os.path.join也是一级文件
# p_folder是根目录中的下下一级文件
def find_xml_files(root_folder, p_folder):
    xml_file = []
    for grant_patent in os.scandir(root_folder):
        folder = os.path.join(grant_patent.path, p_folder)
        for entry in os.scandir(folder):
            create_folder = os.path.join(entry.path, 'CREATE')
            for file_entry in os.scandir(create_folder):
                for file in os.scandir(file_entry):
                    for fi in os.scandir(file):
                        if fi.is_file() and fi.name.endswith('.XML'):
                            xml_file.append(fi.path)
    return xml_file


def exam_entity(eid, dupli, fd):
    for item in dupli:
        if eid == item[':ID']:
            eid = fd[item['name']]
            break
    return eid


def grant_patent(result, first_dup, jishu):
    # start_cpu = time.process_time()  # 记录开始 CPU 时间
    root_folder = r'G:\19个行业专利数据'  # 专利数据存储路径
    xml_files = find_xml_files(root_folder, 'BIBLIOGRAPHIC_INVENTION_GRANT')

    for file in xml_files:
        # 解析XML文件并提取所需信息
        tree = ET.parse(file)
        root = tree.getroot()

        # 记录写入表格的实体、关系
        patent_list = []
        relation_list = []

        # root.findall查找子节点，查找孙节点得加.//
        for patent in root.findall('.//PatentDocument'):
            # 实体1
            Appli_orig = entity_content2(patent,
                                         './/ApplicationInfo[@dataFormat="original"]/DocumentID/Country',
                                         './/ApplicationInfo[@dataFormat="original"]/DocumentID/Number',
                                         'Appli_orig')
            patent_list.append(Appli_orig)

            # 实体2
            Appli_orig_d = entity_content1(patent,
                                           './/ApplicationInfo[@dataFormat="original"]/DocumentID/Date',
                                           'Appli_orig_d')
            patent_list.append(Appli_orig_d)

            # 实体3
            Appli_ipph = entity_content2(patent,
                                         './/ApplicationInfo[@dataFormat="ipph"]/DocumentID/Country',
                                         './/ApplicationInfo[@dataFormat="ipph"]/DocumentID/Number',
                                         'Appli_ipph')
            patent_list.append(Appli_ipph)

            # 实体4
            Appli_ipph_d = entity_content1(patent,
                                           './/ApplicationInfo[@dataFormat="ipph"]/DocumentID/Date',
                                           'Appli_ipph_d')
            patent_list.append(Appli_ipph_d)

            # 实体5
            Publi_orig = entity_content3(patent,
                                         './/PublicationInfo[@dataFormat="original"]/DocumentID/Country',
                                         './/PublicationInfo[@dataFormat="original"]/DocumentID/Number',
                                         './/PublicationInfo[@dataFormat="original"]/DocumentID/Kind',
                                         'Publi_orig')
            patent_list.append(Publi_orig)

            # 实体6
            Publi_orig_d = entity_content1(patent,
                                           './/PublicationInfo[@dataFormat="original"]/DocumentID/Date',
                                           'Publi_orig_d')
            patent_list.append(Publi_orig_d)

            # 实体7
            Publi_ipph = entity_content3(patent,
                                         './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Country',
                                         './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Number',
                                         './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Kind',
                                         'Publi_ipph')
            patent_list.append(Publi_ipph)

            # 实体8
            Publi_ipph_d = entity_content1(patent,
                                           './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Date',
                                           'Publi_ipph_d')
            patent_list.append(Publi_ipph_d)

            # 实体9
            GrantDate = entity_content1(patent,
                                        './/PrintedWithGrant/DocumentID/Date',
                                        'GrantDate')
            patent_list.append(GrantDate)

            # 实体10
            RevokDate = entity_content1(patent, './/RevocationDate', 'RevokDate')
            patent_list.append(RevokDate)

            # 实体11
            Gazette = {}
            Gazette[':ID'] = generate_random_id(12)
            Gazette['name'] = patent.findtext('.//GazetteReference/GazetteNumber') + \
                              "(" + patent.findtext('.//GazetteReference/Date') + ")"
            Gazette[':LABEL'] = 'Gazette'
            patent_list.append(Gazette)

            # 实体12  一个专利可能有多个专利分类号，
            # 但每个专利分类号都是唯一的，只指向该专利
            ipcrs = []
            for ipcr in patent.findall('.//ClassificationIPCR/Text'):
                patent_dict12 = {}
                patent_dict12[':ID'] = generate_random_id(12)
                ipcrs.append(patent_dict12[':ID'])
                patent_dict12['name'] = ipcr.text
                patent_dict12[':LABEL'] = 'IPCR'
                patent_list.append(patent_dict12)

            # 实体13
            Applicant_n = entity_content1(patent,
                                          './/Applicant/Name',
                                          'Applicant_n')
            patent_list.append(Applicant_n)

            # 实体14
            Applicant_ad = entity_content1(patent,
                                           './/Applicant/AddressBook/Address/Text',
                                           'Applicant_ad')
            patent_list.append(Applicant_ad)

            # 实体15  可能有多个发明人
            inventors = []
            count = 1
            for inventor in patent.findall('.//Inventor/Name'):
                patent_dict15 = {}
                patent_dict15[':ID'] = generate_random_id(12)
                inventors.append(patent_dict15[':ID'])
                patent_dict15['name'] = inventor.text + "(第{0}发明人)".format(count)
                patent_dict15[':LABEL'] = 'Inventor'
                count = count + 1
                patent_list.append(patent_dict15)

            # 实体16 默认每个专利的名称都是唯一的
            Title = entity_content1(patent, './/Title', 'Title')
            patent_list.append(Title)

            # 实体17 默认每个专利的摘要都是唯一的
            Abstract = entity_content1(patent,
                                       './/Abstract/Paragraph',
                                       'Abstract')
            patent_list.append(Abstract)

            # 实体18
            keywords = []
            for keyword in patent.findall('.//Keyword'):
                patent_dict18 = {}
                patent_dict18[':ID'] = generate_random_id(12)
                keywords.append(patent_dict18[':ID'])
                patent_dict18['name'] = keyword.text
                patent_dict18[':LABEL'] = 'Keyword'
                patent_list.append(patent_dict18)

            # 实体19
            Owner_n = entity_content1(patent, './/Owner/Name', 'Owner_n')
            patent_list.append(Owner_n)

            # 实体20
            Owner_ad = entity_content1(patent,
                                       './/Owner/AddressBook/Address/Text',
                                       'Owner_ad')
            patent_list.append(Owner_ad)

            # 实体21
            Agency = entity_content1(patent,
                                     './/Agency/OrganizationName',
                                     'Agency')
            patent_list.append(Agency)

            # 实体22
            Agent = entity_content1(patent,'.//Agent/Name','Agent')
            patent_list.append(Agent)

            # 实体23
            Examiner = entity_content1(patent,'.//Examiner/Name','Examiner')
            patent_list.append(Examiner)

            # 实体24
            TotalPage = entity_content1(patent,
                                        './/StatisticalInfo/TotalPage',
                                        'TotalPage')
            patent_list.append(TotalPage)

            # 去除重复实体
            # patent_unique_list放每个xml文件中不重复的实体三元组
            patent_unique_list = []
            # dup_list放每个xml文件中所有重复的实体三元组
            dup_list = []
            for li in patent_list:
                name = li['name']
                if name not in result:
                    result[name] = li[':ID']
                    patent_unique_list.append(li)
                else:
                    dup_list.append(li)
                    if name not in first_dup:
                        first_dup[name] = result[name]
            patent_list = patent_unique_list

            Appli_orig[':ID'] = exam_entity(Appli_orig[':ID'], dup_list, first_dup)
            Appli_orig_d[':ID'] = exam_entity(Appli_orig_d[':ID'], dup_list, first_dup)
            Appli_ipph[':ID'] = exam_entity(Appli_ipph[':ID'], dup_list, first_dup)
            Appli_ipph_d[':ID'] = exam_entity(Appli_ipph_d[':ID'], dup_list, first_dup)

            Publi_orig[':ID'] = exam_entity(Publi_orig[':ID'], dup_list, first_dup)
            Publi_orig_d[':ID'] = exam_entity(Publi_orig_d[':ID'], dup_list, first_dup)
            Publi_ipph[':ID'] = exam_entity(Publi_ipph[':ID'], dup_list, first_dup)
            Publi_ipph_d[':ID'] = exam_entity(Publi_ipph_d[':ID'], dup_list, first_dup)

            GrantDate[':ID'] = exam_entity(GrantDate[':ID'], dup_list, first_dup)
            RevokDate[':ID'] = exam_entity(RevokDate[':ID'], dup_list, first_dup)
            Gazette[':ID'] = exam_entity(Gazette[':ID'], dup_list, first_dup)

            Applicant_n[':ID'] = exam_entity(Applicant_n[':ID'], dup_list, first_dup)
            Applicant_ad[':ID'] = exam_entity(Applicant_ad[':ID'], dup_list, first_dup)
            for i in range(len(inventors)):
                inventors[i] = exam_entity(inventors[i], dup_list, first_dup)

            for i in range(len(keywords)):
                keywords[i] = exam_entity(keywords[i], dup_list, first_dup)

            Owner_n[':ID'] = exam_entity(Owner_n[':ID'], dup_list, first_dup)
            Owner_ad[':ID'] = exam_entity(Owner_ad[':ID'], dup_list, first_dup)
            Agency[':ID'] = exam_entity(Agency[':ID'], dup_list, first_dup)
            Agent[':ID'] = exam_entity(Agent[':ID'], dup_list, first_dup)
            Examiner[':ID'] = exam_entity(Examiner[':ID'], dup_list, first_dup)

            TotalPage[':ID'] = exam_entity(TotalPage[':ID'], dup_list, first_dup)

            # 以下为获取关系信息，专利标题是中心节点，专门赋值
            id_title = Title[':ID']

            # 关系1
            relation_dict1 = get_relation(id_title,
                                          '专利原始申请号',
                                          Appli_orig[':ID'],
                                          '专利原始申请号')
            relation_list.append(relation_dict1)

            # 关系2
            relation_dict2 = get_relation(id_title,
                                          '专利原始申请日期',
                                          Appli_orig_d[':ID'],
                                          '专利原始申请日期')
            relation_list.append(relation_dict2)

            # 关系3
            relation_dict3 = get_relation(Appli_orig[':ID'],
                                          '原始申请号的申请日期',
                                          Appli_orig_d[':ID'],
                                          '原始申请号的申请日期')
            relation_list.append(relation_dict3)

            # 关系4
            relation_dict4 = get_relation(id_title,
                                          '专利规范申请号',
                                          Appli_ipph[':ID'],
                                          '专利规范申请号')
            relation_list.append(relation_dict4)

            # 关系5
            relation_dict5 = get_relation(id_title,
                                          '专利规范申请日期',
                                          Appli_ipph_d[':ID'],
                                          '专利规范申请日期')
            relation_list.append(relation_dict5)

            # 关系6
            relation_dict6 = get_relation(Appli_ipph[':ID'],
                                          '规范申请号的申请日期',
                                          Appli_ipph_d[':ID'],
                                          '规范申请号的申请日期')
            relation_list.append(relation_dict6)

            # 关系7
            relation_dict7 = get_relation(id_title,
                                          '专利原始公开号',
                                          Publi_orig[':ID'],
                                          '专利原始公开号')
            relation_list.append(relation_dict7)

            # 关系8
            relation_dict8 = get_relation(id_title,
                                          '专利原始公开日期',
                                          Publi_orig_d[':ID'],
                                          '专利原始公开日期')
            relation_list.append(relation_dict8)

            # 关系9
            relation_dict9 = get_relation(Publi_orig[':ID'],
                                          '原始公开号的公开日期',
                                          Publi_orig_d[':ID'],
                                          '原始公开号的公开日期')
            relation_list.append(relation_dict9)

            # 关系10
            relation_dict10 = get_relation(id_title,
                                           '专利规范公开号',
                                           Publi_ipph[':ID'],
                                           '专利规范公开号')
            relation_list.append(relation_dict10)

            # 关系11
            relation_dict11 = get_relation(id_title,
                                           '专利规范公开日期',
                                           Publi_ipph_d[':ID'],
                                           '专利规范公开日期')
            relation_list.append(relation_dict11)

            # 关系12
            relation_dict12 = get_relation(Publi_ipph[':ID'],
                                           '规范公开号的公开日期',
                                           Publi_ipph_d[':ID'],
                                           '规范公开号的公开日期')
            relation_list.append(relation_dict12)

            # 关系13
            relation_dict13 = get_relation(id_title,
                                           '专利授权日期',
                                           GrantDate[':ID'],
                                           '专利授权日期')
            relation_list.append(relation_dict13)

            # 关系14
            relation_dict14 = get_relation(id_title,
                                           '专利被撤销日期',
                                           RevokDate[':ID'],
                                           '专利被撤销日期')
            relation_list.append(relation_dict14)

            # 关系15
            relation_dict15 = get_relation(id_title,
                                           '专利公报引用标志符',
                                           Gazette[':ID'],
                                           '专利公报引用标志符')
            relation_list.append(relation_dict15)

            # 关系16
            for i in range(len(ipcrs)):
                relation_dict16 = {}
                relation_dict16[':START_ID'] = id_title
                relation_dict16['name'] = 'IPCR'
                relation_dict16[':END_ID'] = ipcrs[i]
                relation_dict16[':TYPE'] = 'IPCR'
                relation_list.append(relation_dict16)

            # 关系17
            relation_dict17 = get_relation(id_title,
                                           '申请人',
                                           Applicant_n[':ID'],
                                           '申请人')
            relation_list.append(relation_dict17)

            # 关系18
            relation_dict18 = get_relation(Applicant_n[':ID'],
                                           '申请人的地址',
                                           Applicant_ad[':ID'],
                                           '申请人的地址')
            relation_list.append(relation_dict18)

            # 关系19
            for i in range(len(inventors)):
                relation_dict19 = {}
                relation_dict19[':START_ID'] = id_title
                relation_dict19['name'] = '发明人'
                relation_dict19[':END_ID'] = inventors[i]
                relation_dict19[':TYPE'] = '发明人'
                relation_list.append(relation_dict19)

            # 关系20
            relation_dict20 = get_relation(id_title, '摘要', Abstract[':ID'], '摘要')
            relation_list.append(relation_dict20)

            # 关系21
            for i in range(len(keywords)):
                relation_dict21 = {}
                relation_dict21[':START_ID'] = id_title
                relation_dict21['name'] = '关键词'
                relation_dict21[':END_ID'] = keywords[i]
                relation_dict21[':TYPE'] = '关键词'
                relation_list.append(relation_dict21)

            # 关系22
            relation_dict2 = get_relation(id_title,
                                          '专利权所有人',
                                          Owner_n[':ID'],
                                          '专利权所有人')
            relation_list.append(relation_dict2)

            # 关系23
            relation_dict23 = get_relation(Owner_n[':ID'],
                                           '专利所有人地址',
                                           Owner_ad[':ID'],
                                           '专利所有人地址')
            relation_list.append(relation_dict23)

            # 关系24
            relation_dict24 = get_relation(id_title, '代理机构', Agency[':ID'], '代理机构')
            relation_list.append(relation_dict24)

            # 关系25
            relation_dict25 = get_relation(id_title, '代理人', Agent[':ID'], '代理人')
            relation_list.append(relation_dict25)

            # 关系26
            relation_dict26 = get_relation(id_title, '审查员', Examiner[':ID'], '审查员')
            relation_list.append(relation_dict26)

            # 关系27
            relation_dict27 = get_relation(id_title, '总页数', TotalPage[':ID'], '总页数')
            relation_list.append(relation_dict27)

        # 将数据保存到CSV文件中
        if jishu == 1:
            patent_df = pd.DataFrame(patent_list)
            patent_df.to_csv('patents.csv', mode='a', header=True, index=False, encoding='utf-8')

            relation_df = pd.DataFrame(relation_list)
            relation_df.to_csv('relations.csv', mode='a', header=True, index=False, encoding='utf-8')
        else:
            patent_df = pd.DataFrame(patent_list)
            patent_df.to_csv('patents.csv', mode='a', header=False, index=False, encoding='utf-8')

            relation_df = pd.DataFrame(relation_list)
            relation_df.to_csv('relations.csv', mode='a', header=False, index=False, encoding='utf-8')

        print(jishu)
        jishu += 1

    # end_cpu = time.process_time()  # 记录结束 CPU 时间
    # total_cpu = end_cpu - start_cpu  # 计算 CPU 时间差
    # print("程序运行时间：", total_cpu)
    return result, first_dup, jishu


def publication_patent(result, first_dup, jishu):
    root_folder = r'G:\19个行业专利数据'  # 专利数据存储路径
    xml_files = find_xml_files(root_folder, 'BIBLIOGRAPHIC_INVENTION_PUBLICATION')

    for file in xml_files:
        # 解析XML文件并提取所需信息
        tree = ET.parse(file)
        root = tree.getroot()

        # 记录写入表格的实体、关系
        patent_list = []
        relation_list = []

        # root.findall查找子节点，查找孙节点得加.//
        for patent in root.findall('.//PatentDocument'):
            # 实体1
            Appli_orig = entity_content2(patent,
                                         './/ApplicationInfo[@dataFormat="original"]/DocumentID/Country',
                                         './/ApplicationInfo[@dataFormat="original"]/DocumentID/Number',
                                         'Appli_orig')
            patent_list.append(Appli_orig)

            # 实体2
            Appli_orig_d = entity_content1(patent,
                                           './/ApplicationInfo[@dataFormat="original"]/DocumentID/Date',
                                           'Appli_orig_d')
            patent_list.append(Appli_orig_d)

            # 实体3
            Appli_ipph = entity_content2(patent,
                                         './/ApplicationInfo[@dataFormat="ipph"]/DocumentID/Country',
                                         './/ApplicationInfo[@dataFormat="ipph"]/DocumentID/Number',
                                         'Appli_ipph')
            patent_list.append(Appli_ipph)

            # 实体4
            Appli_ipph_d = entity_content1(patent,
                                           './/ApplicationInfo[@dataFormat="ipph"]/DocumentID/Date',
                                           'Appli_ipph_d')
            patent_list.append(Appli_ipph_d)

            # 实体5
            Publi_orig = entity_content3(patent,
                                         './/PublicationInfo[@dataFormat="original"]/DocumentID/Country',
                                         './/PublicationInfo[@dataFormat="original"]/DocumentID/Number',
                                         './/PublicationInfo[@dataFormat="original"]/DocumentID/Kind',
                                         'Publi_orig')
            patent_list.append(Publi_orig)

            # 实体6
            Publi_orig_d = entity_content1(patent,
                                           './/PublicationInfo[@dataFormat="original"]/DocumentID/Date',
                                           'Publi_orig_d')
            patent_list.append(Publi_orig_d)

            # 实体7
            Publi_ipph = entity_content3(patent,
                                         './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Country',
                                         './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Number',
                                         './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Kind',
                                         'Publi_ipph')
            patent_list.append(Publi_ipph)

            # 实体8
            Publi_ipph_d = entity_content1(patent,
                                           './/PublicationInfo[@dataFormat="ipph"]/DocumentID/Date',
                                           'Publi_ipph_d')
            patent_list.append(Publi_ipph_d)

            # 实体9
            GrantDate = entity_content1(patent,
                                        './/PrintedWithGrant/DocumentID/Date',
                                        'GrantDate')
            patent_list.append(GrantDate)

            # 实体10
            RevokDate = entity_content1(patent, './/RevocationDate', 'RevokDate')
            patent_list.append(RevokDate)

            # 实体11
            Gazette = {}
            Gazette[':ID'] = generate_random_id(12)
            Gazette['name'] = patent.findtext('.//GazetteReference/GazetteNumber') + \
                              "(" + patent.findtext('.//GazetteReference/Date') + ")"
            Gazette[':LABEL'] = 'Gazette'
            patent_list.append(Gazette)

            # 实体12  一个专利可能有多个专利分类号，
            # 但每个专利分类号都是唯一的，只指向该专利
            ipcrs = []
            for ipcr in patent.findall('.//ClassificationIPCR/Text'):
                patent_dict12 = {}
                patent_dict12[':ID'] = generate_random_id(12)
                ipcrs.append(patent_dict12[':ID'])
                patent_dict12['name'] = ipcr.text
                patent_dict12[':LABEL'] = 'IPCR'
                patent_list.append(patent_dict12)

            # 实体13
            Applicant_n = entity_content1(patent,
                                          './/Applicant/Name',
                                          'Applicant_n')
            patent_list.append(Applicant_n)

            # 实体14
            Applicant_ad = entity_content1(patent,
                                           './/Applicant/AddressBook/Address/Text',
                                           'Applicant_ad')
            patent_list.append(Applicant_ad)

            # 实体15  可能有多个发明人
            inventors = []
            count = 1
            for inventor in patent.findall('.//Inventor/Name'):
                patent_dict15 = {}
                patent_dict15[':ID'] = generate_random_id(12)
                inventors.append(patent_dict15[':ID'])
                patent_dict15['name'] = inventor.text + "(第{0}发明人)".format(count)
                patent_dict15[':LABEL'] = 'Inventor'
                count = count + 1
                patent_list.append(patent_dict15)

            # 实体16 默认每个专利的名称都是唯一的
            Title = entity_content1(patent, './/Title', 'Title')
            patent_list.append(Title)

            # 实体17 默认每个专利的摘要都是唯一的
            Abstract = entity_content1(patent,
                                       './/Abstract/Paragraph',
                                       'Abstract')
            patent_list.append(Abstract)

            # 实体18
            keywords = []
            for keyword in patent.findall('.//Keyword'):
                patent_dict18 = {}
                patent_dict18[':ID'] = generate_random_id(12)
                keywords.append(patent_dict18[':ID'])
                patent_dict18['name'] = keyword.text
                patent_dict18[':LABEL'] = 'Keyword'
                patent_list.append(patent_dict18)

            # 实体19
            Agency = entity_content1(patent,
                                     './/Agency/OrganizationName',
                                     'Agency')
            patent_list.append(Agency)

            # 实体20
            Agent = entity_content1(patent,'.//Agent/Name','Agent')
            patent_list.append(Agent)

            # 实体21
            TotalPage = entity_content1(patent,
                                        './/StatisticalInfo/TotalPage',
                                        'TotalPage')
            patent_list.append(TotalPage)

            # 去除重复实体
            # patent_unique_list放每个xml文件中不重复的实体三元组
            patent_unique_list = []
            # dup_list放每个xml文件中所有重复的实体三元组
            dup_list = []
            for li in patent_list:
                name = li['name']
                if name not in result:
                    result[name] = li[':ID']
                    patent_unique_list.append(li)
                else:
                    dup_list.append(li)
                    if name not in first_dup:
                        first_dup[name] = result[name]
            patent_list = patent_unique_list

            Appli_orig[':ID'] = exam_entity(Appli_orig[':ID'], dup_list, first_dup)
            Appli_orig_d[':ID'] = exam_entity(Appli_orig_d[':ID'], dup_list, first_dup)
            Appli_ipph[':ID'] = exam_entity(Appli_ipph[':ID'], dup_list, first_dup)
            Appli_ipph_d[':ID'] = exam_entity(Appli_ipph_d[':ID'], dup_list, first_dup)

            Publi_orig[':ID'] = exam_entity(Publi_orig[':ID'], dup_list, first_dup)
            Publi_orig_d[':ID'] = exam_entity(Publi_orig_d[':ID'], dup_list, first_dup)
            Publi_ipph[':ID'] = exam_entity(Publi_ipph[':ID'], dup_list, first_dup)
            Publi_ipph_d[':ID'] = exam_entity(Publi_ipph_d[':ID'], dup_list, first_dup)

            GrantDate[':ID'] = exam_entity(GrantDate[':ID'], dup_list, first_dup)
            RevokDate[':ID'] = exam_entity(RevokDate[':ID'], dup_list, first_dup)
            Gazette[':ID'] = exam_entity(Gazette[':ID'], dup_list, first_dup)

            Applicant_n[':ID'] = exam_entity(Applicant_n[':ID'], dup_list, first_dup)
            Applicant_ad[':ID'] = exam_entity(Applicant_ad[':ID'], dup_list, first_dup)
            for i in range(len(inventors)):
                inventors[i] = exam_entity(inventors[i], dup_list, first_dup)

            for i in range(len(keywords)):
                keywords[i] = exam_entity(keywords[i], dup_list, first_dup)

            Agency[':ID'] = exam_entity(Agency[':ID'], dup_list, first_dup)
            Agent[':ID'] = exam_entity(Agent[':ID'], dup_list, first_dup)

            TotalPage[':ID'] = exam_entity(TotalPage[':ID'], dup_list, first_dup)

            # 以下为获取关系信息，专利标题是中心节点，专门赋值
            id_title = Title[':ID']

            # 关系1
            relation_dict1 = get_relation(id_title,
                                          '专利原始申请号',
                                          Appli_orig[':ID'],
                                          '专利原始申请号')
            relation_list.append(relation_dict1)

            # 关系2
            relation_dict2 = get_relation(id_title,
                                          '专利原始申请日期',
                                          Appli_orig_d[':ID'],
                                          '专利原始申请日期')
            relation_list.append(relation_dict2)

            # 关系3
            relation_dict3 = get_relation(Appli_orig[':ID'],
                                          '原始申请号的申请日期',
                                          Appli_orig_d[':ID'],
                                          '原始申请号的申请日期')
            relation_list.append(relation_dict3)

            # 关系4
            relation_dict4 = get_relation(id_title,
                                          '专利规范申请号',
                                          Appli_ipph[':ID'],
                                          '专利规范申请号')
            relation_list.append(relation_dict4)

            # 关系5
            relation_dict5 = get_relation(id_title,
                                          '专利规范申请日期',
                                          Appli_ipph_d[':ID'],
                                          '专利规范申请日期')
            relation_list.append(relation_dict5)

            # 关系6
            relation_dict6 = get_relation(Appli_ipph[':ID'],
                                          '规范申请号的申请日期',
                                          Appli_ipph_d[':ID'],
                                          '规范申请号的申请日期')
            relation_list.append(relation_dict6)

            # 关系7
            relation_dict7 = get_relation(id_title,
                                          '专利原始公开号',
                                          Publi_orig[':ID'],
                                          '专利原始公开号')
            relation_list.append(relation_dict7)

            # 关系8
            relation_dict8 = get_relation(id_title,
                                          '专利原始公开日期',
                                          Publi_orig_d[':ID'],
                                          '专利原始公开日期')
            relation_list.append(relation_dict8)

            # 关系9
            relation_dict9 = get_relation(Publi_orig[':ID'],
                                          '原始公开号的公开日期',
                                          Publi_orig_d[':ID'],
                                          '原始公开号的公开日期')
            relation_list.append(relation_dict9)

            # 关系10
            relation_dict10 = get_relation(id_title,
                                           '专利规范公开号',
                                           Publi_ipph[':ID'],
                                           '专利规范公开号')
            relation_list.append(relation_dict10)

            # 关系11
            relation_dict11 = get_relation(id_title,
                                           '专利规范公开日期',
                                           Publi_ipph_d[':ID'],
                                           '专利规范公开日期')
            relation_list.append(relation_dict11)

            # 关系12
            relation_dict12 = get_relation(Publi_ipph[':ID'],
                                           '规范公开号的公开日期',
                                           Publi_ipph_d[':ID'],
                                           '规范公开号的公开日期')
            relation_list.append(relation_dict12)

            # 关系13
            relation_dict13 = get_relation(id_title,
                                           '专利授权日期',
                                           GrantDate[':ID'],
                                           '专利授权日期')
            relation_list.append(relation_dict13)

            # 关系14
            relation_dict14 = get_relation(id_title,
                                           '专利被撤销日期',
                                           RevokDate[':ID'],
                                           '专利被撤销日期')
            relation_list.append(relation_dict14)

            # 关系15
            relation_dict15 = get_relation(id_title,
                                           '专利公报引用标志符',
                                           Gazette[':ID'],
                                           '专利公报引用标志符')
            relation_list.append(relation_dict15)

            # 关系16
            for i in range(len(ipcrs)):
                relation_dict16 = {}
                relation_dict16[':START_ID'] = id_title
                relation_dict16['name'] = 'IPCR'
                relation_dict16[':END_ID'] = ipcrs[i]
                relation_dict16[':TYPE'] = 'IPCR'
                relation_list.append(relation_dict16)

            # 关系17
            relation_dict17 = get_relation(id_title,
                                           '申请人',
                                           Applicant_n[':ID'],
                                           '申请人')
            relation_list.append(relation_dict17)

            # 关系18
            relation_dict18 = get_relation(Applicant_n[':ID'],
                                           '申请人的地址',
                                           Applicant_ad[':ID'],
                                           '申请人的地址')
            relation_list.append(relation_dict18)

            # 关系19
            for i in range(len(inventors)):
                relation_dict19 = {}
                relation_dict19[':START_ID'] = id_title
                relation_dict19['name'] = '发明人'
                relation_dict19[':END_ID'] = inventors[i]
                relation_dict19[':TYPE'] = '发明人'
                relation_list.append(relation_dict19)

            # 关系20
            relation_dict20 = get_relation(id_title, '摘要', Abstract[':ID'], '摘要')
            relation_list.append(relation_dict20)

            # 关系21
            for i in range(len(keywords)):
                relation_dict21 = {}
                relation_dict21[':START_ID'] = id_title
                relation_dict21['name'] = '关键词'
                relation_dict21[':END_ID'] = keywords[i]
                relation_dict21[':TYPE'] = '关键词'
                relation_list.append(relation_dict21)

            # 关系22
            relation_dict24 = get_relation(id_title, '代理机构', Agency[':ID'], '代理机构')
            relation_list.append(relation_dict24)

            # 关系23
            relation_dict25 = get_relation(id_title, '代理人', Agent[':ID'], '代理人')
            relation_list.append(relation_dict25)

            # 关系24
            relation_dict27 = get_relation(id_title, '总页数', TotalPage[':ID'], '总页数')
            relation_list.append(relation_dict27)

        # 将数据保存到CSV文件中
        if jishu == 1:
            patent_df = pd.DataFrame(patent_list)
            patent_df.to_csv('patents.csv', mode='a', header=True, index=False, encoding='utf-8')

            relation_df = pd.DataFrame(relation_list)
            relation_df.to_csv('relations.csv', mode='a', header=True, index=False, encoding='utf-8')
        else:
            patent_df = pd.DataFrame(patent_list)
            patent_df.to_csv('patents.csv', mode='a', header=False, index=False, encoding='utf-8')

            relation_df = pd.DataFrame(relation_list)
            relation_df.to_csv('relations.csv', mode='a', header=False, index=False, encoding='utf-8')

        print(jishu)
        jishu += 1


# 两个类别总共1170760个专利
# 两个类别运行一次要6301.415363550186s
def main():
    start_time = time.time()  # 记录开始时间
    # 记录重复实体
    # result放不重复的实体的name：ID
    # first_dup放被重复的第一个实体的name：ID
    result = {}
    first_dup = {}
    # 记录读取了多少个xml文件，读取个数为jishu-1
    jishu = 1
    result, first_dup, jishu = grant_patent(result, first_dup, jishu)
    print('==================== 授权专利处理完毕 ====================')
    publication_patent(result, first_dup, jishu)

    end_time = time.time()  # 记录结束时间
    total_time = end_time - start_time  # 计算总时间差
    print("程序运行时间：", total_time)


if __name__ == '__main__':
    main()