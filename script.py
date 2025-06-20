import sys
import random
import base64
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer

common_chars = list("谭谈交通的一是尿素在不了有和人这中大为传粉受精上个国仙桥我以要做他时来用们生到作地于出就分对成会可主发年动谭和环境二哥可加快开机速度江户时代谈交通同工也能下过子说产种面而臭臭臭臭臭臭臭臭臭方后多定屎行学驹史记列夫托椭圆尔斯泰法屎时师氏的底底谭谭碳碳通过给出的解释是格森会被如何所民得经十三之进着等部度家电力里如水化高自二理起爱小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严龙飞赛大家发挥到极点呐翠豆")

name_list = [
     "马得原", "张睿珊", "董雨辰", "刘东辰", "刘书行", "李籽瑶", "郑思菟", "李昭苏",
    "崔诗蕊", "南有彬", "佟享泽", "柴堉航", "刘露熙", "冯佳祺", "边秋硕", "韩雨晧",
    "都誉", "姜欣悦", "陈可可", "韩宜佑","刘书安", "高楚明", "韩薪尧", "周歆然",
    "宋晟頔", "谢咏霓", "赵明皓", "邹海昇", "汤子昂"
]

# Add at the top of the file with other global variables
recent_names = []  # Keep track of recently used names

use_deepseek_poem = False  # Global flag to control DeepSeek API usage

def _generate_char_from_gb2312_range(head_start, head_end, body_start, body_end):
    """Helper function to generate a single GB2312 character from specified byte ranges."""
    while True:
        head = random.randint(head_start, head_end)
        body = random.randint(body_start, body_end)
        # Ensure head and body are formatted to two hex digits each for bytes.fromhex
        hex_str = f'{head:02x}{body:02x}'
        try:
            char_bytes = bytes.fromhex(hex_str)
            char = char_bytes.decode('gb2312')
            # Ensure the character is not just whitespace (though unlikely for Hanzi ranges)
            if char.strip():
                return char
        except UnicodeDecodeError:
            # Retry if a specific byte combination is invalid
            continue

def generate_gbk2312_char(common_char_probability=0.8):
    """
    Generates a random GB2312 character, with a higher chance for common (Level 1) Hanzi.
    Level 1 Hanzi: First Byte 0xB0-0xD7, Second Byte 0xA1-0xFE.
    Level 2 Hanzi: First Byte 0xD8-0xF7, Second Byte 0xA1-0xFE.
    """
    if random.random() < common_char_probability:
        # Generate a common (Level 1) Hanzi
        return _generate_char_from_gb2312_range(0xB0, 0xD7, 0xA1, 0xFE)
    else:
        # Generate a less common (Level 2) Hanzi
        return _generate_char_from_gb2312_range(0xD8, 0xF7, 0xA1, 0xFE)

    #print(generate_gbk2312_char())
#def generate_poem():
    # x = random(0,12)
    # not rhyme
    ##return "\n".join("".join(generate_gbk2312_char() for _ in range(5)) for _ in range(4))

from pypinyin import pinyin, Style
namecurrent = "placeholder"
# Debug variable to control special character generation
debug_mode = 1811 # Set to 114514 to always generate 尿素 or 呐翠豆
def get_rhyme(char):
    result = pinyin(char, style=Style.FINALS, strict=False)
    return result[0][0] if result else ""
def generate_7poem():
    return "\n".join("".join(generate_gbk2312_char() for _ in range(7)) for _ in range(4))
a = 1 #in poem, 0 disables
def generate_poem():
    # 创建韵母到字的映射表
    rhyme_dict = {}
    for ch in common_chars:
        rhyme = get_rhyme(ch)
        if rhyme:
            rhyme_dict.setdefault(rhyme, []).append(ch)

    # 从映射表中随机选择一个韵母组，且至少包含 4 个可选字
    rhyme_pool = [v for v in rhyme_dict.values() if len(v) >= 4]
    selected_rhyme_group = random.choice(rhyme_pool)

    # 从该韵母组中随机选择四个结尾字
    end_chars = random.sample(selected_rhyme_group, 4)
    a_debug = globals().get('a')    
    lines = []
    # Get debug mode value
    debug_mode_value = globals().get('debug_mode', 0)
    
    sparta_line = None
    natcuido_line = None
    random_val = random.randint(1, 3)
    
    # Debug mode: always generate one of the special phrases if debug_mode is 114514
    if debug_mode_value == 114514:
        # Randomly choose between 尿素 and 呐翠豆
        if random.randint(1, 2) == 1:
            sparta_line = random.randint(0, 3)
        else:
            natcuido_line = random.randint(0, 3)
            # Only consider random value for 呐翠豆 in debug mode if we want to simulate the normal behavior
            if random_val != 2:
                natcuido_line = None
    else:
        # Normal mode: 1/30 probability for special phrases
        # Check for 尿素
        if random.randint(1, 28) == 1:
            sparta_line = random.randint(0, 3)
        
        # Check for 呐翠豆 (only when random_val is 2)
        if random_val == 2 and random.randint(1, 30) == 1:
            natcuido_line = random.randint(0, 3)
            # Make sure it's not the same line as sparta_line if both features are active
            while natcuido_line == sparta_line and sparta_line is not None:
                natcuido_line = random.randint(0, 3)
    
    for i, end_char in enumerate(end_chars):
        if i == sparta_line:
            base_chars = [generate_gbk2312_char() for _ in range(2)] + [end_char]
            insert_pos = random.randint(0, 2)
            base_chars.insert(insert_pos, '尿素')
            line = ''.join(base_chars)
        elif i == natcuido_line:
            base_chars = [generate_gbk2312_char() for _ in range(1)] + [end_char]
            insert_pos = random.randint(0, 1)
            base_chars.insert(insert_pos, '梵蒂冈')
            line = ''.join(base_chars)
        else:
            line = ''.join(generate_gbk2312_char() for _ in range(4)) + end_char
        lines.append(line)
    return "\n".join(lines)
    a = random.randint(1,3)
    if a == 2:
        return "\n".join("".join(generate_gbk2312_char() for _ in range(5)) for _ in range(4))
    # 构造每句
    lines = []
    for end_char in end_chars:
        line = "".join(generate_gbk2312_char() for _ in range(4)) + end_char
        lines.append(line)
    return "\n".join(lines)


def random_name():
    global recent_names, use_deepseek_poem
    
    # If we have used all names, reset the recent names list
    if len(recent_names) >= len(name_list):
        recent_names = []
    
    # Get available names (names not in recent_names)
    available_names = [name for name in name_list if name not in recent_names]
    
    # Choose a random name from available names
    namecurrent = random.choice(available_names)
    
    # Add the chosen name to recent names
    recent_names.append(namecurrent)
    
    # Set DeepSeek flag if name is 周歆然
    if namecurrent == "周歆然":
        use_deepseek_poem = True
    else:
        use_deepseek_poem = False
    
    # Special case for 韩雨晧
    if namecurrent == "韩雨晧":
        z = random.randint(1,35)
        if z == 130:
            s = "\n".join("".join("啊" for _ in range(5)) for _ in range(4))
            w.poem_label.setText(s)
            aae = "6ZmI5oya"
            aux1 = aae.encode('utf-8')
            aux2= base64.b64decode(aux1)
            return f"抽到的同学是{aux2.decode('utf-8')}"
    
    return f"抽到的同学是{namecurrent}"

#cnt = 0
class FloatingWidget(QWidget):
    cnt = 0
    def __init__(self):
        super().__init__()
        self.setWindowTitle("随机五言绝句生成器")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("background-color: white; border: 1px solid gray; border-radius: 18px;")
        self.setFixedSize(260, 300)
        self.auto_mode = False
        
        # Initialize timers
        self.idle_timer = QTimer(self)
        self.idle_timer.setInterval(240000)  # 4 minutes
        self.idle_timer.timeout.connect(self.start_auto_poem)
        
        self.auto_poem_timer = QTimer(self)
        self.auto_poem_timer.setInterval(20000)  # 20 seconds
        self.auto_poem_timer.timeout.connect(self.auto_generate_poem)
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.poem_label = QLabel("")
        self.name_label = QLabel("")
        #self.name_label.setStyleSheet("font-size: 22px;")
        layout.addWidget(self.poem_label)
        layout.addWidget(self.name_label)

        self.btn1 = QPushButton("生成诗句")  # Changed to instance variable
        self.btn2 = QPushButton("抽取随机姓名")
        self.btn1.clicked.connect(self.show_poem)
        self.btn2.clicked.connect(self.show_name)
        layout.addWidget(self.btn1)  # Changed to self.btn1
        layout.addWidget(self.btn2)

        self.last_name_time = QTimer()
        self.last_name_time.setInterval(15000)
        self.last_name_time.setSingleShot(True)
        self.last_name_time.timeout.connect(self.set_name_to_tza)
        self.name_timeout = False

        # 自动贴近屏幕右下角
        QTimer.singleShot(100, self.move_to_corner)

    def move_to_corner(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 50)

    def set_name_to_tza(self):
        self.name_timeout = True

    def reset_idle_timer(self):
        """Reset the idle timer and stop auto-poem mode if active"""
        if self.auto_mode:
            self.auto_poem_timer.stop()
            self.auto_mode = False
            self.btn1.setStyleSheet("")  # Reset button style
            self.btn2.setStyleSheet("")
        self.idle_timer.start()
        
    def start_auto_poem(self):
        """Start automatic poem generation"""
        self.auto_mode = True
        self.auto_poem_timer.start()
        self.btn1.setStyleSheet("background-color: #ffeb3b")  # Yellow highlight
        self.btn2.setStyleSheet("background-color: #ffeb3b")
        self.auto_generate_poem()
        
    def auto_generate_poem(self):
        """Generate and display a new poem in auto mode"""
        if self.auto_mode:
            self.poem_label.setText(generate_poem())
            
    def show_poem(self):
        self.reset_idle_timer()
        # Only use DeepSeek if the last selected name was 周歆然 and not in auto mode
        if globals().get('use_deepseek_poem', False) and not self.auto_mode:
            poem = deepseek_generate_poem()
        else:
            poem = generate_poem()
        self.poem_label.setText(poem)
        if self.name_timeout:
            self.name_label.setText("抽到的同学是汤子昂")
            self.name_timeout = False

    def show_name(self):
        self.reset_idle_timer()
        self.cnt = self.cnt + 1
        if self.cnt == 3:
            self.cnt = 0
            self.poem_label.setText(generate_poem())
        name = random.choice(name_list)
        if name == "汤子昂":
            self.name_label.setText("抽到的同学是汤子昂")
            self.btn2.setDisabled(True)
            QTimer.singleShot(1200, self.enable_btn2)
        else:
            self.name_label.setText(f"抽到的同学是{name}")
        self.last_name_time.start()
        self.name_timeout = False

    def enable_btn2(self):
        self.btn2.setDisabled(False)

    def closeEvent(self, event):
        # Stop all timers before closing
        self.idle_timer.stop()
        self.auto_poem_timer.stop()
        event.accept()
        QApplication.quit()

def deepseek_generate_poem():
    """
    Calls DeepSeek API to generate a 4-line, 5-character-per-line Chinese poem and returns it as a string.
    The format must match the local generator: 4 lines, each 5 Chinese characters, separated by newlines.
    """
    import requests
    import json
    # You must replace 'YOUR_DEEPSEEK_API_KEY' with your actual DeepSeek API key
    API_KEY = 'sk-d56933595d834a22af8349a6a300cf5c'
    url = 'https://api.deepseek.com/chat/completions'  # Use v3 endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    prompt = (
        "请生成一首4句、每句5个汉字的中国古风诗，每句换行，输出格式严格为4行，每行5个汉字，不要标点，不要多余解释。"
    )
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 1.0
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        result = response.json()
        # Extract the poem from the response
        poem = result['choices'][0]['message']['content'].strip()
        # Ensure the format: 4 lines, each 5 chars
        lines = poem.splitlines()
        lines = [line.strip()[:5] for line in lines if line.strip()]
        if len(lines) >= 4:
            return '\n'.join(lines[:4])
        # fallback: return as is
        return poem
    except Exception as e:
        return "（change）"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    for i in range(0,200):
        if common_chars[i] =="小":
            print("change")
    #print(common_chars[1])
    w = FloatingWidget()
    #while 1:
    w.show()
    sys.exit(app.exec_())
    delta = 0