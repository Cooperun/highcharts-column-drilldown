import pandas as pd
import numpy
import json,copy,traceback,logging,signal,base64

class getFileContent():
    csv_content = None
    csv_filed = None
    def __init__(self,filename):
        self.csv_content = pd.read_excel(filename)
        self.csv_filed = list(self.csv_content.columns)

class drillDownCreate():
    basic_base64 = b'eyJjaGFydCI6IHsidHlwZSI6ICJjb2x1bW4ifSwgInRpdGxlIjogeyJ0ZXh0IjogbnVsbH0sICJz\ndWJ0aXRsZSI6IHsidGV4dCI6IG51bGx9LCAieEF4aXMiOiB7InR5cGUiOiAiY2F0ZWdvcnkifSwg\nInlBeGlzIjogeyJ0aXRsZSI6IHsidGV4dCI6IG51bGx9fSwgImxlZ2VuZCI6IHsiZW5hYmxlZCI6\nIGZhbHNlfSwgInBsb3RPcHRpb25zIjogeyJzZXJpZXMiOiB7ImJvcmRlcldpZHRoIjogMCwgImRh\ndGFMYWJlbHMiOiB7ImVuYWJsZWQiOiB0cnVlLCAiZm9ybWF0IjogIntwb2ludC55fSJ9fX0sICJ0\nb29sdGlwIjogeyJoZWFkZXJGb3JtYXQiOiAiPHNwYW4gc3R5bGU9XCJmb250LXNpemU6MTFweFwi\nPntzZXJpZXMubmFtZX08L3NwYW4+PGJyPiIsICJwb2ludEZvcm1hdCI6ICI8c3BhbiBzdHlsZT1c\nImNvbG9yOntwb2ludC5jb2xvcn1cIj57cG9pbnQubmFtZX08L3NwYW4+OiA8Yj57cG9pbnQueX08\nL2I+PGJyLz4ifSwgInNlcmllcyI6IFt7Im5hbWUiOiAidGVzdCIsICJjb2xvckJ5UG9pbnQiOiB0\ncnVlLCAiZGF0YSI6IFtdfV0sICJkcmlsbGRvd24iOiB7InNlcmllcyI6IFtdfX0=\n'
    data_model_base64 = b'eyJuYW1lIjogbnVsbCwgInkiOiBudWxsLCAiZHJpbGxkb3duIjogbnVsbH0=\n'
    sec_model_base64 = b'eyJuYW1lIjogbnVsbCwgImlkIjogbnVsbCwgImRhdGEiOiBbXX0=\n'
    basic = None
    data_model = None
    sec_model = None
    dem:int = 0
    field:list = []
    csv_file = None
    way_compute = None
    compute_field = None
    def __init__(self,target_file):
        try:
            self.basic = json.loads(base64.decodebytes(self.basic_base64))
            self.data_model = json.loads(base64.decodebytes(self.data_model_base64))
            self.sec_model = json.loads(base64.decodebytes(self.sec_model_base64))
            self.csv_file = getFileContent(target_file)
        except Exception as e:
            logging.error(e)
            self.before_exit()
    
    def before_exit(self):
        input("Press Enter to exit...")
        exit()

    def set_title(self,title:str):
        self.basic['title']['text'] = title

    def add_data(self,level:int,data,id):
        if level == 1:
            self.basic['series'][0]['data'].append(data)
        else:
            # Todo find correct data then append
            for i in range(len(self.basic['drilldown']['series'])):
                if self.basic['drilldown']['series'][i]['id'] == id:
                    self.basic['drilldown']['series'][i]['data'].append(data)

        if data['drilldown'] is not None:
            for i in range(len(self.basic['drilldown']['series'])):
                if self.basic['drilldown']['series'][i]['id'] == data['name']:
                    return
            
            sec_data = copy.deepcopy(self.sec_model)
            sec_data['name'] = data['name']
            sec_data['id'] = data['drilldown']
            self.basic['drilldown']['series'].append(sec_data)

    def set_field(self):
        field = list(self.csv_file.csv_content.columns)
        c = 1
        for i in field:
            print(c,end=":")
            print(i)
            c += 1
        print("please select your target field in order")
        inp = input()
        inp = inp.strip()
        try:
            self.field = [field[eval(i)-1] for i in inp.split(" ")]
        except IndexError as e:
            logging.error(e)
            self.before_exit()
        except Exception as e:
            logging.error(e)
            self.before_exit()

        print("target field you select :",self.field)
        print("please select the way you expect to compute: 1.count 2.sum")
        try:
            self.way_compute = eval(input())
            if self.way_compute <=0 or self.way_compute > 2:
                logging.error("please select the way in list")
                self.before_exit()
            
        except Exception as e:
            logging.error(e)
            self.before_exit()
        
        c = 1
        for i in field:
            print(c,end=":")
            print(i)
            c += 1
        print("please select your field to compute")
        try:
            self.compute_field = field[eval(input())-1]
        except IndexError as e:
            logging.error(e)
            self.before_exit()
        except Exception as e:
            logging.error(e)
            self.before_exit()
        
        print("compute field:",self.compute_field)
        if self.way_compute == 2:
            if not isinstance(self.csv_file.csv_content[self.compute_field].sum(),numpy.int64) \
                and not isinstance(self.csv_file.csv_content[self.compute_field].sum(),numpy.float64):
                logging.error("please select the field that could be computed")
                self.before_exit()
        self.dem = len(self.field)
        self.basic['series'][0]['name'] = self.compute_field
        print("generating……")

    def create_data(self,level,dem,df,now_field):
        if dem == len(self.field):
            return 
        field_content = set(df[self.field[dem]])
        for i in field_content:
            data_ = copy.deepcopy(self.data_model)
            data_['name'] = i
            if self.way_compute == 1:
                data_['y'] = int(df[df[self.field[dem]]==i].count()[self.compute_field])
            else:
                data_['y'] = int(df[df[self.field[dem]]==i].sum()[self.compute_field])
            
            next_field = i
            if dem != self.dem-1:
                if level != 1:
                    next_field = "_".join([now_field,i])
                data_['drilldown'] = next_field

            self.add_data(level,data_,now_field)
            self.create_data(level+1,dem+1,df[df[self.field[dem]]==i],next_field)
            


target_file = input("please input the target file path: ")
test = drillDownCreate(target_file)
test.set_title(input("please input the title: "))
test.set_field()

import re
regex = r'(?<!: )"(\S*?)"'

test.create_data(1,0,test.csv_file.csv_content,"")

begin = "Highcharts.chart(\"container\","
end = ");"
js_str = begin+re.sub(regex,"\\1",json.dumps(test.basic,ensure_ascii=False,indent=1))+end

html_head_base64 = b'PCFET0NUWVBFIEhUTUw+CjxodG1sPgogICAgPGhlYWQ+CiAgICAgICAgPG1ldGEgY2hhcnNldD0i\ndXRmLTgiPjxsaW5rIHJlbD0iaWNvbiIgaHJlZj0iaHR0cHM6Ly9qc2Nkbi5jb20uY24vaGlnaGNo\nYXJ0cy9pbWFnZXMvZmF2aWNvbi5pY28iPgogICAgICAgIDxtZXRhIG5hbWU9InZpZXdwb3J0IiBj\nb250ZW50PSJ3aWR0aD1kZXZpY2Utd2lkdGgsIGluaXRpYWwtc2NhbGU9MSI+CiAgICAgICAgPHRp\ndGxlPuaLm+eUn+iuoeWIkuihqDwvdGl0bGU+CiAgICAgICAgPHN0eWxlPgogICAgICAgICAgICAv\nKiBjc3Mg5Luj56CBICAqLwogICAgICAgIDwvc3R5bGU+CiAgICAgICAgPHNjcmlwdCBzcmM9Imh0\ndHBzOi8vY29kZS5oaWdoY2hhcnRzLmNvbS5jbi9oaWdoY2hhcnRzL2hpZ2hjaGFydHMuanMiPjwv\nc2NyaXB0PgogICAgICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NvZGUuaGlnaGNoYXJ0cy5jb20u\nY24vaGlnaGNoYXJ0cy9tb2R1bGVzL2V4cG9ydGluZy5qcyI+PC9zY3JpcHQ+CiAgICAgICAgPHNj\ncmlwdCBzcmM9Imh0dHBzOi8vY29kZS5oaWdoY2hhcnRzLmNvbS5jbi9oaWdoY2hhcnRzL21vZHVs\nZXMvZHJpbGxkb3duLmpzIj48L3NjcmlwdD4KICAgICAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9p\nbWcuaGNoYXJ0cy5jbi9oaWdoY2hhcnRzLXBsdWdpbnMvaGlnaGNoYXJ0cy16aF9DTi5qcyI+PC9z\nY3JpcHQ+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICA8ZGl2IGlkPSJjb250YWluZXIi\nIHN0eWxlPSJtaW4td2lkdGg6IDMxMHB4OyBoZWlnaHQ6IDQwMHB4OyBtYXJnaW46IDAgYXV0byI+\nPC9kaXY+CiAgICAgICAgPHNjcmlwdD4=\n'
html_tail_base64 = b'PC9zY3JpcHQ+CjwvYm9keT4KPC9odG1sPg==\n'
try:
    html_head = base64.decodebytes(html_head_base64).decode("utf-8")
    html_tail = base64.decodebytes(html_tail_base64).decode("utf-8")
    with open("drilldown.html","w",encoding="utf-8") as f:
        f.write("\n".join([html_head,js_str,html_tail]))
    print("finished!")
    print("the file's name is drilldown.html")
except Exception as e:
    logging.error(e)

input("Press Enter to exit...")
