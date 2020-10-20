import speech_recognition as sr
import wikipedia
import os


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def set_microphone(mic_name):
    mic_list = sr.Microphone.list_microphone_names()
    my_mic_index = mic_list.index(mic_name)
    print(my_mic_index)
    return sr.Microphone(device_index=my_mic_index)


def get_wikipedia_summary(t, s):
    summary = wikipedia.summary(topic, auto_suggest=True, sentences=s)
    print("Here are some information about {}\n".format(topic))
    print(summary)


def get_categories(topic):
    r = requests.get('https://en.wikipedia.org/wiki/{}'.format(topic))
    if r.status_code == 200:
        soup: bs4.BeautifulSoup = BeautifulSoup(r.content, "html.parser")

    categories = list()
    for category in soup.find_all(None, {"class": "toclevel-1"}, recursive=True):
        end_index = category.text.find('\n')
        main_category = category.text[:end_index]
        categories.append(main_category)

    return categories


if __name__ == "__main__":

    MIC_NAME = "DELL PRO STEREO HEADSET UC150: USB Audio (hw:2,0)"
    ATTEMPTS = 2

    recognizer = sr.Recognizer()
    microphone = set_microphone(MIC_NAME)

    os.system('clear')
    print("What do you want to know about ?")
    r = recognize_speech_from_mic(recognizer, microphone)

    for _ in range(ATTEMPTS):
        if r["transcription"]:
            break
        if not r["success"]:
            break
        ATTEMPTS -= 1
        print("Didn't get that. Repeat please.  (remaining attempts: {})".format(ATTEMPTS))
        r = recognize_speech_from_mic(recognizer, microphone)
    ATTEMPTS = 2

    topic = r["transcription"]
    print("\nYou chose: ", topic, "\n")

    get_wikipedia_summary(topic, 3)

    url = wikipedia.WikipediaPage(topic).url
    print("\nsource: {}\n".format(url))

    print("Do you want to see related categories ?  (Yes, No)")
    r = recognize_speech_from_mic(recognizer, microphone)

    for _ in range(ATTEMPTS):
        if r["transcription"]:
            break
        if not r["success"]:
            break
        ATTEMPTS -= 1
        print("This is Yes-No question (remaining attempts: {})".format(ATTEMPTS))
        r = recognize_speech_from_mic(recognizer, microphone)
    ATTEMPTS = 2

    if r["transcription"] == "yes":
        print()
        for category in get_categories(topic):
            print(category)
        print()
    elif r["transcription"] == "no":
        pass

