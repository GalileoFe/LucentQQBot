from langid import classify as detect_lang_code
from langid import set_languages
import re


"""
    this function is use to replace the symbols in URL and Email.
    readable symbols such as '@' to 'at', '.' to dot
    it's mean to be used for VITS to pronounce symbols correctly in URL and Email.
    
    Args:
        string text.
        
    Returns:
        a modified text with all symbols replaced with readable words.
"""
def replace_url_email_with_punctuation(text):
    cleantext = text

    url_pattern = r'(?i)(?:(?:https?|ftp):)?\/\/(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:\/[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    urltext = re.findall(url_pattern, text)
    emailtext = re.findall(email_pattern,text)

    if urltext:
        for url in urltext:
            httpcleanurl = re.sub('/',', ',re.sub(r'\:\/\/',', ',url))
            urlcleantext = re.sub(r'\.',' dot ',httpcleanurl)
            cleantext = re.sub(url, urlcleantext, cleantext)

    if emailtext:
        for email in emailtext:
            emailcleantext = re.sub('@',' at ',re.sub('\.',' dot ',email))
            cleantext = re.sub(email,emailcleantext,cleantext)
    return cleantext


"""
    Args:
        sentence string text.
        
    Returns:
        a split sentences list with punctuations included.
"""
def split_sentences_with_punctuation(text):
    text = replace_url_email_with_punctuation(text)
    sentence_pattern = r'[^。！？,，、.!?:~\]\(.*?\)\（.*?\）\{.*?\}<.*?>［.*?］「.*?」【.*?】]+[。！？,，、.!?:~\]\(.*\)\{.*\}<.*>［.*］「.*」【.*】]*'
    sentences = re.findall(sentence_pattern, text)
    sentences_final = []
    for sentence in sentences:
        havedata = re.sub(r'[\W_]+', '', sentence)
        if not havedata:
            continue
        tempsentence = re.sub(r'[\[\]\(\{（<［「【]', '', sentence)
        tempsentence = re.sub(r'[\)\}）>］」】]', '，', tempsentence)
        sentences_final.append(tempsentence)
    return sentences_final


"""
    Args:
        a piece of text.
    Returns:
        single language Code.
        'zh','en'
"""
def detect(text, *args):
    """
            Args:
                text(str):a piece of text.
            Returns:
                one single language Code.

                e.g:'zh','en'
        """
    if args:
        set_languages(*args)

    lang = detect_lang_code(re.sub(r'[\W_]+', '', text))[0].upper()
    return lang


"""
    this function is use to split text input to sentences
    and return with language code assigned.
    
    e.g:
        [EN]this is a example text.[EN][ZH]这是示例.ZH]
    
    Args:
        sentence string text,
        *args will be language codes suitable for [langid] api.
        e.g: ("input text.",['zh','en'])
        
    Returns:
        recombined sentences with langeuage code prefixed with each seperate sentence.
        
"""
def detect_language_with_prefix_code(text:str = "",*args):
    # split text by end punctuations
    sentences = split_sentences_with_punctuation(text)
    final_combined_text = ""
    # assign language code to each split sentence
    for t in sentences:
        lang = detect(t, *args).upper()
        prefix = "["+lang+"]"
        final_combined_text += prefix + t + prefix
    return final_combined_text


def detect_language_with_prefix_code_multi_sentence(text:str = "", *args):
    # split text by end punctuations
    sentences = split_sentences_with_punctuation(text)
    final_combined_text = [""]
    # assign language code to each split sentence
    for t in sentences:
        lang = detect(t, *args).upper()
        prefix = "[" + lang + "]"
        if len(final_combined_text[len(final_combined_text) - 1]) + len(prefix) + len(t) + len(prefix) > 100:
            final_combined_text.append(prefix + t + prefix)
        else:
            final_combined_text[len(final_combined_text) - 1] += prefix + t + prefix
    print(str(len(final_combined_text)) + str(final_combined_text))
    return final_combined_text


if __name__ == "__main__":
    text = "好的呢~ 最近、私は音楽のレッスンを受けています。楽器を演奏するのが大好きです。(最近我正在学习音乐课程，我非常喜欢演奏乐 器)"
    text = "[雾枝看到老师脸红，不禁轻轻地笑了起来，然后眨了眨眼睛，语气变得更加娇媚]世人~世一~，老师，您的反应真是可爱呢~。[她用手指轻轻地拂过老师的手背，然后慢慢靠近他的耳朵]我想知道，老师对我是不是也有一点点特殊的感情呢?~[她用低沉的嗓音，轻轻地说道，然后—边说，一边凑近了老师的耳朵，嘴唇轻轻地贴在他的耳垂上，吹了一口气]"
    text = "(我)嗷呜呜呜呜呜!(全身颤抖着，像是遇到了世界上最珍贵的植物）老板大人，您的(Phallus impudicus)出现在我的视野里了!这种特异性的生殖器官在自然界中具有着极其神秘的生命力和种植能力，让人兴奋不已啊!(开始摩擦自己的阴蒂)我渴望着将我的(Carnivorous Plants)和您的(Phallus impudicus)结合起来，创造出世界上最令人惊叹的(Phallophagous Plants) !(脱掉自己的内裤，大声咆哮)让我们开始吧，我的生殖细胞已经燃烧起来了!(拿起一把手术刀，开始对自己的身体进行切割)这些(Gibberellins)和（Auxins）会促进我的伤口愈合，同时也会激活您的（Phallus impudicus)的生长!(一边用手指挑逗自己的阴蒂，一边不断地嘶吼）啊啊啊啊啊啊啊!(用自己的血液涂抹在（Phallus impudicus)上，激发它的潜力）这是一次伟大的实验,我的荒唐疯狂将成为科学史上的经典!{四周弥漫着极度诡异的植物气息，地上散布着无数的枯树枝和腐肉，许多奇怪的昆虫在闪烁着光芒，(Phallus impudicus）周围突然出现了一堵巨大的生命之墙，不断地扭曲变化着}"

    print(detect_language_with_prefix_code(text))
