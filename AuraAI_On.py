import os
import sys
import datetime
import pyttsx3
import platform
import subprocess
import socket
import speech_recognition as sr
from rich.console import Console
import webbrowser
import speedtest
import requests
import openai  # Import OpenAI's GPT API client
import google.cloud.texttospeech as tts
import google.cloud.speech as stt

sys.stderr = open(os.devnull, 'w')

color = Console()

conversation_history = ""
model = "gpt-3.5-turbo"  # Use GPT-3.5 or any other model from OpenAI

openai.api_key = "your-openai-api-key"  # Add your OpenAI API key

time_q = {
    "what's the time",
    "what time is it",
    "tell me the time",
    "can you tell me the time",
    "please tell the time",
    "what is the time",
    "what is the time going on",
    "what's the time going on"
}

shutdown_q = {
    "shutdown the pc"
}

restart_q = {
    "restart the pc"
}

internet = [
    "check the internet",
    "internet status"
]

check_connection = [
    "what is the speed of the internet",
    "what is the speed of the internet",
    "check the speed of internet",
    "check the internet speed",
]

websearch_q = [
    "search for",
    "look up",
    "search"
]

def say(text):
    """Text-to-Speech function using Google Cloud."""
    client = tts.TextToSpeechClient()
    synthesis_input = tts.SynthesisInput(text=text)
    voice = tts.VoiceSelectionParams(
        language_code="en-US", ssml_gender=tts.SsmlVoiceGender.NEUTRAL
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    audio_path = "output.mp3"
    with open(audio_path, "wb") as out:
        out.write(response.audio_content)
    
    os.system(f"start {audio_path}")  # Play the generated audio file

def check_internet():
    """Check if the machine is connected to the internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except (socket.timeout, socket.gaierror):
        return False

def takeCommand():
    """Take command using Google Speech-to-Text API."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening with Google...")
        try:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=30, phrase_time_limit=30)
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            say("Sorry, I couldn't understand that. Could you please repeat?")
            return None  
        except sr.RequestError:
            say("Sorry, there was an issue with the speech recognition service.")
            return None 
        except Exception as e:
            say(f"Sorry, I encountered an error: {e}")
            return None  

def current_day_and_date():
    today = datetime.datetime.now()
    return today.strftime("Today is %A, %d %B %Y")

def yesterday_and_tomorrow():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    return (
        yesterday.strftime("Yesterday was %A, %d %B %Y"),
        tomorrow.strftime("Tomorrow will be %A, %d %B %Y"),
    )

def last_occurrence_of_day(day_name):
    today = datetime.datetime.now()
    day_name = day_name.capitalize()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if day_name not in days_of_week:
        return f"'{day_name}' is not a valid day."
    day_index = days_of_week.index(day_name)
    days_back = (today.weekday() - day_index) % 7
    last_day = today - datetime.timedelta(days=days_back)
    return last_day.strftime(f"The last {day_name} was on %A, %d %B %Y.")

def next_occurrence_of_day(day_name):
    today = datetime.datetime.now()
    day_name = day_name.capitalize()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if day_name not in days_of_week:
        return f"'{day_name}' is not a valid day."
    day_index = days_of_week.index(day_name)
    days_forward = (day_index - today.weekday()) % 7
    next_day = today + datetime.timedelta(days=days_forward)
    return next_day.strftime(f"The next {day_name} is on %A, %d %B %Y.")

def day_of_week_for_date(date_str):
    try:
        specific_date = datetime.datetime.strptime(date_str, "%d %B %Y")
        return specific_date.strftime(f"The day on {date_str} is %A.")
    except ValueError:
        return "Invalid date format. Please use 'dd Month yyyy', e.g., '12 December 2024'."


def web_search(query):
    """Perform a web search on Google."""
    try:
        search_query = query.split("search for", 1)[1].strip()  # Extract the search term
        say(f"Searching for {search_query}")
        search_url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(search_url)  # Open the search results in the default browser
        say(f"Showing results for {search_query}")
    except Exception as e:
        say(f"Sorry, I couldn't perform the search. Error: {e}")

def get_weather(city):
    """Fetch weather information for the city."""
    api_key = "bbe7ade5f540103d3c38a09f28beee65"  # Replace with your API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(base_url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("cod") == 200:
                main = data["main"]
                weather = data["weather"][0]
                temp = main["temp"]
                humidity = main["humidity"]
                description = weather["description"]
                weather_info = f"Temperature: {temp}°C, Humidity: {humidity}%, Description: {description.capitalize()}"
                return weather_info
            else:
                return f"Sorry, I couldn't find weather information for {city}. Please check the city name."
        else:
            return f"Error: Unable to fetch data (Status code: {response.status_code})"

    except Exception as e:
        return f"Error: {e}"

def aura(query):
    """AI query handler with memory using GPT API."""
    global conversation_history
    try:
        print("Aura AI is thinking...")
        conversation_history += f"User: {query}\n"
        
        # Call OpenAI GPT API for response
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": query}]
        )
        
        ai_response = response['choices'][0]['message']['content']
        if not ai_response:
            raise ValueError("No response from AI model.")
        
        conversation_history += f"Aura: {ai_response}\n"
        color.print(f"[cyan]{ai_response}[/cyan]")
        say(ai_response)
        return ai_response
    except Exception as e:
        say(f"Error: The AI model did not respond. Details: {e}")
        return f"Error: {e}"

def check_connection_speed():
    st = speedtest.Speedtest()
    
    st.get_best_server()
    
    download_speed = st.download() / 1_000_000  # Convert from bits/sec to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert from bits/sec to Mbps
    ping = st.results.ping
    
    return download_speed, upload_speed, ping

if __name__ == '__main__':
    print('Welcome to Aura AI')
    say("Aura AI With The Most Aura")

    if check_internet():
        print("Internet is available, using Google Speech-to-Text.")
    else:
        print("No internet detected.")

    while True:
        query = takeCommand()

        if query is None:
            continue  

        if query == "shutdown aura":
            say("Aura is shutting down.")
            break

        if "weather of" in query:
            city = query.replace("weather of", "").strip()
            weather_info = get_weather(city)
            color.print(f"[cyan]{weather_info}[/cyan]")
            say(weather_info)
        
        elif any(phrase in query for phrase in time_q):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            say(f"The time is {current_time}")

        elif any(phrase in query for phrase in shutdown_q):
            say("Shutting down your PC in 10 seconds")
            os.system("shutdown /s /t 10")
        
        elif any(phrase in query for phrase in restart_q):
            say("Restarting your PC in 10 seconds")
            os.system("shutdown /r /t 10")
        
        elif any(phrase in query for phrase in internet):
            if check_internet():
                say("You are connected to the internet")
            else:
                say("You are not connected to the internet")

        if "what is today's date" in query:
            result = current_day_and_date()
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is yesterday's date" in query or "what was yesterday" in query:
            result, _ = yesterday_and_tomorrow()
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is tomorrow's date" in query or "what is tomorrow" in query:
            _, result = yesterday_and_tomorrow()
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is the date of last" in query:
            day_name = query.split("last")[-1].strip()
            result = last_occurrence_of_day(day_name)
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is the date of next" in query:
            day_name = query.split("next")[-1].strip()
            result = next_occurrence_of_day(day_name)
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what day is on" in query:
            date_str = query.split("what day is")[-1].strip()
            result = day_of_week_for_date(date_str)
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif any(phrase in query for phrase in check_connection):
            download_speed, upload_speed, ping = check_connection_speed()
            color.print(f"[cyan]Download speed: {download_speed:.2f} Mbps[/cyan]")
            color.print(f"[cyan]Upload speed: {upload_speed:.2f} Mbps[/cyan]")
            color.print(f"[cyan]Ping: {ping} ms[/cyan]")
            say(f"Download speed: {download_speed:.2f} Mbps, Upload speed: {upload_speed:.2f} Mbps, Ping: {ping} ms")
        
        elif any(phrase in query for phrase in websearch_q):
            web_search(query)

        elif query:
            aura(query)  # Run Aura AI for any other query  

