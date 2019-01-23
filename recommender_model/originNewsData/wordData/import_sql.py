# with open('../HistoryRecord.txt','r') as f:
#     for eachline in f:
#         args = eachline.strip().split(":")
#         sql = 'insert into rs_member_history(`member_id`,`article_id`,`timestamp`,`impression`) values(%s,%s,%s,\'%s\');'%(
#             args[0],args[1],args[2],args[-1]
#         )
#         print(sql)

import json

with open('../ArticleRecord.txt','r') as f:
    for eachline in f:
        args = eachline.strip().split(":::")
        contents = json.loads(args[1])

        article_id = contents.get('id') if contents.get('id') is not None else ''
        article_url = contents.get('url') if contents.get('url') is not None else ''
        img_url = contents.get('img') if contents.get('img') is not None else ''
        title = contents.get('title') if contents.get('title') is not None else ''
        title = title.replace('\n','').replace('\'','\\\'')
        text = contents.get('text') if contents.get('text') is not None else ''
        text = text.replace('\n','').replace('\'','\\\'')
        create_date =contents.get('created_at') if contents.get('created_at') is not None else ''
        update_date = contents.get('updated_at') if contents.get('updated_at') is not None else ''
        time_stamp = contents.get('timestamp') if contents.get('timestamp') is not None else ''
        domain_id = contents.get('domainid') if contents.get('domainid') is not None else ''
        category_id = contents.get('categoryid') if contents.get('categoryid') is not None else ''
        sql = 'insert into rs_article_info values( \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\');'%(
            article_id,article_url, img_url,title,text,create_date,update_date,time_stamp,domain_id,category_id
        )
        print(sql)