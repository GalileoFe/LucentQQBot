import re
from langdetect import detect as detect_lang


def replace_url_email_with_punctuation(text:str = ""):
    """
        this function is used to replace the symbols in URL and Email.
        readable symbols such as '@' to 'at', '.' to dot
        it mean to be used for VITS to pronounce symbols correctly in URL and Email.

        Args:
            string text.

        Returns:
            a modified text with all symbols replaced with readable words.
    """
    cleantext = text

    url_pattern = r'(?i)(?:(?:https?|ftp):)?\/\/(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:\/[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    urlmatch = re.findall(url_pattern, text)
    emailmatch = re.findall(email_pattern,text)

    if urlmatch:
        for url in urlmatch:
            unclean = re.sub('/', ', ', re.sub(r'\:\/\/', ', ', url))
            urlclean = re.sub(r'\.', ' dot ', unclean)
            cleantext = re.sub(url, urlclean, cleantext)

    if emailmatch:
        for email in emailmatch:
            emailcleantext = re.sub('@', ' at ', re.sub(r'\.', ' dot ', email))
            cleantext = re.sub(email, emailcleantext, cleantext)
    return cleantext


def split_sentences_with_punctuation(text):
    """
        Args:
            sentence string text.

        Returns:
            a split sentences list with punctuations included.
    """
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


def detect(text, *args):
    """
        Args:
            text(str):a piece of text.
        Returns:
            one single language Code.

            e.g:'zh','en'
    """
    if args:
        languages, *_ = args
    else:
        languages = ['zh','en','ja','fr']

    lang = detect_lang(re.sub(r'[\W_]+', '', text)).upper()
    prefix = 'ZH' if 'ZH' in lang.upper() else lang
    if str(prefix).lower() in languages:
        return prefix
    else:
        return "EN"


def detect_language_with_prefix_code(text:str = "", *args):
    """
        this function is used to split text input to sentences
        and return with language code assigned.

        e.g:
            return [EN]this is a example text.[EN][ZH]这是示例.ZH]

        Args:
            text(str):
                sentence string text,
            args(list[str]):
                language list, will set [EN] as default if detected language is not in list provided

        Returns:
            str:recombined sentences with language code prefixed with each separate sentence.

    """
    # split text by end punctuations
    sentences = split_sentences_with_punctuation(text)
    final_combined_text = ""
    # assign language code to each split sentence
    for t in sentences:
        lang = detect(t, *args).upper()
        prefix = "["+lang+"]"
        final_combined_text += prefix + t + prefix
    print(final_combined_text)
    return final_combined_text


def detect_language_with_prefix_code_multi_sentence(text:str = "", *args):
    """
        this function is used to split text input to sentences
        and return with a list of sentence of language code assigned.


        e.g:
            return [EN]this is a example text.[EN][ZH]这是示例.ZH]

        Args:
            text(str):
                sentence string text,
            args(list[str]):
                language list, will set [EN] as default if detected language is not in list provided

        Returns:
            str:recombined sentences with language code prefixed with each separate sentence.

    """
    # split text by end punctuations
    sentences = split_sentences_with_punctuation(text)
    final_combined_text = [""]
    # assign language code to each split sentence
    for t in sentences:
        lang = detect(t, *args).upper()
        prefix = "["+lang+"]"
        if len(final_combined_text[len(final_combined_text)-1]) + len(prefix) + len(t) + len(prefix) > 200:
            final_combined_text.append(prefix + t + prefix)
        else:
            final_combined_text[len(final_combined_text)-1] += prefix + t + prefix
    print(str(len(final_combined_text)) + str(final_combined_text))
    return final_combined_text

# 这句话这么多字还能被识别成[ko], 准确率真的多有点低
# print(detect_lang("很适合出去玩呢."))