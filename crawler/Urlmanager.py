
import time
from datetime import date
# 为了获取对应类别
category_dict = {'kultur': 13845, 'sport': 13839, 'studiu': 2215199,'themen': 2215339,
                 'weltspiegel': '2215200', 'wirtschaft': 13836, 'wissen': 13838,
                 'zeitun': 2215229, 'meinun': 13837, 'mediacenter': 2215194, 'medien': 13843,
                 'berlin': 13840, 'mediac': 2215194, 'mobil': 2215248, 'politil': 13841}

for key, value in category_dict.items():
    sql = """
    update rs_article_info set `category_id` = %s where article_url like 'http://www.tagesspiegel.de/%s%%';
    """ % (value, key)
    print(sql)
