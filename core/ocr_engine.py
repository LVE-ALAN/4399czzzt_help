import os
import re
import sys
import tkinter as tk
from tkinter import filedialog
import pyautogui
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# 全局OCR实例（延迟加载）
_ocr = None

def get_ocr():
    global _ocr
    if _ocr is None:
        print("⏳ 正在初始化 PaddleOCR...")
        _ocr = PaddleOCR(lang='ch')
        print("✅ PaddleOCR 加载完毕！")
    return _ocr

def load_data_from_excel(excel_path="data/武将属性.xlsx"):
    """加载Excel数据（原样）"""
    try:
        if not os.path.exists(excel_path):
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="请选择游戏数据文件（Excel）",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            root.destroy()
            if not file_path:
                return None, "未选择文件，程序退出"
            excel_path = file_path

        xl = pd.ExcelFile(excel_path)
        sheet_names = xl.sheet_names
        print(f"📋 检测到以下 Sheet：{sheet_names}")

        all_data = {}

        # ----- 1. 加载武将 -----
        hero_sheet = None
        for name in sheet_names:
            if '武将' in name or 'Sheet1' in name:
                hero_sheet = name
                break
        if hero_sheet:
            try:
                df = xl.parse(hero_sheet, header=0)
                df.columns = df.columns.astype(str).str.strip()
                df = df.loc[:, df.columns.notna() & (df.columns != 'nan')]
                hero_col = belong_col = pos_col = skill_col = main_col = None
                for col in df.columns:
                    if '武将' in col:
                        hero_col = col
                    elif '所属' in col:
                        belong_col = col
                    elif '英雄帖' in col:
                        pos_col = col
                    elif col == '技能':
                        skill_col = col
                    elif col == '主将技':
                        main_col = col
                if hero_col is None and len(df.columns) >= 5:
                    hero_col, belong_col, pos_col, skill_col, main_col = df.columns[:5]

                for idx, row in df.iterrows():
                    name = str(row.get(hero_col, '')).strip()
                    if not name or name == 'nan' or name == '武将':
                        continue
                    info = {}
                    if belong_col and pd.notna(row.get(belong_col)):
                        info['所属'] = str(row[belong_col]).strip()
                    if pos_col and pd.notna(row.get(pos_col)):
                        info['英雄帖品质'] = str(row[pos_col]).strip()
                    if skill_col and pd.notna(row.get(skill_col)):
                        info['技能'] = str(row[skill_col]).strip()
                    if main_col and pd.notna(row.get(main_col)):
                        info['主将技'] = str(row[main_col]).strip()
                    if name in all_data:
                        all_data[name].update(info)
                    else:
                        all_data[name] = info
                print(f"✅ 加载武将数据：{len(df)} 行（来自 Sheet: {hero_sheet}）")
            except Exception as e:
                print(f"⚠️ 加载武将数据失败：{e}")

        # ----- 2. 加载皮肤 -----
        skin_sheet = None
        for name in sheet_names:
            if '皮肤' in name or 'Sheet2' in name:
                skin_sheet = name
                break
        if skin_sheet:
            try:
                df = xl.parse(skin_sheet, header=0)
                df.columns = df.columns.astype(str).str.strip()
                df = df.loc[:, df.columns.notna() & (df.columns != 'nan')]
                name_col = belong_col = hp_col = atk_col = def_col = None
                for col in df.columns:
                    if '皮肤' in col or '名称' in col:
                        name_col = col
                    elif '所属' in col:
                        belong_col = col
                    elif '生命' in col:
                        hp_col = col
                    elif '攻击' in col:
                        atk_col = col
                    elif '防御' in col:
                        def_col = col
                if name_col is None and len(df.columns) >= 5:
                    name_col, belong_col, hp_col, atk_col, def_col = df.columns[:5]

                for idx, row in df.iterrows():
                    name = str(row.get(name_col, '')).strip()
                    if not name or name == 'nan' or name == '皮肤名称':
                        continue
                    key = f"【皮肤】{name}"
                    if key not in all_data:
                        all_data[key] = {}
                    if belong_col and pd.notna(row.get(belong_col)):
                        all_data[key]['所属'] = str(row[belong_col]).strip()
                    if hp_col and pd.notna(row.get(hp_col)):
                        all_data[key]['生命'] = str(row[hp_col]).strip()
                    if atk_col and pd.notna(row.get(atk_col)):
                        all_data[key]['攻击'] = str(row[atk_col]).strip()
                    if def_col and pd.notna(row.get(def_col)):
                        all_data[key]['防御'] = str(row[def_col]).strip()
                print(f"✅ 加载皮肤数据：{len(df)} 行（来自 Sheet: {skin_sheet}）")
            except Exception as e:
                print(f"⚠️ 加载皮肤数据失败：{e}")

        # ----- 3. 加载兵种 -----
        troop_sheet = None
        for name in sheet_names:
            if '兵种' in name or '部队' in name or 'Sheet3' in name:
                troop_sheet = name
                break
        if troop_sheet:
            try:
                df = xl.parse(troop_sheet, header=0)
                df.columns = df.columns.astype(str).str.strip()
                df = df.loc[:, df.columns.notna() & (df.columns != 'nan')]
                troop_col = belong_col = rate_col = None
                for col in df.columns:
                    if '兵种' in col or '部队' in col:
                        troop_col = col
                    elif '所属' in col:
                        belong_col = col
                    elif '倍率' in col or '加成' in col:
                        rate_col = col
                if troop_col is None and len(df.columns) >= 3:
                    troop_col, belong_col, rate_col = df.columns[:3]

                for idx, row in df.iterrows():
                    name = str(row.get(troop_col, '')).strip()
                    if not name or name == 'nan' or name == '兵种':
                        continue
                    belong = str(row.get(belong_col, '')).strip() if belong_col else ''
                    rate = str(row.get(rate_col, '')).strip() if rate_col else ''
                    key = f"【兵种】{name}"
                    if key not in all_data:
                        all_data[key] = {}
                    if belong:
                        all_data[key]['所属'] = belong
                    if rate:
                        all_data[key]['倍率'] = rate
                print(f"✅ 加载兵种数据：{len(df)} 行（来自 Sheet: {troop_sheet}）")
            except Exception as e:
                print(f"⚠️ 加载兵种数据失败：{e}")

        # ----- 4. 加载物品 -----
        item_sheet = None
        for name in sheet_names:
            if '物品' in name or '宝石' in name or '道具' in name or 'Sheet4' in name:
                item_sheet = name
                break
        if item_sheet:
            try:
                df = xl.parse(item_sheet, header=0)
                df.columns = df.columns.astype(str).str.strip()
                df = df.loc[:, df.columns.notna() & (df.columns != 'nan')]

                if len(df.columns) >= 3:
                    name_col = df.columns[0]
                    price_col = df.columns[1]
                    attr_col = df.columns[2]
                elif len(df.columns) == 2:
                    name_col = df.columns[0]
                    price_col = None
                    attr_col = df.columns[1]
                else:
                    name_col = df.columns[0]
                    price_col = None
                    attr_col = None

                loaded_count = 0
                for idx, row in df.iterrows():
                    name = str(row.get(name_col, '')).strip()
                    if not name or name == 'nan' or name == '物品' or name == '名称':
                        continue

                    key = f"【物品】{name}"
                    if key not in all_data:
                        all_data[key] = {}

                    if price_col is not None:
                        price = str(row.get(price_col, '')).strip()
                        if price and price != 'nan' and price != '/' and price != '':
                            all_data[key]['价格'] = price

                    if attr_col is not None:
                        raw_attr = row.get(attr_col)
                        if pd.notna(raw_attr):
                            if isinstance(raw_attr, (int, float)):
                                attr_display = f"{int(round(raw_attr * 100, 0))}%"
                            else:
                                attr_display = str(raw_attr).strip()
                            if attr_display and attr_display != 'nan' and attr_display != '/':
                                all_data[key]['属性'] = attr_display

                    loaded_count += 1
                print(f"✅ 加载物品数据：{loaded_count} 行（来自 Sheet: {item_sheet}）")
            except Exception as e:
                print(f"⚠️ 加载物品数据失败：{e}")

        return all_data, f"✅ 总共加载 {len(all_data)} 条数据"
    except Exception as e:
        return None, f"❌ 读取Excel失败：{str(e)}"


# ---------- 以下为 OCR 匹配核心 ----------
CHAR_OCR_ERRORS = {
    '夏': {'戛'}, '侯': {'候'}, '天': {'夭'}, '王': {'壬'},
    '汉': {'汊'}, '史': {'虫'}, '日': {'曰'}, '山': {'杉'},
    '子': {'孑'}, '干': {'千'}, '奘': {'装'}, '逖': {'邀'},
    '翦': {'剪'}, '郃': {'邰'}, '惇': {'悖'}, '士': {'土', '十'},
}

def gen_fuzzy_variants(name):
    variants = {name}
    for i, ch in enumerate(name):
        for wrong in CHAR_OCR_ERRORS.get(ch, ()):
            variants.add(name[:i] + wrong + name[i + 1:])
    return variants

def build_name_index(data):
    idx = []
    for key in data.keys():
        pure = (key.replace("【兵种】", "").replace("【皮肤】", "")
                .replace("【物品】", "").replace("【道具】", ""))
        idx.append((pure, key))
    idx.sort(key=lambda x: len(x[0]), reverse=True)
    return idx

def capture_and_search(region, data, img_np=None, verbose=False):
    """截取指定区域 -> OCR识别 -> 数据库查询 -> 返回结果字符串"""
    try:
        if img_np is None:
            img = pyautogui.screenshot(region=region)
            img_np = np.array(img)

        ocr = get_ocr()
        result = ocr.ocr(img_np, cls=False)
        all_texts = []
        if result and result[0]:
            for line in result[0]:
                text, confidence = line[1]
                if confidence > 0.5:
                    all_texts.append(text.strip())

        if not all_texts:
            return "❌ 未识别到文字"

        full_text = "".join(all_texts)
        clean_text = re.sub(r'[\s\n\r]+', '', full_text)
        clean_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9：:，,。、？?！!%]', '', clean_text)
        if verbose:
            print(f"【清洗后识别】: {clean_text}")

        alias = {
            "神戛侯悖": "神夏侯惇",
            "夏侯悖": "夏侯惇",
            "戛侯悖": "夏侯惇",
            "戛侯惇": "夏侯惇",
            "夏候惇": "夏侯惇",
            "美洲虎战土": "美洲虎战士",
            "美洲虎战十": "美洲虎战士",
            "增长夭王": "增长天王",
            "增长夭壬": "增长天王",
            "阿育壬": "阿育王",
            "齐夭大圣": "齐天大圣",
            "千将": "干将",
            "持国夭王": "持国天王",
            "武则夭": "武则天",
            "多闻夭王": "多闻天王",
            "神汊钟离": "神汉钟离",
            "广目夭壬": "广目天王",
            "汊尼拔": "汉尼拔",
            "张邰": "张郃",
            "卣熊步兵": "白熊步兵",
            "汊军步兵": "汉军步兵",
            "蜀汊步兵": "蜀汉步兵",
            "自袍军弓兵": "白袍军弓兵",
            "汊军弓兵": "汉军弓兵",
            "汊军骑兵": "汉军骑兵",
            "汊军火枪": "汉军火枪",
            "蜀汊弓兵": "蜀汉弓兵",
            "蜀汊火枪": "蜀汉火枪",
            "蜀汊骑兵": "蜀汉骑兵",
            "自袍军步兵": "白袍军步兵",
            "自袍军火枪": "白袍军火枪",
            "自袍军骑兵": "白袍军骑兵",
            "路易诗斯": "路易十四",
            "亚力杉达": "亚历山大",
            "亚力杉大": "亚历山大",
            "菲力二世": "腓力二世",
            "菲列特一世": "腓列特一世",
            "膝望塔": "瞭望塔",
            "爱树": "爱心树",
            "每曰僵尸波数": "每日僵尸波数",
            "夭坛最大红钻": "天坛最大红钻",
            "戛侯渊": "夏侯渊",
            "欧治孑": "欧冶子",
            "腓特烈世": "腓列特一世",
            "太虫慈": "太史慈",
            "神韩湘孑": "神韩湘子",
            "哈罗德": "哈德罗",
            "斯大令": "斯大林",
            "草人步兵": "稻草人步兵",
            "鲁翼诗斯": "路易十四",
            "粱红玉": "梁红玉",
            "祖邀": "祖逖",
            "髅弓兵": "骷髅弓兵",
            "神夏候": "神夏侯惇",
            "再闵": "冉闵",
            "欧治子": "欧冶子",
            "甸奴王": "匈奴王",
            "朴金": "普今",
            "特烈一世": "腓列特一世",
            "王剪": "王翦",
            "神夏侯": "神夏侯惇",
            "戚灵顿": "威灵顿",
            "神戚灵顿": "神威灵顿",
            "唐玄装": "唐玄奘",
        }
        for wrong, right in alias.items():
            clean_text = clean_text.replace(wrong, right)

        chinese_only = re.sub(r'[^\u4e00-\u9fa5]', '', clean_text)
        if verbose:
            print(f"【中文提取】: {chinese_only}")

        name_index = build_name_index(data)

        found_key = None
        for pure, key in name_index:
            if pure in clean_text or pure in chinese_only:
                found_key = key
                break
            for variant in gen_fuzzy_variants(pure):
                if variant in clean_text:
                    found_key = key
                    break
            if found_key:
                break
        if found_key:
            info = data[found_key]
            lines = [f"📌 {found_key}"]
            for k, v in info.items():
                if v and v != 'nan':
                    lines.append(f"   ├─ {k}：{v}")
            return "\n".join(lines)

        for key, info in data.items():
            for attr, value in info.items():
                v = str(value).strip()
                if v and v != 'nan' and len(v) >= 3 and (v in clean_text or v in chinese_only):
                    lines = [f"🔍 匹配到 {key}"]
                    for k, vv in info.items():
                        if vv and vv != 'nan':
                            lines.append(f"   ├─ {k}：{vv}")
                    return "\n".join(lines)

        if "宝石" in clean_text and "十级" in clean_text:
            for key in data.keys():
                if "十级普通宝石" in key:
                    info = data[key]
                    lines = [f"📌 {key}"]
                    for k, v in info.items():
                        if v and v != 'nan':
                            lines.append(f"   ├─ {k}：{v}")
                    return "\n".join(lines)
            return "💎 十级普通宝石属性加成：请查看游戏内数据"
        if "摇号" in clean_text and "数字" in clean_text:
            return "🎲 充值摇号不会出现的数字：3（请以活动规则为准）"

        if "主将技" in clean_text:
            match = re.search(r'([\u4e00-\u9fa5·]+)的主将技', clean_text)
            if match:
                possible = match.group(1)
                for pure, key in name_index:
                    if pure == possible:
                        info = data[key]
                        lines = [f"📌 {key}"]
                        for k, v in info.items():
                            if v and v != 'nan':
                                lines.append(f"   ├─ {k}：{v}")
                        return "\n".join(lines)
                return f"❓ 检测到武将【{possible}】，但数据库中无数据"

        return f"❌ 无法匹配，识别文字：{clean_text[:40]}..."
    except Exception as e:
        return f"⚠️ 识别出错：{str(e)}"