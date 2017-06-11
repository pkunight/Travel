import requests
from lxml import etree
import re
import time
import json

youji_url_pattern = re.compile(r"(/youji/[0-9]*)\"")
youji_count_pattern = re.compile(r".*/hot_heat/([0-9]+)\.htm")
remove_pattern = re.compile(r"<script[\S\s]+?</script>|<style[\S\s]+?</style>|<!--[\S\s]+?-->")


def get_youji_url_list(youji_list_page_url):
    raw_html_text = requests.get(url=youji_list_page_url).text
    youji_url_raw_list = youji_url_pattern.findall(raw_html_text, re.M)

    youji_url_dict = {}

    for raw_url in youji_url_raw_list:
        if raw_url not in youji_url_dict:
            youji_url_dict[raw_url] = ''

    return youji_url_dict.keys()


def get_youji_content(youji_content_page_url):
    print(youji_content_page_url)


_url = "http://travel.qunar.com/travelbook/list/22-beijing-299914/hot_heat/1.htm"
root = etree.HTML(requests.get(url=_url).text.encode('utf-8'))
page_href_list = root.xpath('//div[@class="b_paging"]/a/@href')

max_count = 1
for href in page_href_list:
    youji_page_num = int(youji_count_pattern.findall(href)[0])
    if youji_page_num > max_count:
        max_count = youji_page_num


_url_get_head_pattern = re.compile(r"(.*)/[0-9]+\.htm")
_url_head = _url_get_head_pattern.findall(_url)[0]

file_head = "qunar/qunar"
file_num = 1000000000
img_num = 1000000000

for i in range(0, max_count):
    time.sleep(10)
    youji_url_list = get_youji_url_list(_url_head + "/" + str(i+1) + ".htm")
    print("page", i+1)
    for raw_url in youji_url_list:
        time.sleep(5)
        real_url = "http://travel.qunar.com" + raw_url
        root = etree.HTML(requests.get(real_url).text.encode('utf-8'))

        youji_dict = {"channel":"去哪儿"}

        # youji_whole_text = "<url='" + real_url + "' />\n"
        youji_dict["url"] = real_url

        #文章标题和发表时间
        #如果这里报错说明ip被禁了
        youji_title = root.xpath('//span[@id="booktitle"]/text()')[0]
        # youji_whole_text += "<title>" + youji_title + "</title>\n"
        youji_dict["title"] = youji_title
        print("title", youji_title)

        youji_createtime = root.xpath('//li[@class="date"]/span/text()')[0]
        youji_dict["create_time"] = youji_createtime.replace("/","-")

        # -----------------------------------------------------------------------------------------------------------
        youji_forward_list_root = root.xpath('//ul[@class="foreword_list"]')[0]
        #出发日期
        youji_forward_when = youji_forward_list_root.xpath('li[@class="f_item when"]/p/span[@class="data"]/text()')
        if len(youji_forward_when) > 0:
            youji_forward_when = youji_forward_when[0]
            youji_dict["travel_time"] = youji_forward_when.replace("/", "-")
            # youji_whole_text += "<time>" + youji_forward_when + "</time>\n"
        else:
            youji_dict["travel_time"] = ""

            #旅游天数
        youji_forward_howlong = youji_forward_list_root.xpath('li[@class="f_item howlong"]/p/span[@class="data"]/text()')
        if len(youji_forward_howlong) > 0:
            youji_forward_howlong = youji_forward_howlong[0]
            youji_dict["days"] = youji_forward_howlong
            # youji_whole_text += "<days>" + youji_forward_howlong + "</days>\n"
        else:
            youji_dict["days"] = ""

            # 人均费用
        youji_forward_howmuch = youji_forward_list_root.xpath('li[@class="f_item howmuch"]/p/span[@class="data"]/text()')
        if len(youji_forward_howmuch) > 0:
            youji_forward_howmuch = youji_forward_howmuch[0]
            youji_dict["much"] = youji_forward_howmuch
            # youji_whole_text += "<much>" + youji_forward_howmuch + "元</much>\n"
        else:
            youji_dict["much"] = ""

            # 人数
        youji_forward_who = youji_forward_list_root.xpath('li[@class="f_item who"]/p/span[@class="data"]/text()')
        if len(youji_forward_who) > 0:
            youji_forward_who = youji_forward_who[0]
            youji_dict["who"] = youji_forward_who
            # youji_whole_text += "<who>" + youji_forward_who + "</who>\n"
        else:
            youji_dict["who"] = ""

            # 玩法
        youji_forward_how = youji_forward_list_root.xpath('li[@class="f_item how"]/p/span[@class="data"]/text()')
        if len(youji_forward_how) > 0:
            youji_forward_how = youji_forward_how[0]
            youji_dict["how"] = youji_forward_how
            # youji_whole_text += "<how>" + youji_forward_how + "</how>\n"
        else:
            youji_dict["how"] = ""
        # -----------------------------------------------------------------------------------------------------------

        youji_content_root = root.xpath('//div[@class="b_panel_schedule"]')[0]
        youji_ch_root_list = youji_content_root.xpath('div[@class="e_main"]/div')

        youji_whole_text = ""
        for ch_root in youji_ch_root_list:
            # 章节标题
            ch_head = ch_root.xpath('h4[@class="period_hd"]/dl/dt/div[@class="text"]/text()')[0]
            youji_whole_text += "<h1>" + ch_head + "</h1>\n"
            # print(ch_head)

            para_root_list = ch_root.xpath('div[@class="period_ct"]/div')
            for para_root in para_root_list:
                # 段落标题
                para_content_top = para_root.xpath('div[@class="top"]/h5/div[@class="b_poi_title_box"]/text()')
                if len(para_content_top) == 0:
                    para_content_top = para_root.xpath('div[@class="top"]/h5/div[@class="b_poi_title_box"]/a/text()')
                if len(para_content_top) > 0:
                    para_content_top = para_content_top[0]
                    youji_whole_text += "<h2>" + para_content_top + "</h2>\n"
                # print(para_content_top)

                para_content_bottom_imglist_root_list = para_root.xpath('div[@class="bottom"]/div[@class="e_img_schedule"]/div[@class="imglst"]')

                for para_content_bottom_imglist_root in para_content_bottom_imglist_root_list:
                    img_and_p_root_list = para_content_bottom_imglist_root.xpath('div/p|dl/dt/img|dl/dd/div/p')

                    for img_and_p_root in img_and_p_root_list:
                        if img_and_p_root.tag == "p" and img_and_p_root.text:
                            youji_whole_text += "<p>" + img_and_p_root.text + "</p>\n"
                            # print(img_and_p_root.text)
                        elif img_and_p_root.tag == "img":
                            youji_whole_text += "<img title=\"【" + img_and_p_root.attrib["title"] + "】\" src=\"" + img_and_p_root.attrib["data-original"] + "\" />\n"
                            # print(img_and_p_root.attrib["title"], img_and_p_root.attrib["src"])



                # para_content_bottom_p_root_list = para_root.xpath('div[@class="bottom"]/div[@class="e_img_schedule"]/div[@class="imglst"]/div[@class="text js_memo_node"]/p')
                # for p_root in para_content_bottom_p_root_list:
                #     p = p_root.xpath('text()')
                #     if len(p) > 0:
                #         youji_whole_text += p[0] + "\n"

        # print(youji_whole_text)
        youji_dict["content"] = youji_whole_text

        with open(file_head + "-" + str(file_num) + ".txt", "w") as file:
            file.write(json.dumps(youji_dict, ensure_ascii=False))

        file_num += 1
        # print("\n")
